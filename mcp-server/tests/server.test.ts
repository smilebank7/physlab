import { expect, test } from "bun:test";
import { serverName } from "../src/server.ts";

test("serverName returns package name", () => {
  expect(serverName()).toBe("physlab");
});
