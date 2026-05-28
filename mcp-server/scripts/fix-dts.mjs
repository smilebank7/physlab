import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../dist", import.meta.url));

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      await walk(fullPath);
    } else if (entry.isFile() && entry.name.endsWith(".d.ts")) {
      await fixFile(fullPath);
    }
  }
}

async function fixFile(filePath) {
  const original = await readFile(filePath, "utf8");
  const fixed = original
    .replace(/^#![^\n]*\n/, "")
    .replace(/(from\s+["'][^"']+)\.ts(["'])/g, "$1.js$2");
  if (fixed !== original) {
    await writeFile(filePath, fixed);
  }
}

await walk(root);
