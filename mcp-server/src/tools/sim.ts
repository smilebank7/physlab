import schemas from "../generated/schemas.json";
import { RpcToolError, type ToolDefinition } from "../server.ts";
import { PythonWorker, WorkerError } from "../worker.ts";

type SimToolName = keyof typeof schemas;

export function createSimToolSet(): {
  tools: ToolDefinition[];
  close: () => Promise<void>;
} {
  const worker = new PythonWorker();
  const tools: ToolDefinition[] = [
    workerTool(worker, "sim.make", "Create a task environment handle."),
    workerTool(worker, "sim.reset", "Reset an environment handle."),
    workerTool(
      worker,
      "sim.step",
      "Advance an environment handle by one action.",
    ),
    workerTool(
      worker,
      "sim.observe",
      "Read the latest observation without advancing.",
    ),
    workerTool(worker, "task.list", "List registered physlab tasks."),
  ];
  return { tools, close: () => worker.close() };
}

function workerTool(
  worker: PythonWorker,
  name: SimToolName,
  description: string,
): ToolDefinition {
  return {
    name,
    description,
    inputSchema: schemas[name],
    handler: async (args: unknown) => {
      try {
        return await worker.request(name, args as Record<string, unknown>);
      } catch (error) {
        if (error instanceof WorkerError) {
          throw new RpcToolError(error.code, error.message);
        }
        throw error;
      }
    },
  };
}
