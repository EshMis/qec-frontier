# Wider cyclic lifted products

The first profiles verified [[260,58,6]],w6 and [[609,197,6]],w7 using qLDPC 0.4.0, the unchanged official validator, and exact SAT. Scheduler accounting confirms both jobs exited successfully, using at most 1.316 GiB virtual memory within a 4 GiB allocation.

The 63 entries in `lp-all-specs.json` are construction recipes and goals, not measured results. Jobs `wide-v1-a` (indices 1–3) and `wide-v1-b` (5–8) test seven further shapes within the measured profile range. The isolated `wide-v1-max-profile` tests index 46, n=986, before any sweep extends to that size. Each task receives one CPU, 4 GiB memory and a two-hour wall limit. SAT has a 300-second per-side cap; unresolved exact checks remain unverified.

Raw runs retain their exact source snapshots, recipes, screening witnesses, official validation and SAT verdicts. The central registry includes only complete, hash-matched exact results. Rejected targets and missed aspirations remain visible in their screen files.
