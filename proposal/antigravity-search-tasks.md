# Search tasks for Antigravity (copy everything below the line into Antigravity)

---

You are helping a student team finish a consulting proposal due **22:00 Vietnam time, 26 Oct 2026**. The proposal is "Nordic Flow": optimise goods allocation (supplier → existing warehouse → customer zone, LP/MILP) for "Company A", a Danish building-materials retailer in DK/NO/SE. Sweden-first pilot, 3 warehouses, planner approves every plan.

**Rules (important):**
- Open each source page or PDF yourself and read it. Do NOT rely on search-result snippets.
- For every item return: exact figure, what exactly was measured, year, sample/scope, direct URL, page or section, and a short exact quote (under 15 words). If you cannot open it or the figure is not there, write `NOT VERIFIED` and say why.
- Never invent or "round to make it fit". If a figure differs from what we expect, report the real one.
- Mark each source as `independent` (academic, government, audited annual report) or `vendor/consultancy`.
- Return one table per section, in English, in Markdown.

## A. Must-do (these go on slides; highest priority)

1. **Logistics share of cost for a Nordic building-materials merchant.** Open annual reports (2024 or 2025) of Byggmax, Beijer Byggmaterial, Stark Group, Bauhaus, or Silvan. Find: transport/distribution/logistics cost as a share of net sales or of cost of goods; number of distribution centres/warehouses; any statement about delivery from DC vs direct from supplier ("direktleverans"). This sets the "relevant logistics cost" base in our break-even model.
2. **Byggmax Annual Report 2025, page 7.** Our slide 3 cites it for "logistics restructuring to improve flow control, planning and delivery efficiency". Confirm the exact wording and page. Also net sales and EBITA margin 2025 (we have SEK 6,133M and 5.9% from the year-end report; confirm).
3. **Network/allocation optimisation results, independent evidence.** Find peer-reviewed or audited results (not marketing) quantifying the cost reduction from optimising multi-warehouse allocation or order routing: journals such as Management Science, Operations Research, Interfaces (INFORMS Edelman Award papers are good), EJOR, IJPE. Report % cost saving, baseline definition, and industry. Prefer retail, wholesale or building materials.
4. **McKinsey tire-distributor case ("10–15% logistics cost saving, 150+ warehouses")** and **Miebach case (12% projected saving, 41 EMEA + 29 North American sites)**: open the pages, confirm the figures, and state whether they are achieved or projected.
5. **DeHoratius & Raman (2008), Management Science 54(4):627–641.** Confirm: share of inaccurate inventory records, number of stores and records, and the profit effect. Also confirm the Chicago Booth Review summary says "more than 10%" and what it refers to.

## B. Should-do (supports prioritisation, slide 2)

6. Evidence that **order-processing/manual work** in Nordic building-materials is smaller or larger than assumed: Eurostat "enterprises receiving orders via EDI/web" for DK, NO, SE (dataset isoc_ec_esells or similar); Digitaliseringsstyrelsen/Digdir B2B e-invoicing share. Report exact values and year.
7. Evidence on **direct-from-supplier delivery share** for heavy building materials (Nordic or UK): any figure from annual reports, trade bodies (Byggmaterialhandlarna, Builders Merchants Federation).
8. **Sweden as pilot market:** Byggföretagen or Konjunkturinstitutet forecast for building investment 2026–27 (we have "+4% per year" via TV4/TT; confirm from the primary source).

## C. Nice-to-have (only if time allows)

9. Any public Netcompany case study or whitepaper on supply-chain optimisation, planning, or AI in logistics (for tone and credibility).
10. EU AI Act: confirm that decision-support optimisation of goods allocation (no profiling of people) is not "high-risk". Quote the relevant Annex III text.
11. OR-Tools: confirm that MPSolver/CP-SAT supports LP, MILP and min-cost flow, and the licence (Apache 2.0).

## Output format

For each numbered item:

| # | Claim we want to use | Verified figure | Measured what / scope / year | Independent? | URL + page/section | Status (VERIFIED / PARTIAL / NOT VERIFIED) |

End with a list of **claims that should be dropped** because they could not be confirmed, and a list of **surprises** where the real figure differs from our expectation.
