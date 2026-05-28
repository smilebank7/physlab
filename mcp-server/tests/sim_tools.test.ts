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

async function callTool(
  server: StartedHttpServer,
  name: string,
  args: Record<string, unknown>,
  id: number,
): Promise<Record<string, unknown>> {
  return rpc(server, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: { name, arguments: args },
    id,
  });
}

afterEach(async () => {
  while (servers.length > 0) {
    await servers.pop()?.close();
  }
});

test("tools/list returns ping and sim tools", async () => {
  const server = await start();
  const response = await rpc(server, {
    jsonrpc: "2.0",
    method: "tools/list",
    id: 1,
  });
  const result = response.result as { tools: Array<{ name: string }> };
  const names = result.tools.map((tool) => tool.name);
  expect(names).toContain("ping");
  expect(names).toContain("sim.make");
  expect(names).toContain("sim.reset");
  expect(names).toContain("sim.step");
  expect(names).toContain("sim.observe");
  expect(names).toContain("task.list");
});

test("task.list includes cartpole and sim step returns observation", async () => {
  const server = await start();
  const list = await callTool(server, "task.list", {}, 2);
  expect((list.result as { tasks: string[] }).tasks).toContain("cartpole");

  const made = await callTool(
    server,
    "sim.make",
    { task: "cartpole", backend: "mujoco", seed: 42 },
    3,
  );
  const handleId = (made.result as { handle_id: string }).handle_id;
  expect(handleId.length).toBeGreaterThan(0);

  const stepped = await callTool(
    server,
    "sim.step",
    { handle_id: handleId, action: [0] },
    4,
  );
  const result = stepped.result as { observation: number[]; reward: number };
  expect(result.observation.length).toBeGreaterThan(0);
  expect(typeof result.reward).toBe("number");
});

test("stale handle returns JSON-RPC -32602", async () => {
  const server = await start();
  const response = await callTool(
    server,
    "sim.step",
    { handle_id: "fake-handle-id", action: [0] },
    5,
  );
  expect(response.error).toMatchObject({ code: -32602 });
});

test("ten concurrent handles are isolated", async () => {
  const server = await start();
  const handles = await Promise.all(
    Array.from({ length: 10 }, (_, index) =>
      callTool(
        server,
        "sim.make",
        { task: "cartpole", backend: "mujoco", seed: index },
        index + 10,
      ),
    ),
  );
  const handleIds = handles.map(
    (response) => (response.result as { handle_id: string }).handle_id,
  );
  expect(new Set(handleIds).size).toBe(10);

  const resets = await Promise.all(
    handleIds.map((handle_id, index) =>
      callTool(server, "sim.reset", { handle_id, seed: index }, index + 30),
    ),
  );
  const observations = resets.map((response) =>
    JSON.stringify((response.result as { observation: number[] }).observation),
  );
  expect(new Set(observations).size).toBeGreaterThan(1);
});
