import Ajv2020 from "ajv/dist/2020";
import { afterEach, expect, test } from "bun:test";
import { type StartedHttpServer, startHttpServer } from "../src/server.ts";

const requiredTools = [
  "ping",
  "sim.make",
  "sim.reset",
  "sim.step",
  "sim.observe",
  "task.list",
];
const servers: StartedHttpServer[] = [];

type Tool = {
  name: string;
  description: string;
  inputSchema: object;
};

async function start(): Promise<StartedHttpServer> {
  const server = await startHttpServer({ host: "127.0.0.1", port: 0 });
  servers.push(server);
  return server;
}

async function rpc(
  server: StartedHttpServer,
  body: unknown,
): Promise<Record<string, unknown>> {
  const response = await fetch(server.url, {
    method: "POST",
    body: JSON.stringify(body),
    headers: { "content-type": "application/json" },
  });
  expect(response.status).toBe(200);
  return (await response.json()) as Record<string, unknown>;
}

afterEach(async () => {
  while (servers.length > 0) {
    await servers.pop()?.close();
  }
});

test("tools/list schemas and descriptions are MCP-client portable", async () => {
  const server = await start();
  const response = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/list",
    id: 1,
  });
  const tools = (response.result as { tools: Tool[] }).tools;
  const names = new Set(tools.map((tool) => tool.name));
  const ajv = new Ajv2020({ strict: true });

  expect(tools.length).toBeGreaterThanOrEqual(6);
  for (const name of requiredTools) {
    expect(names.has(name)).toBe(true);
  }
  for (const tool of tools) {
    expect(tool.description.length).toBeGreaterThanOrEqual(20);
    expect(ajv.validateSchema(tool.inputSchema)).toBe(true);
  }
});

test("TypeScript JSON-RPC client sees spec error codes and tool round-trip", async () => {
  const server = await start();
  const unknown = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/unknown",
    id: 2,
  });
  expect(unknown.error).toMatchObject({ code: -32601 });

  const invalidParams = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name: "ping", arguments: {} },
    id: 3,
  });
  expect(invalidParams.error).toMatchObject({ code: -32602 });

  const ping = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name: "ping", arguments: { msg: "ts-client" } },
    id: 4,
  });
  expect(ping.result).toMatchObject({
    content: [{ type: "text", text: "pong: ts-client" }],
  });
});
