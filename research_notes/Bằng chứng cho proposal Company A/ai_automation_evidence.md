# Evidence for AI Automation of Manual Processes in B2B Distribution and Building-Materials Retail

Labels: [INDEPENDENT] = statistical office, academic, press/trade media, company's own disclosure. [VENDOR] = marketing material from a vendor selling the solution (treat as upper bound, unaudited). [CONSULTANCY] = McKinsey etc.
Research date: 2026-10-21. About 20 tool calls; several targeted fetches timed out (McKinsey pages), so some McKinsey figures come from search snippets.

## (a) Cost and prevalence of manual order processing in B2B distribution

### Takeaway
Most B2B orders in distribution still come in unstructured (email, PDF, phone, fax) and get keyed in by hand. The figures that recur are about 70% of orders handled manually, 8-12 minutes per order, 1-3% error rate (APQC, per Conexiom) or higher on complex orders, and 20-40% of inside-sales/CS time spent on data entry. Almost all of these numbers come from vendors. I found no independent survey (Gartner, NAW, MDM) quantifying channel mix.

### Cited Findings
- Rexel Canada (electrical distributor): before automation, "70% of sales orders were manually entered" (case study dated 17 Feb 2022). [VENDOR: Conexiom] — [Conexiom / Rexel Canada](https://conexiom.com/blog/rexel-canada-uses-conexioms-sales-order-automation-to-focus-on-customer-experience); also reported in trade press [Canadian Electrical Wholesaler](https://www.canadianelectricalwholesaler.ca/order-automation-key-to-rexel-and-conexiom-s-successful-partnership)
- "Seventy percent of B2B sales orders are still processed manually in 2025" via email, phone, fax, spreadsheets. [VENDOR/blog, original source not given] — [Workd](https://www.workd.com/insights/articles/hidden-cost-managing-b2b-orders-email-2026/)
- Customer service and inside-sales reps spend 20-40% of their time on manual order handling. Average manual order-entry error rate is 1-3% (attributed to APQC benchmarks, no link). About 12 minutes to enter each order. Worked example: 1,500 orders/month × 12 min = 300 h/month ≈ 3.75 FTE ≈ USD 225k/yr at USD 60k/FTE. Orders can sit in a queue for 4-6 hours. [VENDOR: Conexiom] — [Conexiom, "The real cost of manual order entry"](https://conexiom.com/blog/the-real-cost-of-manual-order-entry-in-b2b-operations)
- Manual handling costs USD 30-80 per order vs USD 1-5 automated. A 15-line order takes 8-12 minutes to key. Manual error rates of 15-20% (order-level, so not comparable with the 1-3% field-level figure). [VENDOR/blog, unsourced] — summarised from [Darwin AI blog](https://blog.getdarwin.ai/en/ai-order-taking-whatsapp-email-orders-erp) / [Orderwerks](https://www.orderwerks.com/blog/wholesale-distributor-ordering-portal) search snippets
- Manual B2B order processing costs £15-45 per order vs £1.50-4 self-served/automated. A typical order takes 5-10 minutes manually. [VENDOR/blog] — [Baytech Consulting](https://www.baytechconsulting.com/blog/quiet-share-shift-self-service)
- European B2B bakery supplier: manual email-order data errors were 12% before automation. [VENDOR: Beam AI] — [Beam AI case study](https://beam.ai/resources/case-studies/order-management-case-study)
- Trade press: order entry from unformatted documents (material lists, POs, job-site photos) is still "heavily manual for many distributors" in lumber, hardware, plumbing and HVAC. [INDEPENDENT trade press, reporting a vendor launch] — [Distribution Strategy Group, Sept 2026](https://distributionstrategy.com/2026/09/toolbx-launches-ai-order-entry-for-building-supply-distributors/)
- Fastenal reported 61% of Q1 (2025) sales through digital channels, so at large, mature distributors a large share of orders is already structured. [INDEPENDENT press] — [Digital Commerce 360, May 2025](https://www.digitalcommerce360.com/2025/05/27/4-b2b-distributors-ai-trends/)

### Inferences
- A defensible planning range for a Nordic builders merchant is 8-12 min per manual order and 1-3% line/field error rate. Use the conservative APQC-attributed 1-3%, not the 12-20% vendor figures.
- The "70% manual" figure fits mid-size, trade-counter-heavy merchants better than digital leaders like Fastenal (61% digital). The proposal should present it as "up to ~70%" and suggest validating it with Company A's own order-channel data.

### Gaps
- No independent (Gartner, McKinsey, NAW, MDM) statistic on channel mix (email/PDF/phone/fax) in wholesale distribution was found. Search returned only vendor material.
- The APQC benchmark behind the 1-3% figure could not be checked directly (Conexiom gives no link).
- Esker, Rossum and ABBYY channel-mix reports were not retrieved.

## (b) Proven ROI and accuracy of AI order capture / document extraction

### Takeaway
Vendors report 70-85% touchless orders, 70-80%+ less processing time and about 90% fewer errors. Field accuracy of modern LLM/IDP extraction is about 99% on simple header fields and 95-97% on line items. Line items are the hard part, so confidence-based human review stays necessary.

### Cited Findings
- Major "Global 100" safety/security/energy distributor: hit its 70% touchless order target by 2020 and now averages 70-80% touchless order entry across 4 divisions in 20+ countries. [VENDOR: Conexiom] — [Conexiom case PDF](https://conexiom.com/wp-content/uploads/2023/04/Major-Global-100-Company-Safety-Security-and-Energy.pdf)
- Rexel Canada automated sales orders for 600 customers and saved Inside Sales "thousands of hours" (no exact figure). [VENDOR] — [Conexiom / Rexel](https://conexiom.com/blog/rexel-canada-uses-conexioms-sales-order-automation-to-focus-on-customer-experience)
- ADI Global (security distributor): case titled "saves 142 hours/day with Conexiom". [VENDOR] — [casestudies.com / Conexiom ADI](https://www.casestudies.com/company/conexiom/case-study/adi-global-saves-142-hoursday-with-conexiom)
- Conexiom claims "80%+ reduction in order entry time" and "90%+ reduction in errors", and markets ">80% touchless orders". [VENDOR] — [Conexiom](https://conexiom.com/blog/the-real-cost-of-manual-order-entry-in-b2b-operations)
- European B2B bakery supplier (MS Dynamics NAV): email handling time fell from 4 hours to under 15 minutes, data errors from 12% to under 1%, and over 85% of order workflows are fully automated. [VENDOR: Beam AI] — [Beam AI](https://beam.ai/resources/case-studies/order-management-case-study)
- Doppler (Austrian industrial manufacturer): 70% faster order processing and 90% fewer errors with B2Bware AI Order Hub. [VENDOR, hosted by UK Made Smarter programme] — [Made Smarter PDF](https://www.madesmarter.uk/media/4jbpgtsp/b2bware_ai_order_hub_case_study_2.pdf)
- Toolbx AI Order Entry (building supply, launched Sept 2026) reads emails, PDFs, spreadsheets and job-site photos and matches lines to the dealer catalogue. It produces a draft order in under 1 minute, flags low-confidence matches, and no order enters the ERP without employee approval. Expected match rate is ≥95% "with complete product data". It integrates with Epicor BisTrack/Eagle, ECI Spruce and DMSi Agility. Early adopter is Swift Supply (5 locations, AL/FL). Toolbx serves 200+ dealers at 1,000+ locations. [INDEPENDENT trade press reporting VENDOR claims] — [Distribution Strategy Group](https://distributionstrategy.com/2026/09/toolbx-launches-ai-order-entry-for-building-supply-distributors/)
- McKinsey example: an industrial/electronics player used genAI to prescreen supplier bid documents, cutting review time by 90% and bringing tender-to-project-start forward by 2 months. A large electronics distributor uses genAI for tariff-code classification. A building-materials distributor uses genAI for personalised marketing emails. [CONSULTANCY, anonymised] — [McKinsey, "How generative AI is disrupting distribution"](https://www.mckinsey.com/industries/industrials-and-electronics/our-insights/distribution-blog/how-generative-ai-is-disrupting-distribution) (via search snippet; page fetch timed out)
- Extraction accuracy: modern systems reach 95-99% field-level accuracy on typed invoices. Simple fields (totals, vendor name) exceed 99%, while line items and multi-row tax land at 95-97%. [VENDOR/blog aggregation] — [invoicedataextraction.com](https://invoicedataextraction.com/blog/invoice-ocr-accuracy-developer-guide); [Cradl AI](https://www.cradl.ai/posts/invoice-data-extraction-with-ai)

### Inferences
- A realistic target for a business case: 60-80% touchless orders after a ramp-up, about 70-80% less handling time on automated orders, and error rates under 1% with human review of exceptions. Present these as vendor-reported ranges, not guarantees.
- Building-materials BOMs/material lists are harder than invoices: free-text product descriptions need to be matched to SKUs. Toolbx's "≥95% match with complete product data" caveat shows that catalogue/master-data quality is a prerequisite.

### Gaps
- No named, quantified AI order-automation result was found for Ferguson, Wolseley, Würth, Ahlsell, STARK, Beijer, Grainger, Saint-Gobain or Kingfisher. Earnings materials (Ferguson, Grainger FY2025) mention AI only generically.
- No independent audit of touchless rates or of vendor accuracy claims was found.

## (c) AI deployed by builders merchants / DIY retailers

### Takeaway
The big players are live with genAI in quoting/takeoff (Home Depot Blueprint Takeoffs), customer advice assistants (Kingfisher "Hello Casto", built on its Athena framework) and catalogue/search work (Grainger). I found no public evidence for Nordic merchants (STARK, Beijer, Byggmax, Bauhaus, Kesko) in this session.

### Cited Findings
- Home Depot (19 Nov 2025) launched an AI-powered Blueprint Takeoffs solution. It delivers a full material list and quote for a single-family project "within days, a process that used to take weeks", and Pros access it through outside sales reps or the Pro Desk. [INDEPENDENT: company IR] — [Home Depot IR](https://ir.homedepot.com/news-releases/2025/11-19-2025-120103402); [Home Depot corporate](https://corporate.homedepot.com/news/company/home-depot-launches-ai-powered-blueprint-takeoffs)
- Kingfisher: Project Athena is an in-house orchestration framework that sits on top of LLMs (OpenAI ChatGPT, Google Gemini) and routes each query to the right microservice. Castorama's "Hello Casto" genAI DIY assistant gives step-by-step advice and product recommendations, with English versions planned for B&Q and Screwfix. The group AI team had about 30 people working on 20+ AI initiatives, many for internal efficiency (2024). [INDEPENDENT press] — [Modern Retail, Jun 2024](https://www.modernretail.co/technology/as-brands-look-for-ai-edge-bq-retail-owner-kingfisher-is-expanding-in-house-development/); [Retail Gazette interview, Aug 2024](https://www.retailgazette.co.uk/blog/2024/08/interview-kingfisher-ai/); [Retail Insight Network](https://www.retail-insight-network.com/news/kingfisher-ai-diy-assistant/)
- Grainger uses AI/ML for product associations at scale, a custom GPT assistant to find SKU-addition opportunities, and ML for marketing spend. AI also supports search relevance, recommendations and inventory. [INDEPENDENT: company earnings/press] — [Grainger Q4 2025 deck](https://s1.q4cdn.com/422144722/files/doc_earnings/2025/q4/presentation/2025-Q4_Earnings-Deck-Final.pdf); [Digital Commerce 360](https://www.digitalcommerce360.com/2025/05/27/4-b2b-distributors-ai-trends/)
- Toolbx AI Order Entry for North American lumber/building-supply dealers (see (b)). [Trade press] — [Distribution Strategy Group](https://distributionstrategy.com/2026/09/toolbx-launches-ai-order-entry-for-building-supply-distributors/)

### Inferences
- Home Depot's move shows that BOM-to-quote is a commercially valued use case for Pro customers. The proposal can frame BOM/PDF-to-basket as "following the US market leader".
- Kingfisher's multi-LLM orchestration layer is a reference architecture for avoiding vendor lock-in.

### Gaps
- Not retrieved: Lowe's (Mylow / Mylow Companion), Travis Perkins, STARK Group, Byggmax, Bauhaus, Kesko, Saint-Gobain Distribution, Ahlsell. Searches for STARK/Ahlsell/Beijer AI order automation returned nothing relevant.
- No public case for ML delivery-ETA prediction at a builders merchant was found.

## (d) Customer service ("where is my order") and generative AI productivity evidence

### Takeaway
The strongest independent evidence is Brynjolfsson, Li and Raymond (NBER w31161): +14% issues resolved per hour, +34% for novice agents. WISMO is the largest single contact type for companies shipping physical goods (vendor-cited 20-40%), and proactive ETA notifications reportedly remove 30-50% of those contacts.

### Cited Findings
- 5,179 customer support agents; access to a genAI assistant raised productivity (issues resolved/hour) by 14% on average and by 34% for novice/low-skilled workers, with minimal effect on experienced staff. It also improved customer sentiment and employee retention. [INDEPENDENT: academic, NBER/QJE] — [NBER w31161](https://www.nber.org/system/files/working_papers/w31161/w31161.pdf); [arXiv 2304.11771](https://arxiv.org/abs/2304.11771)
- McKinsey estimates genAI could add USD 2.6-4.4 trillion a year globally, with the biggest impact in customer operations, marketing and sales, software engineering and R&D. It also says genAI improves customer service without increasing headcount. [CONSULTANCY] — [McKinsey distribution blog](https://www.mckinsey.com/industries/industrials-and-electronics/our-insights/distribution-blog/how-generative-ai-is-disrupting-distribution)
- WISMO queries make up 20-40% of inbound support for companies shipping physical products (25-40% in e-commerce, 50-60% at peak). Proactive status/delay notifications remove 30-50% of WISMO contacts. Cost per contact falls from about USD 5-10 human-handled to USD 0.50-1 AI-handled. [VENDOR glossaries: Lorikeet, Decagon, Zowie; B2C-oriented] — [Lorikeet](https://www.lorikeetcx.ai/glossary/wismo-where-is-my-order); [Decagon](https://decagon.ai/glossary/what-is-wismo-where-is-my-order); [Zowie](https://getzowie.com/blog/wismo-automation)

### Inferences
- In builders merchants, WISMO calls usually concern delivery slots to job sites. A proactive ETA (from route/telematics data) plus an LLM front-end is a plausible "quick win". The 30-50% deflection figure is B2C vendor data and should be presented as indicative.
- The NBER result fits Nordic merchants with high staff turnover or seasonal staff, since the largest gains go to novices.

### Gaps
- No B2B-specific WISMO share for distributors was found. No independent study of ML delivery-ETA accuracy in building-materials logistics was found.

## (e) Nordic labour costs

### Takeaway
Denmark has the second-highest hourly labour cost in the EU: EUR 51.7 in 2025, against an EU average of EUR 34.9. Sweden has among the highest non-wage cost shares (about 31.7%). Exact Swedish and Norwegian figures were not retrieved.

### Cited Findings
- 2025: EU average EUR 34.9/h, euro area EUR 38.2/h. Highest were Luxembourg EUR 56.8, Denmark EUR 51.7 and the Netherlands EUR 47.9. Labour costs grew 4.1% in the EU (2024→2025) and 3.0% in Denmark. Sweden had the second-highest non-wage cost share at 31.7%. [INDEPENDENT: Eurostat, March 2026 release, via search snippet] — [Eurostat euro-indicators 19 Mar 2026](https://ec.europa.eu/eurostat/web/products-euro-indicators/w/3-19032026-bp)
- 2024: EU EUR 33.5/h, euro area EUR 37.3/h, Denmark EUR 50.1/h. Services sector EUR 33.3 (EU) / EUR 36.4 (euro area). Non-wage share was 24.7% in the EU, and Sweden had the highest share at 31.6%. [INDEPENDENT: Eurostat] — [Eurostat news 28 Mar 2025](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20250328-1)
- Norway: SSB StatBank table 07685 gives average labour cost per FTE by industry (SIC2007), including wholesale/retail, for 2008-2024. The value was not extracted. [INDEPENDENT] — [SSB table 07685](https://www.ssb.no/en/statbank1/table/07685/)

### Inferences
- Illustrative saving: one FTE ≈ 1,600-1,700 paid hours/yr × about EUR 50/h (Denmark) ≈ EUR 80-85k fully loaded per year. The Conexiom example (1,500 orders/month × 12 min ≈ 3.75 FTE) would then equal about EUR 300k/yr in Denmark. This is my calculation; the hours per FTE are an assumption to state explicitly in the proposal.

### Gaps
- Not retrieved: Sweden's and Norway's 2025 hourly cost in EUR, and sector G (wholesale/retail) hourly costs for DK/SE/NO. Check Eurostat dataset lc_lci_lev (by NACE) and SSB table 07685 before use.

## (f) Risks: LLM extraction error, human-in-the-loop, confidence thresholds

### Takeaway
Accuracy on header fields is high, but line items are 95-97%. Best practice is field-level confidence scoring with a threshold of about 0.85-0.90, routing low-confidence fields to human review, and requiring human approval before ERP posting (as Toolbx does). Research shows calibrated confidence can lift accuracy on auto-processed items to about 99% while still automating about 80% of them.

### Cited Findings
- Typical confidence thresholds are 0.85-0.90. Fields above the threshold pass automatically and those below go to an exception queue. [VENDOR/blog] — [invoicedataextraction.com](https://invoicedataextraction.com/blog/invoice-ocr-accuracy-developer-guide)
- ExtractConf (arXiv 2606.24420): on DocILE (55-field invoices with a 26% baseline failure rate), multi-signal confidence reaches 0.928 ROC AUC and 99.1% accuracy at 80% coverage. The authors say the central challenge is reliable field-level confidence estimation, not raw extraction accuracy. [INDEPENDENT: academic preprint, not peer-reviewed] — [arXiv 2606.24420](https://arxiv.org/pdf/2606.24420)
- Toolbx design: low-confidence matches are flagged and no order enters the ERP without employee approval. [Trade press/VENDOR] — [Distribution Strategy Group](https://distributionstrategy.com/2026/09/toolbx-launches-ai-order-entry-for-building-supply-distributors/)
- Line items extract at 95-97% vs 99%+ for simple fields. [VENDOR/blog] — [invoicedataextraction.com](https://invoicedataextraction.com/blog/invoice-ocr-accuracy-developer-guide)

### Inferences
- Recommended design for the proposal: draft order → confidence per line → auto-post only above threshold for known customers/SKUs → human queue otherwise. Start with 100% human approval during a pilot, then relax thresholds as measured precision allows.
- Master-data quality (SKU descriptions, customer item cross-references) is the main dependency for accuracy.

### Gaps
- No independent benchmark of LLM extraction specifically on construction BOMs/material lists was found.
