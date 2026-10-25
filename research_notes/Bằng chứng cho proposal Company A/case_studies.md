# Case studies: builders merchants and home-improvement retailers digitalising delivery, store ops and multi-country systems

Scope note: about 20 tool calls. Primary/trade-press sources were preferred. Vendor case studies and secondary aggregators are flagged **[VENDOR]** or **[SECONDARY]**. Several Nordic players (Beijer, XL-BYGG, Bauhaus, Bygma, Optimera, Kesko) and Netcompany's own retail cases could NOT be verified in this pass. See the Gaps sections.

## 1. Delivery/fulfilment digitalisation: what did merchants build and what improved?

### Takeaway
The best-documented moves are (a) customer-facing delivery visibility on top of an existing ePOD/telematics layer (Travis Perkins, UK) and (b) taking heavy Pro/B2B orders out of stores and into dedicated delivery hubs (Home Depot flatbed DCs). Both are incremental: they sit on top of existing ERPs rather than replacing them. Public sources rarely give hard KPI outcomes such as OTIF or NPS deltas. Most published claims describe capabilities, not measured results.

### Cited Findings
**Travis Perkins (UK, ~550 branches)**
- 24 Feb 2022: Travis Perkins launched nationwide real-time delivery tracking for all account customers. It called itself the first national UK builders merchant to do so. Features: text notification on delivery day with a named 2-hour timeslot, live tracking, an alert when the driver is about 20 minutes away, an emailed proof of delivery, delivery day of choice, next-day delivery, and free delivery from the local branch. It covers 550+ branches and was extended to group businesses Keyline and CCF — [Builders Merchants News](https://www.buildersmerchantsnews.co.uk/news/merchants/travis-perkins-launches-industry-national-delivery-tracking-service)
- Rationale quote from James How, Digital Operations Director: "For our customers, time is money" — [Builders Merchants News](https://www.buildersmerchantsnews.co.uk/news/merchants/travis-perkins-launches-industry-national-delivery-tracking-service)
- Foundation layer: in 2015 Travis Perkins rolled out Microlise electronic proof of delivery (ePOD) "to track customer promises". So tracking came roughly 7 years after the ePOD data foundation — [Microlise press release **[VENDOR]**](https://www.microlise.com/news/travis-perkins-deploys-microlise-electronic-proof-of-delivery-solution-to-track-customer-promises/); [Fleet News](https://www.fleetnews.co.uk/news/latest-news/2015/10/16/travis-perkins-introduces-electronic-proof-of-delivery)
- Travis Perkins launched a customer mobile app in 2021, "designed in conjunction with customers", for real-time ordering and checking stock on the go — [Electrical Contracting News](https://electricalcontractingnews.com/news/travis-perkins-delivery-tracking/)

**Home Depot (US): Pro delivery network**
- Pros (remodelers, builders, MRO) are about 4% of customers but about 45% of annual sales. This is the economic case for a dedicated Pro fulfilment investment — [AJOT](https://www.ajot.com/news/home-depot-is-spending-big-to-keep-lucrative-contractors-happy) (via search summary); [Manufacturing.net](https://www.manufacturing.net/supply-chain/news/21113026/home-depot-opens-first-drivethrough-distribution-center)
- Flatbed distribution centres (FDCs): the first was an 800,000 sq ft drive-through facility in Dallas. Trucks are loaded with lumber, pipe and roofing from both sides. It handles 65–75 trucks per day and "thousands of flatbed deliveries per week" within a 75-mile radius. The plan was 40 FDCs in the 40 largest US markets, for same-day or next-day Pro delivery — [Manufacturing.net](https://www.manufacturing.net/supply-chain/news/21113026/home-depot-opens-first-drivethrough-distribution-center); [JLC Online](https://www.jlconline.com/business/home-depot-launches-pro-customer-delivery-center-in-dallas_o/)
- Phased rollout: Westminster, MA was the 18th FDC in the network. This shows a multi-year, market-by-market rollout rather than a big bang — [Home Depot corporate](https://corporate.homedepot.com/newsroom/home-depot-opens-three-distribution-centers) (via search summary)
- 2024 rationale (Senior EVP Ann-Marie Campbell): "Not shipping from stores helps reduce the amount of time associates have to spend picking, packing and staging items." In Q4 2023 nearly half of online orders were still fulfilled by stores. By end-2024, 17 top Pro markets were to get new fulfilment options, localised assortment, expanded sales teams and digital capabilities including trade credit and order management — [Supply Chain Dive](https://www.supplychaindive.com/news/home-depot-distribution-centers-fulfill-pro-orders/709402/); [Retail Dive](https://www.retaildive.com/news/home-depot-distribution-centers-fulfill-pro-orders/709556)

**Kingfisher / Screwfix (UK): click & collect**
- Screwfix promotes collection "in as little as five minutes". Click & collect is just over half of Screwfix.com orders and about 70% of mobile-site orders. One reported period had click & collect sales +21%, digital +18% and mobile +43% — [The Retail Bulletin interview (2018)](https://theretailbulletin.com/interviews/interview-screwfix-placing-stores-at-heart-of-its-digital-model-25-09-2018); [Builders Merchants News](https://www.buildersmerchantsnews.co.uk/news/news-archive/store-digital-growth-drives-screwfix-sucess); [InternetRetailing](https://internetretailing.net/?p=33163) (figures via search summaries. They are 2018–2019 era, so older than the preferred window.)

**Nordic: Byggmax and Optimera**
- Byggmax (SE/NO/FI) deployed Zimply AI assistants for two automated flows, purchasing and delivery management. The claim is "more than 50 work hours daily" freed — [Zimply press release on Mynewsdesk **[VENDOR]**](https://www.mynewsdesk.com/se/zimply/tag/byggmax) (seen in search snippet only. The full page fetch failed, so treat as unverified.)

### Inferences
- The Travis Perkins sequence (ePOD 2015, customer app 2021, real-time tracking 2022) supports a "data foundation first, customer feature second" roadmap. Company A could ship a "track my delivery" MVP quickly if driver/ePOD data already exists in one country.
- Home Depot's main lesson for Company A is to separate B2B/Pro heavy-goods fulfilment from store picking. This frees store staff time and improves in-store availability. Home Depot rolled it out market by market (18 of 40 planned FDCs at the time of the source).
- Being "first in sector" (Travis Perkins 2022) suggests delivery visibility was still a differentiator in builders' merchanting as recently as 2022.

### Gaps
- No published OTIF, NPS or cost-per-drop outcome numbers were found for Travis Perkins tracking or Home Depot FDCs.
- Not researched in this pass, or nothing verifiable found: Jewson, Ferguson, Lowe's Pro fulfilment, STARK Group delivery apps, Beijer Byggmaterial, XL-BYGG, Bauhaus, Bygma, Saint-Gobain, Würth.
- Optimera (NO/SE) reportedly launched a pro app with in-store scanning, live stock and prices, and order tracking. The source behind the search snippet was not identifiable, so this is not cited.

## 2. Store operations standardisation: task management, store apps, handheld picking

### Takeaway
Home Depot's Sidekick is the clearest benchmark. Home Depot built it in-house on top of a standard handheld fleet, piloted it in about 600 stores, then rolled it out to all US stores by end-2022. Its design principle was "no user training required". Public quantified outcomes, such as hours saved, are not disclosed.

### Cited Findings
- Sidekick is an in-house app on "hdPhones" (Zebra devices; 99,000+ issued to associates). It uses a cloud ML algorithm to prioritise actionable tasks and computer vision to detect out-of-stock shelves and locate products. It has associate and manager dashboard views — [Retail Dive](https://www.retaildive.com/news/home-depot-sidekick-app/641040/); [CIO Dive](https://www.ciodive.com/news/home-depot-sidekick-app/640521/)
- Rollout: live in about 600 stores at announcement, with all US stores to follow. It was built by internal engineers, designers and product managers for faster feedback loops, and designed for "no user training required" — [Retail Dive](https://www.retaildive.com/news/home-depot-sidekick-app/641040/)
- Rollout was completed in all US stores by the end of 2022. It was later extended with "Pipeline Management", a consolidated view of a customer's kitchen-design project activity for associates serving pros — [Customer Experience Dive](https://www.customerexperiencedive.com/news/home-depot-associates-professional-customers-sidekick/724136/); [Home Depot corporate](https://corporate.homedepot.com/news/company/home-depot-launches-new-store-application-help-associates-provide-better-customer)
- Home Depot's FDC strategy is explicitly framed as freeing store associates' time from picking, packing and staging (see Q1) — [Supply Chain Dive](https://www.supplychaindive.com/news/home-depot-distribution-centers-fulfill-pro-orders/709402/)

### Inferences
- The pattern is to standardise the device and data layer first (one handheld fleet), then ship a single task-prioritisation app with a pilot cohort before a chain-wide rollout. This maps well to a Company A "one store app across DK/NO/SE" MVP that pilots in a subset of stores.
- "No training required" is a useful design target for Nordic store staff and for change management.

### Gaps
- No quantified Sidekick outcomes (hours saved, OOS reduction %) were found in public sources.
- Not covered or not found: Kingfisher store colleague apps, Lowe's associate devices (Lowe's reportedly rolled out ~100k+ smartphones circa 2018–2020, not verified here), and Kesko/K-Rauta store apps.

## 3. Multi-country system harmonisation: big-bang ERP vs incremental approaches

### Takeaway
The evidence strongly favours caution on big-bang, heavily customised ERP harmonisation. Lidl wrote off about €500m after 7 years. Kingfisher's group-wide SAP "unified IT platform" coincided with severe disruption at Castorama France: sales -7.3%, retail profit -35%, and stock/logistics inefficiencies costing about 80 bps of gross margin. Kingfisher later refused SAP's S/4HANA roadmap and chose a third-party-maintained ECC on Google Cloud. STARK Group (Company A's closest peer) still runs its Danish ERP Aspect 4 and reports large ongoing transformation costs.

### Cited Findings
**Kingfisher (UK/FR/PL etc.): "ONE Kingfisher" unified SAP platform**
- The programme was announced 2014/15 as a four-year group-wide standard SAP implementation (B&Q, Screwfix, Castorama France), with concurrent refresh of servers, tills and devices. Process mapping was done at Castorama France in 2013/14. IT capex was £117m in 2013/14 (32% of capex), with £140–160m planned for 2014/15 (40% of capex) — [Insight DIY](https://www.insightdiy.co.uk/news/kingfisher-to-commence-sap-implementation-programme-this-year/3065.htm)
- FY18/19 results (March 2019): "The rollout of our unified IT platform is substantially complete". The same year Castorama sales fell 7.3% (LFL -7.1%) to £2,246m and France retail profit fell 35.2% to £209m. Gross margin was hit about 80 bps by "logistics and stock inefficiencies" alongside "transformation-related activity", and national demonstrations cost about 3% of Q4 LFL — [Insight DIY: "Castorama is now Kingfisher's biggest problem"](https://insightdiy.co.uk/news/castorama-is-now-kingfishers-biggest-problem/7039.htm); [Kingfisher RNS, 20 Mar 2019](https://data.fca.org.uk/artefacts/NSM/data-migration/LSE20190320070005_14008283.html)
- Caveat: Kingfisher attributed the Castorama decline to multiple factors (footfall, price repositioning, protests, transformation). Sources do not isolate the IT rollout as the sole cause.
- Nov 2025: Kingfisher (~1,900 stores, ~€14.5bn revenue) chose to keep SAP ECC 6 instead of migrating to S/4HANA. CTO Chris Blatchford said SAP's licensing proposal would multiply costs by about 20x. Kingfisher is migrating ECC to Google Cloud Platform with Rimini Street third-party maintenance. (Rimini claims 50–90% maintenance savings **[VENDOR claim]**) — [Le Monde Informatique](https://www.lemondeinformatique.fr/actualites/lire-kingfisher-choisit-de-conserver-ecc-sap-avec-une-tierce-maintenance-98483.html)

**Lidl (multi-country): eLWIS on SAP for Retail/HANA**
- Started around 2011 and halted July 2018 after about 7 years. Estimated €500m sunk (not officially confirmed by Lidl or SAP). Root cause: Lidl's inventory valuation was based on purchase prices whereas standard SAP Retail uses retail prices. Lidl chose to customise the software rather than adapt its processes, which led to cascading performance and cost problems. CEO Jesper Højer: the strategic goals "were not possible at an acceptable expense". SAP had given Lidl a customer award in April 2017, and the IT head left in May 2017 — [Consultancy.uk](https://www.consultancy.uk/news/18243/lidl-cancels-sap-introduction-having-sunk-500-million-into-it); [Computerwoche](https://www.computerwoche.de/article/2777764/lidl-stoppt-millionenschweres-sap-projekt-fuer-warenwirtschaft.html); [RetailDetail](https://www.retaildetail.eu/en/news/food/lidls-failed-it-project-cost-half-billion)
- An SAP user-group leader commented that a company wanting standard software "has to adapt its own processes" — [Consultancy.uk](https://www.consultancy.uk/news/18243/lidl-cancels-sap-introduction-having-sunk-500-million-into-it)

**STARK Group (DK/NO/SE/FI/DE/AT/UK): Company A's closest peer**
- FY2024/25 (published 12 Nov 2025): net sales €7.8bn, adjusted EBITDA €369m, reported EBITDA €288m after €81m transformation costs "especially relating to... major acquisitions in the UK and its digital transformation". The group has 1,050+ branches, 18,500+ employees and 7 countries. The Nordics are described as its "strongest and most mature market", where it grew share — [STARK Group press release](https://starkgroup.dk/newsroom/latest-news/stark-group-delivers-stable-net-sales-and-underlying-earnings-historically-challenging-market)
- A STARK job posting describes supporting the legacy ERP Aspect 4 while transitioning to "a more modernised IT platform". This indicates incremental modernisation, not a completed common ERP — [Jobbank.dk posting](https://jobbank.dk/job/2701825) (via search summary. Job ads are a weak source.)
- STARK outsourced IT infrastructure, operations and application management/development to NNIT. The deal covered 72 Danish stores and 2,600+ employees, with Norway, Sweden and Finland only partially included. The national scope differences illustrate per-country fragmentation — [NNIT press release on Mynewsdesk](https://www.mynewsdesk.com/nnit/pressreleases/nnit-signs-agreement-with-stark-on-outsourcing-of-it-2425045) (date not captured. The deal is likely pre-2019, so check before citing.)
- STARK used a SIAM model on ServiceNow so that "all end-to-end common processes [are] gathered in a single tool" — [KPMG Denmark case story **[VENDOR/ADVISOR]**](https://kpmg.com/dk/en/about-us/case-stories/stark-streamlined-its-governance-structure-with-a-new-operating-.html)

**Industry failure statistics (all [SECONDARY] — the Gartner figures are reported via aggregators, and the original Gartner research is paywalled)**
- Gartner is cited as predicting that by 2027 more than 70% of recently implemented ERP initiatives will fail to fully meet their original business goals. Gartner is also widely quoted as estimating that 55–75% of ERP projects fail to meet objectives — [Gartner insight page](https://www.gartner.com/en/information-technology/insights/what-it-leaders-must-do-to-avoid-disappointing-erp-initiatives); [Rand Group **[SECONDARY/VENDOR]**](https://www.randgroup.com/insights/services/solution-implementation/what-percentage-of-erp-implementations-fail/); [MeltingSpot **[SECONDARY]**](https://meltingspot.io/en/blog/erp-implementation-failure-why-70-percent-of-projects-fail)

### Inferences
- Lidl's lesson is that customising standard ERP to preserve local or legacy process quirks is the main failure mode. For Company A this argues for "global core, local configuration" plus process harmonisation, or for leaving ERPs in place behind an API/integration layer.
- Kingfisher shows that even a "substantially complete" unified platform can coincide with stock and logistics disruption in a major country unit. Ten years on, Kingfisher is avoiding the next big-bang ERP upgrade on cost grounds. This supports pitching Company A an API layer and composable front-ends (delivery tracking, store app) that deliver value without waiting for ERP consolidation.
- STARK still runs Aspect 4 and carries €81m/yr-scale transformation costs. This suggests that even the regional leader has not solved Nordic harmonisation through a single ERP, which strengthens the case for an incremental approach.

### Gaps
- Saint-Gobain Distribution, Ahlsell and Kesko harmonisation programmes were not researched in this pass.
- No McKinsey ERP statistic was verified, for example the McKinsey/Oxford finding that large IT projects run about 45% over budget. Verify before use.
- The exact attribution of Castorama losses to the IT rollout versus other factors is not quantified in sources.

## 4. MVP/pilot-first rollout lessons and Nordic change management

### Takeaway
The successful cases (Home Depot Sidekick and FDCs, Travis Perkins tracking) all used pilot-then-scale or market-by-market rollouts and co-design with users. The failures (Lidl, Kingfisher France) were long, group-wide, single-platform programmes. No sourced evidence was found specifically on Nordic union or works-council involvement in retail IT rollouts.

### Cited Findings
- Sidekick: piloted at about 600 stores, then chain-wide by end-2022, built in-house for fast feedback loops, with "no user training required" — [Retail Dive](https://www.retaildive.com/news/home-depot-sidekick-app/641040/); [Customer Experience Dive](https://www.customerexperiencedive.com/news/home-depot-associates-professional-customers-sidekick/724136/)
- FDCs: one market first (Dallas), then incrementally to 18+ of 40 planned markets — [Manufacturing.net](https://www.manufacturing.net/supply-chain/news/21113026/home-depot-opens-first-drivethrough-distribution-center); [Home Depot corporate](https://corporate.homedepot.com/newsroom/home-depot-opens-three-distribution-centers)
- Travis Perkins app "designed in conjunction with customers" (2021) — [Electrical Contracting News](https://electricalcontractingnews.com/news/travis-perkins-delivery-tracking/)
- Lidl: 7 years with an initial international rollout and a vendor award, then cancellation. Early "success" signals did not predict the outcome — [Consultancy.uk](https://www.consultancy.uk/news/18243/lidl-cancels-sap-introduction-having-sunk-500-million-into-it)

### Inferences
- Proposal structure suggested by the evidence: a single-country or single-region pilot (for example DK, or a store cluster), a fixed time-box, and explicit KPIs (delivery-window adherence, store hours saved, NPS). Then roll out country by country and reuse a shared core.

### Gaps
- No sourced material was found on Danish/Nordic union (e.g. HK Handel) or samarbejdsudvalg (works council) involvement in retail IT rollouts. This needs a dedicated search.

## 5. Netcompany case studies relevant to retail/logistics/Nordic

### Takeaway
No verifiable Netcompany retail, builders-merchant or logistics case study was found in this pass. The netcompany.com customer-cases URL tried returned 404, and searches surfaced only public-sector and financial-services work.

### Cited Findings
- Netcompany lists retail & wholesale and logistics among its served sectors. Known product platforms include AMPLIO (case handling), PULSE (real-time, connected operations) and EASLEY (AI/NLP) — [Yahoo Finance profile (Netcompany)](https://uk.finance.yahoo.com/quote/0YH9.L/profile) (via search summary)
- Netcompany delivered the HMRC Trader Support Service on its ERMIS customs product with AMPLIO case handling. This is a logistics/customs-adjacent reference — (via search summary of Netcompany material. The primary URL was not captured, so verify on netcompany.com.)

### Gaps
- Browse netcompany.com directly (cases/insights pages) for Danish retail clients. Candidates to check: Matas, Salling Group, Coop, DSV, PostNord, or any builders merchant. None was confirmed here.
