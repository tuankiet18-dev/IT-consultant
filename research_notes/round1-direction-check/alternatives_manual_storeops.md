# Alternatives test: X (B2B order automation, DK) and Y (store-ops standardisation, NO) vs delivery reliability

## Verification status (read first)
WebFetch failed for every host (DNS ENOTFOUND, or proxy 403 for ec.europa.eu). NO source below was opened.
Everything is from WebSearch result summaries only, so every item is UNVERIFIED. Re-open each URL before it goes into the proposal.

## 1. How manual is B2B order-to-cash (all unverified)
| Claim | Figure | Year | Measured | Independent? | URL |
|---|---|---|---|---|---|
| EU enterprises e-selling via EDI-type messages only / websites only / both | 3.1% / 17.7% / 3.1% | 2023 | Share of enterprises (Eurostat, dataset isoc_ec_esels) | Yes (official statistics), unverified | https://ec.europa.eu/eurostat/statistics-explained/index.php/E-commerce_statistics |
| Enterprises with e-sales: DK 38.76%, SE 36.50% | as stated | 2023 | Share of enterprises. No EDI split seen | Yes, unverified | same |
| Norway: 35% of firms (10+ staff) receive orders via website, 7% via EDI | 35% / 7% | 2011/2012 (old) | Statistics Norway | Yes, but dated, unverified | https://www.ssb.no/a/en/static/iktbrukn_en/tab-2012-10-08-08-en.html |
| About 7 in 10 B2B orders arrive by email/phone/fax/spreadsheet before ERP keying | ~70% | 2025 data, article 2026 | Cites Conexiom data | NO, vendor-sourced, secondhand | https://www.workd.com/insights/articles/hidden-cost-managing-b2b-orders-email-2026/ |
| Denmark e-invoice share >40% (consumer invoices) | >40% | 2016 (Billentis via ECB) | Not B2B | Semi-independent, dated, unverified | https://www.ecb.europa.eu/paym/intro/mip-online/2016/html/mip_qr_1_article_4_e-invoicing.da.html |
| Norway B2B e-invoicing >80% electronic / 84% | 80% / 84% | undated | Secondary sources, scope unclear | Unclear, unverified | https://econnect.eu/en/docs/knowledge/regulations/europe/norway ; https://ec.europa.eu/digital-building-blocks/sites/spaces/einvoicingCFS/pages/718735714/2024+Norway+2024+eInvoicing+Country+Sheet |
| Norway B2B e-invoicing mandate from 1 Jan 2027 (EHF) | n/a | 2026 | KPMG tax note | Professional-services, unverified | https://kpmg.com/us/en/taxnewsflash/news/2026/03/tnf-norway-ministry-of-finance-accelerates-mandatory-digital-bookkeeping-and-e-invoicing-requirements.html |
| Denmark: no B2B e-invoice mandate; B2G mandatory since 2005 | n/a | n/a | Secondary guides | Vendor-ish, unverified | https://lookuptax.com/docs/einvoicing/nemhandel-einvoicing-denmark |

Not found: any Danish/Nordic building-materials share of orders by email/PDF/phone. No Digitaliseringsstyrelsen or Digdir B2B invoice-share figure. No McKinsey/Gartner order-channel split (McKinsey Global B2B Pulse 2022, n=3,862, is about rep interaction channels, not order intake). The Gartner "75% of B2B buyers prefer no rep" claim came via a vendor blog and is unverified.
Implication: the claim that Company A's order intake is largely manual in Denmark is NOT supported by independent evidence we have. It would have to come from Company A's own case data.

## 2. Measured outcomes of order automation
Found only vendor material (Conexiom, Nanonets, Infomaze, WorkD). None independent.
- Nanonets foodservice co-op: 93% touchless on order confirmations (vendor case, unverified): https://nanonets.com/customers/unipro
- WorkD cites an "industry benchmark" of up to 87% touchless, no source; says most mid-market distributors are far below it.
- APQC benchmark: top performers 94% of orders with no human intervention; bottom performers 20% or more needing intervention (APQC is a benchmarking nonprofit, semi-independent, unverified): https://www.sdcexec.com/sourcing-procurement/article/21137951/apqc-touchless-order-performance
- Conexiom: Sonepar "1,000+ hours saved monthly" (vendor): https://conexiom.com/intelligent-document-processing-for-electrical-distributors
- No peer-reviewed or audited data for Ferguson, Grainger, Wolseley, Beijer, Ahlsell, Saint-Gobain, Würth. Nothing on per-order time or error rates from independent sources.
- Realistic touchless: treat 80-90%+ as a vendor/best-case ceiling; no independent evidence for building-materials mix (many line items, product-code ambiguity, project quotes).

