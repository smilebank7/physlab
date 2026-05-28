import { type ChildProcessWithoutNullStreams, spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

type WorkerResponse =
  | { id: number; ok: true; result: unknown }
  | { id: number; ok: false; code: number; message: string };

type PendingRequest = {
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
};

export class WorkerError extends Error {
  code: number;

  constructor(code: number, message: string) {
    super(message);
    this.code = code;
  }
}

export class PythonWorker {
  private process: ChildProcessWithoutNullStreams | null = null;
  private nextId = 1;
  private pending = new Map<number, PendingRequest>();
  private stdoutBuffer = "";
  private stderrBuffer = "";
  private readonly repoRoot: string;

  constructor(repoRoot = resolveRepoRoot()) {
    this.repoRoot = repoRoot;
  }

  async request(
    command: string,
    args: Record<string, unknown>,
  ): Promise<unknown> {
    const child = this.ensureProcess();
    const id = this.nextId;
    this.nextId += 1;
    const payload = JSON.stringify({ id, command, args });
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      child.stdin.write(`${payload}\n`);
    });
  }

  async close(): Promise<void> {
    if (this.process === null) {
      return;
    }
    const child = this.process;
    this.process = null;
    child.kill();
    for (const pending of this.pending.values()) {
      pending.reject(new WorkerError(-32603, "python worker closed"));
    }
    this.pending.clear();
  }

  private ensureProcess(): ChildProcessWithoutNullStreams {
    if (this.process !== null) {
      return this.process;
    }
    const python = pythonExecutable(this.repoRoot);
    const child = spawn(python, ["-m", "physlab.mcp_worker"], {
      cwd: this.repoRoot,
      env: {
        ...process.env,
        PYTHONPATH: [path.join(this.repoRoot, "src"), process.env.PYTHONPATH]
          .filter(Boolean)
          .join(path.delimiter),
        PYTHONUNBUFFERED: "1",
      },
    });
    child.stdout.on("data", (chunk: Buffer) =>
      this.onStdout(chunk.toString("utf8")),
    );
    child.stderr.on("data", (chunk: Buffer) => {
      this.stderrBuffer = `${this.stderrBuffer}${chunk.toString("utf8")}`.slice(
        -4000,
      );
    });
    child.on("exit", () => {
      this.process = null;
      for (const pending of this.pending.values()) {
        pending.reject(
          new WorkerError(-32603, this.stderrBuffer || "python worker exited"),
        );
      }
      this.pending.clear();
    });
    this.process = child;
    return child;
  }

  private onStdout(chunk: string): void {
    this.stdoutBuffer += chunk;
    while (this.stdoutBuffer.includes("\n")) {
      const index = this.stdoutBuffer.indexOf("\n");
      const line = this.stdoutBuffer.slice(0, index);
      this.stdoutBuffer = this.stdoutBuffer.slice(index + 1);
      if (line.trim().length > 0) {
        this.handleLine(line);
      }
    }
  }

  private handleLine(line: string): void {
    const response = JSON.parse(line) as WorkerResponse;
    const pending = this.pending.get(response.id);
    if (pending === undefined) {
      return;
    }
    this.pending.delete(response.id);
    if (response.ok) {
      pending.resolve(response.result);
    } else {
      pending.reject(new WorkerError(response.code, response.message));
    }
  }
}

function resolveRepoRoot(): string {
  const cwd = process.cwd();
  return path.basename(cwd) === "mcp-server" ? path.dirname(cwd) : cwd;
}

function pythonExecutable(repoRoot: string): string {
  const venvPython = path.join(repoRoot, ".venv", "bin", "python");
  return existsSync(venvPython) ? venvPython : "python3";
}
