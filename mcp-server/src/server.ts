#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import Ajv from "ajv";
import pino from "pino";
import { z } from "zod/v4";
import { createSimToolSet } from "./tools/sim.ts";

type JsonRpcId = string | number | null;

type JsonRpcRequest = {
  jsonrpc: "2.0";
  method: string;
  params?: unknown;
  id?: JsonRpcId;
};

type JsonRpcSuccess = {
  jsonrpc: "2.0";
  id: JsonRpcId;
  result: unknown;
};

type JsonRpcFailure = {
  jsonrpc: "2.0";
  id: JsonRpcId;
  error: {
    code: number;
    message: string;
    data?: unknown;
  };
};

type JsonRpcResponse = JsonRpcSuccess | JsonRpcFailure;

type ToolHandler = (args: unknown) => Promise<unknown> | unknown;

export type ToolDefinition = {
  name: string;
  description: string;
  inputSchema: object;
  handler: ToolHandler;
};

type PingArgs = {
  msg: string;
};

export type StartedHttpServer = {
  port: number;
  url: string;
  close: () => Promise<void>;
};

const logger = pino({ name: "physlab-mcp" });
const ajv = new Ajv({ allErrors: true });

const pingTool: ToolDefinition = {
  name: "ping",
  description: "Return pong with the provided message.",
  inputSchema: {
    type: "object",
    properties: {
      msg: { type: "string" },
    },
    required: ["msg"],
    additionalProperties: false,
  },
  handler: (args: unknown) => {
    const parsed = args as PingArgs;
    return { content: [{ type: "text", text: `pong: ${parsed.msg}` }] };
  },
};

type ToolRegistry = {
  tools: ToolDefinition[];
  close: () => Promise<void>;
};

export class RpcToolError extends Error {
  code: number;

  constructor(code: number, message: string) {
    super(message);
    this.code = code;
  }
}

export function serverName(): string {
  return "physlab";
}

export function createMcpServer(): McpServer {
  const server = new McpServer({ name: serverName(), version: "0.0.0" });
  server.registerTool(
    "ping",
    {
      description: pingTool.description,
      inputSchema: { msg: z.string() },
    },
    ({ msg }: PingArgs) => ({
      content: [{ type: "text", text: `pong: ${msg}` }],
    }),
  );
  return server;
}

export async function handleJsonRpc(
  payload: unknown,
  registry = createToolRegistry(),
): Promise<JsonRpcResponse> {
  const request = parseRequest(payload);
  if (!request.ok) {
    return failure(null, -32600, request.message);
  }
  const id = request.value.id ?? null;

  switch (request.value.method) {
    case "tools/list":
      return success(id, {
        tools: registry.tools.map((tool) => ({
          name: tool.name,
          description: tool.description,
          inputSchema: tool.inputSchema,
        })),
      });
    case "tools/call":
      return callTool(id, request.value.params, registry.tools);
    case "resources/list":
      return success(id, { resources: [] });
    case "resources/read":
      return failure(id, -32601, "resources/read has no registered resources");
    default:
      return failure(id, -32601, `method not found: ${request.value.method}`);
  }
}

export async function startHttpServer(
  options: { host?: string; port?: number } = {},
): Promise<StartedHttpServer> {
  createMcpServer();
  const registry = createToolRegistry();
  const host = options.host ?? "127.0.0.1";
  const port = options.port ?? 8765;
  const server = Bun.serve({
    hostname: host,
    port,
    async fetch(request) {
      const url = new URL(request.url);
      if (request.method === "GET" && url.pathname === "/healthz") {
        return Response.json({ ok: true, name: serverName() });
      }
      if (request.method !== "POST") {
        return Response.json(
          failure(null, -32600, "only POST JSON-RPC requests are supported"),
        );
      }
      let payload: unknown;
      try {
        payload = await request.json();
      } catch {
        return Response.json(failure(null, -32700, "parse error"));
      }
      return Response.json(await handleJsonRpc(payload, registry));
    },
  });
  const actualPort = server.port ?? port;
  logger.info({ host, port: actualPort }, "listening on stdio + http");
  return {
    port: actualPort,
    url: `http://${host}:${actualPort}`,
    close: async () => {
      await registry.close();
      server.stop(true);
    },
  };
}

async function callTool(
  id: JsonRpcId,
  params: unknown,
  tools: ToolDefinition[],
): Promise<JsonRpcResponse> {
  if (!isObject(params) || typeof params.name !== "string") {
    return failure(id, -32602, "tools/call params must include a tool name");
  }
  const tool = tools.find((candidate) => candidate.name === params.name);
  if (tool === undefined) {
    return failure(id, -32601, `tool not found: ${params.name}`);
  }
  const args = isObject(params.arguments) ? params.arguments : {};
  const validate = ajv.compile(tool.inputSchema);
  if (!validate(args)) {
    return failure(id, -32602, "invalid tool arguments", validate.errors ?? []);
  }
  try {
    return success(id, await tool.handler(args));
  } catch (error) {
    if (error instanceof RpcToolError) {
      return failure(id, error.code, error.message);
    }
    return failure(
      id,
      -32603,
      error instanceof Error ? error.message : "tool failed",
    );
  }
}

function createToolRegistry(): ToolRegistry {
  const simTools = createSimToolSet();
  return {
    tools: [pingTool, ...simTools.tools],
    close: () => simTools.close(),
  };
}

function parseRequest(
  payload: unknown,
): { ok: true; value: JsonRpcRequest } | { ok: false; message: string } {
  if (!isObject(payload)) {
    return { ok: false, message: "request must be an object" };
  }
  if (payload.jsonrpc !== "2.0") {
    return { ok: false, message: "jsonrpc must be '2.0'" };
  }
  if (typeof payload.method !== "string") {
    return { ok: false, message: "method must be a string" };
  }
  const id = payload.id;
  if (
    id !== undefined &&
    id !== null &&
    typeof id !== "string" &&
    typeof id !== "number"
  ) {
    return {
      ok: false,
      message: "id must be string, number, null, or omitted",
    };
  }
  return { ok: true, value: payload as JsonRpcRequest };
}

function success(id: JsonRpcId, result: unknown): JsonRpcSuccess {
  return { jsonrpc: "2.0", id, result };
}

function failure(
  id: JsonRpcId,
  code: number,
  message: string,
  data?: unknown,
): JsonRpcFailure {
  return { jsonrpc: "2.0", id, error: { code, message, data } };
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

if (import.meta.main) {
  if (process.argv.includes("--help") || process.argv.includes("-h")) {
    console.log(`physlab-mcp-server

Usage:
  physlab-mcp-server [--host 127.0.0.1] [--port 8765]

Starts the physlab MCP JSON-RPC server with sim.make/reset/step/observe and task.list tools.`);
    process.exit(0);
  }
  await startHttpServer({
    host: process.env.PHYSLAB_MCP_HOST ?? "127.0.0.1",
    port: Number(process.env.PHYSLAB_MCP_PORT ?? "8765"),
  });
  console.log("listening on stdio + http://localhost:8765");
}
