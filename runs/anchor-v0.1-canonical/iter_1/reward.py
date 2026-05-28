# ruff: noqa
def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    # ---- Normalize inputs ----------------------------------------------------
    obs = np.asarray(obs, dtype=np.float64).reshape(-1)
    act = np.asarray(action, dtype=np.float64).reshape(-1)
    n = obs.size

    # ---- Resolve world quantities (prefer info dict, fall back to obs slice) -
    # Assumed 24-dim Franka pick-place layout:
    #   [ 0: 7] joint positions
    #   [ 7:14] joint velocities
    #   [14:17] end-effector xyz
    #   [17:20] cube xyz
    #   [20:23] target xyz
    #   [23   ] gripper width
    def _vec(key, fb):
        v = info.get(key) if isinstance(info, dict) else None
        if v is None:
            v = fb
        return np.asarray(v, dtype=np.float64).reshape(-1)

    ee_pos     = _vec('ee_pos',        obs[14:17] if n >= 17 else np.zeros(3))
    cube_pos   = _vec('cube_pos',      obs[17:20] if n >= 20 else np.zeros(3))
    target_pos = _vec('target_pos',    obs[20:23] if n >= 23 else np.zeros(3))
    grip_w     = _vec('gripper_width', obs[23:24] if n >= 24 else np.array([0.04]))
    grip = float(grip_w.flat[0]) if grip_w.size else 0.04

    # ---- Geometric quantities -----------------------------------------------
    d_ee_cube     = float(np.linalg.norm(ee_pos - cube_pos))
    d_cube_target = float(np.linalg.norm(cube_pos - target_pos))
    cube_z        = float(cube_pos[2])

    # ---- Anchor reward (matches the stated signature exactly) ---------------
    success  = (cube_z > 0.5) and (d_cube_target < 0.1)
    r_anchor = -d_cube_target + (1.0 if success else 0.0)

    # ---- Dense shaping ------------------------------------------------------
    # 1. Reach: smooth pull of end-effector toward the cube
    r_reach = float(1.0 - np.tanh(8.0 * d_ee_cube))

    # 2. Grasp: reward closing fingers once the EE is on top of the cube
    r_grasp = 0.0
    if d_ee_cube < 0.05:
        # Franka gripper: ~0.04 m open, ~0.0 m closed
        r_grasp = float(np.clip(1.0 - grip / 0.04, 0.0, 1.0))

    # 3. Lift: bonus for raising the cube above the table
    z_floor = 0.40
    r_lift = float(np.clip((cube_z - z_floor) / 0.20, 0.0, 1.0))

    # 4. Transport: shape toward target only after the cube is lifted
    r_transport = 0.0
    if cube_z > z_floor + 0.02:
        r_transport = float(1.0 - np.tanh(4.0 * d_cube_target))

    # 5. Small action regularizer for smoother trajectories
    r_act = -1e-3 * float(np.dot(act, act)) if act.size else 0.0

    shaping = (
        0.30 * r_reach
        + 0.20 * r_grasp
        + 0.30 * r_lift
        + 0.40 * r_transport
        + r_act
    )

    total = r_anchor + shaping
    if not np.isfinite(total):
        return 0.0
    return float(np.clip(total, -10.0, 10.0))
