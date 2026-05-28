type JsonRpcResponse = {
  result?: unknown;
  error?: { code: number; message: string };
};

const url = process.env.PHYSLAB_MCP_URL ?? "http://127.0.0.1:8765";

async function rpc(method: string, params: unknown, id: number): Promise<unknown> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", method, params, id }),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const payload = (await response.json()) as JsonRpcResponse;
  if (payload.error) {
    throw new Error(`${payload.error.code}: ${payload.error.message}`);
  }
  return payload.result;
}

async function callTool(name: string, args: Record<string, unknown>, id: number): Promise<unknown> {
  return rpc("tools/call", { name, arguments: args }, id);
}

const seed = Number(process.argv.at(2) ?? "42");
const made = (await callTool("sim.make", { task: "cartpole", backend: "mujoco", seed }, 1)) as {
  handle_id: string;
};
let episodeReward = 0;
let steps = 0;
for (steps = 1; steps <= 500; steps += 1) {
  const stepped = (await callTool(
    "sim.step",
    { handle_id: made.handle_id, action: [0] },
    steps + 1,
  )) as { reward: number; terminated: boolean; truncated: boolean };
  episodeReward += stepped.reward;
  if (stepped.terminated || stepped.truncated) {
    break;
  }
}

console.log(`episode_reward=${episodeReward.toFixed(3)} steps=${steps}`);
