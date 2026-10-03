# Active improvement search

The owner requested continuous active search and a clear summary of each verified
point. The four-hour follow-up was deleted at the owner's request. Search continues
in this chat; there is no scheduled Codex automation.

This bounded wave has eight LP and eight bicycle specifications, stored before
submission in the adjacent JSON files. They are targets, not measured discoveries.
The LP lane tests proper seed subgroups to increase capacity or reduce block size,
then nonabelian lifts for stronger distance. The bicycle lane tests smaller blocks,
higher distance at the known block size, and asymmetric higher-rate constructions.

Every candidate is constructed with qLDPC 0.4.0. The search compares against the
pinned official board and all locally exact-certified discoveries. It then uses
300, 5,000 and 50,000 accelerated screening trials, the unchanged official validator,
and exact SAT certification with a 300-second cap per side. Unresolved certificates
are retained as candidates and are not reported as confirmed frontier points.
Within a worker, each newly certified point raises the bar for later candidates.

Each worker has one CPU slot, 4 GB of memory and a two-hour wall-time cap. The largest
LP profile (468 qubits) took 61.18 seconds for screening and used 1.025 GB maximum
virtual memory. Eight such screening pipelines project to 489.44 seconds; even eight
full two-sided SAT timeouts add only 4,800 seconds, leaving headroom below the cap.
The prior bicycle pilot already covered this wave's matrix size; its confirmed
312-qubit point certified both sides in 16 seconds total.

Numeric job IDs and specification hashes are in [JOBS.json](JOBS.json). Each worker
preserves its exact generator and driver source alongside RUN.json and writes
DISCOVERIES.json immediately after each successful exact certificate. The lead
checks the evidence, consolidates dominance relationships and explains each point
in [FRONTIER.md](../../FRONTIER.md) and in chat.
