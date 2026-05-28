# ruff: noqa
def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    # Safely fetch 3-vectors; prefer info dict, fall back to obs slicing.
    info = info if isinstance(info, dict) else {}
    obs = np.asarray(obs, dtype=np.float64).reshape(-1)

    def _v3(key, start):
        v = info.get(key)
        if v is not None:
            a = np.asarray(v, dtype=np.float64).reshape(-1)
            if a.size >= 3:
                return a[:3]
        if obs.size >= start + 3:
            return obs[start:start + 3]
        return np.zeros(3, dtype=np.float64)

    # Assumed 24-D obs layout: q[0:7] qd[7:14] ee[14:17] cube[17:20] target[20:23] grip[23]
    ee_pos     = _v3('ee_pos',     14)
    cube_pos   = _v3('cube_pos',   17)
    target_pos = _v3('target_pos', 20)

    # Key geometry
    d_ct   = float(np.linalg.norm(cube_pos - target_pos))   # cube -> target
    d_ec   = float(np.linalg.norm(ee_pos   - cube_pos))     # ee   -> cube
    cube_z = float(cube_pos[2])

    # Spec'd base reward: -distance(cube, target) + 1_success
    success = (cube_z > 0.5) and (d_ct < 0.1)
    r = -d_ct + (1.0 if success else 0.0)

    # Dense shaping (stage decomposition: reach -> grasp -> lift -> transport)
    # 1) Reach: encourage end-effector toward cube
    r += 0.30 * (1.0 - np.tanh(10.0 * d_ec))

    # 2) Smooth grasp gate (~1 when ee is at the cube)
    grasp_gate = float(np.exp(-50.0 * d_ec * d_ec))

    # 3) Lift: reward cube height, gated by ee-at-cube
    lift_progress = float(np.clip(cube_z / 0.5, 0.0, 1.0))
    r += 0.30 * grasp_gate * lift_progress

    # 4) Transport: smooth proximity-to-target signal (denser than raw -d)
    r += 0.40 * (1.0 - np.tanh(5.0 * d_ct))

    # 5) Tiny action regularization (anti-jitter, won't dominate)
    r -= 5e-4 * float(np.dot(action, action))

    if not np.isfinite(r):
        return -10.0
    return float(r)
