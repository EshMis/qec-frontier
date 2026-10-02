# QEC frontier research protocol

User authorization: pursue the Unitary Foundation QEC Challenge until a new frontier point exists, with full permission to create GitHub repositories, install tools, and use Shirokane. Research artifacts live in this repository. Publication follows the challenge's contributor-driven workflow after validation.

Use qLDPC v0.4.0 for candidate construction. Follow the upstream AGENTS.md for work under `external/qldpc-challenge`. Never modify the trusted upstream `verify/` stack to make a candidate pass. Use its official validator and board frontier logic. Preserve witnesses and failed-candidate evidence. Do not conflate `upper_bound`, `passed` refutation, and exact certification.

All nontrivial CPU workloads run on Shirokane in `~/qec-frontier`, with a dedicated `.venv`. Never install into an existing project's environment. Profile a single task before a sweep; use bounded arrays and per-task atomic outputs. Read scheduler state by numeric job ID, and require terminal accounting plus complete output for finished-run claims.

Parallel lanes own separate scripts and output directories. They must not revert each other's work. Only the lead manages shared contracts, Git, job submission, handoff, and publication unless delegated explicitly.
