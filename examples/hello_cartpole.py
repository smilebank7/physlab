from __future__ import annotations

import argparse

import numpy as np

from physlab import make


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="explicit no-GUI mode")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    env = make("cartpole", "mujoco", seed=args.seed)
    episode_reward = 0.0
    steps = 0
    try:
        env.reset(seed=args.seed)
        for step in range(1, 501):
            steps = step
            _, reward, terminated, truncated, _ = env.step(env.action_space.sample(rng))
            episode_reward += reward
            if terminated or truncated:
                break
    finally:
        env.close()
    print(f"episode_reward={episode_reward:.3f} steps={steps}")


if __name__ == "__main__":
    main()
