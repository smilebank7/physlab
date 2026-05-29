# Roadmap

physlab v0.1 is intentionally narrow: MuJoCo simulation, MCP tools, three
built-in tasks, and one local reward-iteration anchor demo.

## v0.2 Milestones

- v0.2 IsaacLab compatibility research: evaluate one concrete task conversion
  only after IsaacLab internals fluency improves. This is not a v0.1 feature and
  is not a general compatibility promise.
- Plug-in machinery: consider discovery, lifecycle, and sandboxing after the
  v0.1 explicit-registration extension points have real user feedback.
- Drake or Taichi experiments: evaluate as research backends without changing
  the v0.1 MuJoCo contract.
- Richer task packaging: make third-party tasks easier to distribute while
  preserving the explicit registration model until a plug-in spec is approved.

## v0.3 Candidates

- VLA integration research behind a separate policy-serving boundary.
- Full USD asset workflow research.
- Multi-LLM adapter research outside the v0.1 opencode canonical path.
- Larger-scale training experiments with measured hardware claims.

All roadmap items are deferred research, not current capabilities.

## What About IsaacLab?

physlab v0.1 does not ship IsaacLab compatibility. Phase 0 recorded IsaacLab
internals fluency as 0, and the project scope rule drops the compatibility case
study rather than making an unmeasured parity claim. A future v0.2 investigation
must start with one concrete task conversion, explicit divergence notes, and
measured output before any broader compatibility language is considered.
