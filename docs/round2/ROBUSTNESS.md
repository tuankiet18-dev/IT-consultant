# Synthetic robustness results

Run from `mvp` with `python -m nordic_flow robustness --out ../docs/round2/ROBUSTNESS.md`.

MILP with a 30-second solver limit per case. Size is SKU count x zone count.

| Seed | Size | Baseline valid | Saving | Solver status | Solve seconds | Independent check passed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 20 x 6 | Yes | 1.78% | OPTIMAL | 0.011 | Yes |
| 2 | 20 x 6 | Yes | 2.02% | OPTIMAL | 0.004 | Yes |
| 3 | 20 x 6 | Yes | 3.40% | OPTIMAL | 0.006 | Yes |
| 4 | 20 x 6 | Yes | 2.04% | OPTIMAL | 0.005 | Yes |
| 5 | 20 x 6 | Yes | 1.75% | OPTIMAL | 0.007 | Yes |
| 6 | 20 x 6 | Yes | 2.86% | OPTIMAL | 0.007 | Yes |
| 7 | 20 x 6 | Yes | 4.23% | OPTIMAL | 0.005 | Yes |
| 8 | 20 x 6 | Yes | 2.21% | OPTIMAL | 0.009 | Yes |
| 9 | 20 x 6 | Yes | 3.12% | OPTIMAL | 0.005 | Yes |
| 10 | 20 x 6 | Yes | 3.12% | OPTIMAL | 0.005 | Yes |
| 1 | 100 x 12 | Yes | 4.97% | OPTIMAL | 0.064 | Yes |

- Saving min / median / max across 11 comparable cases: 1.75% / 2.86% / 4.97%
- Invalid baselines: 0. Verified plans: 11/11.
- Longest solve: 0.064 s.

All data is synthetic. Savings reflect the generated inputs and cannot forecast Company A's results.
