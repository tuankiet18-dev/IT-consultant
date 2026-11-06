# Live Groq check — 2026-11-06

Synthetic demo, local run 7, model `openai/gpt-oss-120b`. All requests used the same plan. Baseline 32,698, optimised cost 31,316, saving 1,382 (4.2%).

| Attempt | Draft ID | Source | Three complete paragraphs | Reported figures match the supplied facts | Fallback |
| --- | --- | --- | --- | --- | --- |
| 1 | 7 | Groq | Yes | Yes | None |
| 2 | 8 | Groq | Yes | Yes | None |
| 3 | 9 | Groq | Yes | Yes | None |

All three drafts matched the supplied freight and handling changes, reported warehouse moves and route estimates. The drafts still need a planner's edit before approval. All three attributed the moves to Warehouse A being full in the baseline. The facts show that A and B were full in the baseline and that the allocations changed, but do not establish that A's capacity caused the listed moves. The per-pallet route figures are cheapest-supplier estimates, so they should be described as estimates rather than realised savings. Draft 8 also suggested confirming inventory positioning and service-level impacts, which the MVP did not measure.

Live generation and numeric checks passed for these three requests. The semantic review flagged the causal wording in all three. The drafts were left unapproved. Use the offline `demo-guard` check as separate evidence of fallback when a number is unsupported.
