import { afterEach, expect, test } from "bun:test";
import { type StartedHttpServer, startHttpServer } from "../src/server.ts";

const servers: StartedHttpServer[] = [];

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

test("server starts and tools/list returns ping", async () => {
  const server = await start();
  const result = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/list",
    id: 1,
  });
  expect(result.jsonrpc).toBe("2.0");
  expect(result.id).toBe(1);
  const tools = (result.result as { tools: Array<{ name: string }> }).tools;
  expect(tools[0]?.name).toBe("ping");
});

test("tools/call ping returns pong with echo arg", async () => {
  const server = await start();
  const result = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name: "ping", arguments: { msg: "hi" } },
    id: 2,
  });
  expect(result).toMatchObject({
    jsonrpc: "2.0",
    id: 2,
    result: { content: [{ type: "text", text: "pong: hi" }] },
  });
});

test("invalid tool name returns JSON-RPC -32601", async () => {
  const server = await start();
  const result = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name: "nope", arguments: {} },
    id: 3,
  });
  expect(result.error).toMatchObject({ code: -32601 });
});

test("schema validation returns JSON-RPC -32602", async () => {
  const server = await start();
  const result = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name: "ping", arguments: {} },
    id: 4,
  });
  expect(result.error).toMatchObject({ code: -32602 });
});
