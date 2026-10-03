# Session stopping point — 2026-10-02

The user asked to finish once the current work reached a neat stopping point.
Both research agents have completed, all submitted QEC jobs have left the
scheduler, and no further search wave was launched after that request. The
`finish-qec-frontier-submission` heartbeat was deleted earlier at the user's
request. Do not create a replacement or resume automatically.

## Verified results

53 exact-certified discoveries; 50 remain nondominated after including our
own improvements. All 53 evidence chains passed the final audit against the
1,680 CSS entries at upstream revision
`c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23`. The unchanged 34-file validation
closure also passed its integrity check.

Read [FRONTIER.md](FRONTIER.md) for each point's plain-English gain and
tradeoff, and [the registry](evidence/frontier-points.json) for evidence paths.
The [final audit](evidence/final-audit.json) records the exact candidate hashes.
The solver establishes global distance d. A heavier stored witness on one
side does not establish that side's exact distance.

## Public submissions

- [PR 2674](https://github.com/unitaryfoundation/qldpc-challenge/pull/2674):
  [[416,39,6]], w=5; head `54993e4442a02ac72d449f7eb1664f8688864110`.
  Replaces our initial 455-qubit submission, saving 39 physical qubits.
- [PR 2675](https://github.com/unitaryfoundation/qldpc-challenge/pull/2675):
  [[260,58,6]], w=6; head `ebe1a096267b2459be55ba8caf05702f674afa1d`.
  Saves 24 physical qubits versus the board's [[284,58,6]] entry at equal k,d,w.

Both final JSON documents reproduced both matrices exactly and passed fresh
trusted verification plus the full 8,000,000-trial accelerated gate. Their
publication jobs have terminal failed=0 and exit=0 accounting. Both PRs
contain exactly one code and one note and passed the clean-commit prose gate.
Upstream workflows report `action_required`; no merge, leaderboard acceptance
or maintainer-confirmed exact badge is claimed. See
[submissions.json](evidence/submissions.json).

The original 455-qubit result and its complete evidence remain in Git and
the research tree. `submission/609-197-6.json` is prepared metadata only;
its final-publication reconstruction and deep gate have not been run and no
PR was created for it.

## If the user resumes

1. Refresh upstream main and both PR states first. Read the local registry
   before deciding what still advances the frontier. Do not rerun old output
   names; the driver intentionally refuses to overwrite existing evidence.
2. The wide catalog tested slots 0..24 and 46. Slots 25..45 are unrun. Slots 47..62
   are secondary, sometimes dominated goals; apply the current frontier
   before spending on them. Maximum profiled n=986 used 1.355 GiB virtual memory
   within one CPU/4 GiB and completed exact verification in 405.5 seconds.
3. `rectangular_refinements(20261002,2)` prepares unrun d=6 goals 224/33/w6 and
   256/39/w6. Original rectangular slots 5/6 instead proved d=5; their missed
   aspirations are preserved honestly. The refinements avoid the identified
   mixed-sector weight-five logical.
4. BB's `paired_strip_bounds` has a recorded m=16 profile but independent
   non-stabilizer replay is still pending. No candidate was rejected using
   that result. The strategy note contains a separate untested Z15×Z15
   3+3 recipe with predicted n=450,k=20,w=6 and a d>=11 goal. It has no measured
   qLDPC rank or distance. See [BB_STRATEGY.md](docs/BB_STRATEGY.md).

Shirokane work remains isolated in `/home/em_shiro/qec-frontier` with qLDPC
0.4.0. Nontrivial numerical work belongs in bounded scheduler jobs, never
on the Mac or login node. Preflight each submission with `qsub -w v`, retain
atomic evidence, and check numeric job IDs plus terminal accounting.