## 3. Nordic building-materials companies (unverified)
- Byggmax: online ~18% of sales Q1 2020 (company statement via trade press) and ECDB estimate ~18% for 2024 (estimate, not company). 2025 net sales SEK 6,133M (5,986M), +2.5%. Nothing on manual work. https://www.placera.se/pressmeddelanden/byggmax-group-year-end-report-byggmax-group-1-january-31-december-2025-20260130 ; https://ecommercedb.com/company/byggmax-group-ab-publ-13299
- Ahlsell: ~SEK 50bn, 5,700 staff, 200+ stores; joined the industry Vilma product-data standard. No manual-work numbers. https://www.mynewsdesk.com/se/byggmaterialhandlarna/pressreleases/ahlsell-ansluter-sig-till-byggmaterialhandelns-vilmastandard-foer-mer-effektivt-digitalt-produktfloede-3295920
- Bygma: only noted as Vilma member. Beijer Byggmaterial: a 2013 e-commerce push mention; RELEX customer page exists (https://relexsolutions.com/customers/beijer-byggmaterial, not read; vendor). Optimera, Silvan, XL-Bygg, Jem&Fix, Davidsen, Stark: nothing found.
- Note: Beijer Byggmaterial sits under STARK Group (per search summary).

## 4. Store-ops standardisation, measured outcomes (unverified)
- Gap Inc. randomised field experiment (Kesavan et al., Management Science, 2022): 28 stores, 9 months (Nov 2015-Aug 2016), responsible scheduling raised store productivity 5.1% (sales +3.3%, labour -1.8%). Control stores already had some stable-scheduling practices. Independent academic; relevant to scheduling, not task apps or standardisation. Source seen: https://soon.works/research/stable-scheduling-randomized-experiment-gap (not opened).
- Dutch retail chain, team incentives in 108 stores randomised: null effect (working paper, https://repec.tinbergen.nl/tin/wpaper/17090.rdf).
- Dehoratius et al. 2025 (POM): VR lab experiment, lower task complexity gives up to +38.2% productivity and up to -93.6% errors. Lab, not field.
- Home Depot Sidekick task app: rolled out to all US stores end 2022; no outcome figures (trade press): https://www.ciodive.com/news/home-depot-sidekick-app/640521/
- Nothing found for Lowe's, Bunnings, Kingfisher. No independent measured outcomes for task-management apps.

## 5. Strongest for / against
X (order automation, DK)
- For: Directly attacks the data-entry and error step upstream of picking and delivery, so wrong or late order data causes wrong or late deliveries; EDI/e-commerce share is low EU-wide (3.1% EDI-only), suggesting room; Norway B2B e-invoicing mandate (2027) shows direction of travel.
- Against: Our independent evidence is thin; touchless numbers are vendor claims; benefit is confirmation/invoicing speed and cost, only indirectly delivery reliability (stock, transport, last mile are separate); Danish firms are already digitally advanced (high e-sales share, e-invoicing capability), so baseline may be less manual than assumed.

Y (store ops standardisation, Norway)
- For: Only independent randomised field evidence found (Gap, +5.1% productivity); inconsistency is a stated company challenge, and Norway is a defined pilot market.
- Against: Gap result concerns scheduling in apparel, not DIY/trade counters; effect is on productivity not delivery; Dutch incentive trial null; no Nordic or building-materials evidence; weaker link to delivery reliability.

## Verdict
Neither X nor Y has independent evidence stronger than delivery reliability from what we could check. Y has the single best independent causal study (Gap) but off-topic; X has only vendor claims plus generic Eurostat context. Treat both as unproven against delivery until sources are opened and Company A data is used.
