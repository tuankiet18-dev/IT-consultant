# Allocation vs inventory-accuracy: evidence check (round 1)

## IMPORTANT LIMITATION
WebFetch/curl to all target hosts was DENIED by the egress proxy (403/ENOTFOUND: arxiv, chicagobooth, cmr.berkeley, repec, auburn, cision, internetretailing, ec.europa.eu, liu.se...). NO page was opened.
Everything below is from WebSearch result summaries only = "search-snippet, not opened". Treat all as UNVERIFIED until opened by a human.

## Q1 Inventory record accuracy
- DeHoratius & Raman (2008), Management Science 54(4):627-641, "Inventory Record Inaccuracy: An Empirical Analysis". ~370,000 records, 37 stores, ONE US retailer: 65% inaccurate. 26.4% of variance between categories, 2.7% between stores. Academic/independent. URL: https://ideas.repec.org/a/inm/ormnsc/v54y2008i4p627-641.html (not opened; snippet). "Reduced profits >10%" claim is from Chicago Booth Review summary of related "Execution" paper (https://www.chicagobooth.edu/review/first-measure-then-manage) - snippet only.
- Literature range 20-70% inaccurate records, per arXiv 2506.05357 (https://arxiv.org/pdf/2506.05357) - snippet only.
- Auburn RFID Lab / IHL: URL surfaced (rfid.auburn.edu ITRI-WP154) but no figure retrieved. Unverified.
- Building materials/DIY-specific: NOTHING found. Link inaccuracy -> failed/partial order fulfilment: no source found (only Locus blog citing pick-failure in ship-from-store, paper unopened).
- Caveat: 65% = record-level mismatch of any size, not share of orders failed.

## Q2 Order routing outcomes
- No independent measured cost-per-order / split-shipment result found. Results were vendor/practitioner (Grid Dynamics, Fluent Commerce, Racklify, HotWax): illustrative scenarios, not measurements.
- Kingfisher (via internetretailing.net trade press, snippet): FY to Jan 2021 92% of online orders picked in store; click & collect 90% of online orders; FY21/22 91%. No cost per order. Store-pick model => fulfilment source largely decided already; relies on store stock accuracy. Not heavy/bulky site delivery.
- No evidence applies to bulky site-delivered materials.

## Q3/Q4 Nordic structure and cost
- Stark (trade press/company site, snippet): new Stockholm DC gives next-day delivery to 114 of 116 branches (2023/24); sales EUR 7.8bn, EBITDA EUR 372m. https://starkgroup.dk/newsroom/latest-news/stark-group-increases-net-sales-103-challenging-year . Suggests central DC + branch model. No logistics % or direct-delivery split.
- Byggmax 2024: sales SEK 5,986m, EBITA margin 3.9% (company release, cision, snippet). "Logistics ~10% of revenue" appears only on a vendor template site - UNRELIABLE, do not use.
- BMF/Eurostat logistics % of revenue: nothing found.
- Beijer, Bauhaus, Silvan, Jem&Fix, XL-Bygg: not found.

## Q5 Steelman / critique (reasoning, not sourced)
Allocation first when: many overlapping stock nodes, high split rate, verified stock data, e-com/cross-node orders material.
Not first when: stock data unreliable (optimiser routes to phantom stock; garbage in), most B2B orders are single-node/direktleverans from supplier (little choice), tight time to market, 3 countries with different ERPs. Delivery-reliability/visibility (promise date, tracking, proactive notice) is data-light, customer-facing, fast to ship. Hybrid: accuracy + availability-to-promise as the foundation, routing as phase 2.

## Next steps
Open sources manually (or from an unrestricted host): DeHoratius & Raman, Stark/Byggmax/Beijer annual reports (cost by function note), Kingfisher AR, Eurostat/BMF.
