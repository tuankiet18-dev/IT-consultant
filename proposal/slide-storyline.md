# Company A — Proposal Storyline & Slide Content (10 slides) · v2

IT Consultant Challenge 2026 · Round 1 · English · PDF · max 10 slides · deadline 22:00, 26 Oct 2026

> **v2 changes after self-critique:**
> - **One solution in every market.** No more separate country modules; AI order intake moves to the year-2 roadmap.
> - **The 38% vs ~90% gap is explained** and used as an insight.
> - **Honest payback title.** Slide 8 now says 3–4 years and adds a tornado chart.
> - **B2B site-specific differentiation:** a day-before readiness check, crane- and unloading-aware slots, and site-schedule sync.
> - **AI in the MVP's Must-haves:** an exception copilot.
> - **Phased MVP:** Release 0 in week 10 (bought SaaS), Release 1 in week 16.
> - **Buy vs build is addressed.**
> - **Third-party hauliers are covered** as an assumption and a risk.
> - **Sensitivity check on the prioritisation matrix.**
> - **Short notes added:** why B2C comes later, premium-slot revenue upside, and the cost of doing nothing.

---

## The storyline in one paragraph (SCQA)

**Situation.** Company A sells building materials to contractors and DIY customers through hundreds of stores in Denmark, Norway and Sweden. Professional customers are the majority of the market, and margins across the sector are thin and falling.

**Complication.** Each country reports a different "most critical" problem: manual work in Denmark, store operations in Norway, delivery in Sweden. We see a common thread. Much of that pain comes from one broken chain from order to job site, where information does not flow between the merchant, the store, the driver and the contractor. Merchants believe they deliver well. Contractors experience something much worse. The market leader is already competing on delivery reliability.

**Question.** Where should Company A invest first to get the greatest impact fast?

**Answer.** **SiteReady**, one B2B delivery-reliability solution built on top of the existing systems:
- **What it does:** a day-before readiness check, a site-aware delivery slot, live ETA, digital proof of delivery, and an AI exception copilot.
- **Where:** the same solution in every market, configured locally.
- **How fast:** first release in 20 Swedish stores in ~10 weeks.
- **How each market benefits:**
  - Sweden: more reliable deliveries.
  - Denmark: fewer manual calls and less re-planning.
  - Norway: one standard way for stores to prepare delivery orders.

---

## Global design rules for the deck

- **Action titles:** every slide title is a full-sentence conclusion. Reading only the titles tells the whole argument (see the title check at the end).
- **Number tags:** every number carries **[cited]** (public source in the footnote) or **[assumption]** (to be validated in discovery).
- **Footnotes:** 7–8 pt at the bottom of each slide, as short source + year.
- **Colour code:** one accent per country (SE blue, DK red, NO dark green). The shared core is neutral grey.
- **Section tracker:** a thin bar top-right on every slide: *Identify · Prioritise · Solve · Scale*.
- **Text limit:** at most ~60 words of body text per slide. Anything longer goes to the speaker notes, especially on slides 3 and 8.

---

## Slide 1 — Cover + Executive summary

**Title:** *Fix the order-to-site chain once, and every market feels it where it hurts most*

**On-slide content**
- Team name · IT Consultant Challenge 2026 · Proposal to the Executive Board of Company A
- **Our recommendation:**
  1. **Identify:** Behind three different country priorities is one broken order-to-site chain: information does not flow from order to job site.
  2. **Prioritise & Solve:** Invest in **SiteReady**, one B2B delivery-reliability solution on top of existing systems. It replaces no ERP and uses AI from day one.
  3. **Scale:** The same solution goes to every market, configured locally. Pilot in 20 Swedish stores, with the first release live in ~10 weeks.
- **Three key numbers (tiles):**
  - **61%**: share of builders'-merchant turnover from professional customers (Norway) [cited]
  - **€2.9–10.4M / year**: benefit at full scale, conservative vs base [assumption-based model]
  - **~10 weeks**: to the first customer-facing release

**Visual:** the recommendation on the left; three number tiles on the right.

**Speaker note:** Give the answer first. The judges should know our choice within 20 seconds.

**Footnote:** Virke via Konkurransetilsynet (2021).

---

## Slide 2 — Problem understanding

**Title:** *Merchants think deliveries work; contractors experience a broken chain from order to job site*

**On-slide content**
- **Left: the chain diagram.** Order intake → Picking & staging (store / DC) → Dispatch → Delivery to site → Proof & invoice. Each country's priority sits on a different link:
  - 🇩🇰 **Denmark: manual processes.** Delivery bookings, re-planning and "where is my order?" calls are handled by phone and by hand. *[assumption: a large share of DK manual work is order/delivery-related]*
  - 🇳🇴 **Norway: inconsistent store ops.** Each store prepares and stages delivery orders in its own way. *[assumption: delivery staging is a material part of the store-ops problem]*
  - 🇸🇪 **Sweden: delivery & fulfilment.** Late, partial or wrong deliveries reach the job site.
  - **Underneath all three: fragmented systems.** There is no shared order, status or proof-of-delivery data.
- **Right: the perception gap (key insight).**
  - **Merchant view:** a case benchmark for building-materials distribution measured **~90% on-time-in-full** [cited, single case]
  - **Contractor view:** on a studied Swedish project, only **38%** of materials arrived "perfect": right time, quantity, place, condition and documents [cited, single project, 2016]
  - Why they differ: OTIF counts one supplier's order lines. "Perfect delivery" counts everything the site needed to start work. **The gap between them is what the customer feels.**
  - The same pattern appears across studies: 75% of US construction firms cite material lead times or shortages as a cause of delays [cited, association/vendor survey]. Merchants are *"rarely seen as an actor in the building process"* [cited, 2009].
- **Bottom banner:** *The brief says the challenges are "interconnected". We treat the shared cause, missing information flow, rather than three separate symptoms.*

**Visual:** horizontal chain with country flags pinned to links; a large "90% vs 38%" gap graphic on the right.

**Speaker note:**
- The brief says country priorities "may" differ. We treat them as hypotheses to test, and say clearly that our solution **reduces** DK and NO pain rather than solving all of it.
- The 38% comes from one project, so we use it to show the direction of the problem. We do not use it as a parameter in the business case.

**Footnotes:** Thunberg, Linköping Univ. (2016); UPC case study on OTIF in construction-materials distribution; AGC & Autodesk survey; SBUF Informerar 09:14 (2009).

---

## Slide 3 — Who experiences it and why it matters now

**Title:** *Late deliveries cost contractors real money, and the market leader is already competing on reliability*

**On-slide content**
- **Who feels it:**
  - **Site manager / contractor (primary):** crew idle, crane re-booked, schedule slips, time spent phoning the branch.
  - **Branch staff:** interrupted by "where is my order?" calls; re-planning by hand.
  - **Dispatcher / driver:** no early warning; repeat deliveries.
  - DIY customers are **out of scope for now**. Their orders are smaller and less time-critical, and they follow in a later release.
- **Why it matters:**
  1. **Professional customers are the core of the market:** **61%** of builders'-merchant turnover in Norway [cited].
  2. **Waiting is expensive here:** labour in Denmark costs **€50.1/hour** (2nd highest in the EU) [cited]. A 4-person crew waiting 1.5 hours costs ≈ **€180–300 per incident** [assumption].
  3. **The competition has moved to delivery:** the market leader targets "best-in-class delivery" and next-day delivery from a Swedish hub. Its Nordic EBITDA margin fell from 8.9% to **6.6%** [cited].
- **Callout: the cost of doing nothing.** Contractors absorb ≈ **€6–10M/yr** of downtime from failed site deliveries at Company A's scale [assumption-based]. A competitor that removes this wins the account. Company A would then have to compete on price, in a market where margins are already falling.

**Visual:** persona row; three evidence tiles; callout.

**Speaker note (backup evidence):**
- B2B buyers are "more willing than ever to switch suppliers" for a better omnichannel experience (McKinsey 2024).
- UK contractors rank timely site delivery above price (ECA 2019).
- Bauhaus is exiting Norway after NOK 870M in losses, and Bygma has had a 4th year of falling profit.

**Footnotes:** Virke via Konkurransetilsynet (2021); Eurostat (Mar 2025); STARK Group Annual Report 2025.

---

## Slide 4 — Prioritisation

**Title:** *B2B delivery reliability is the one opportunity that eases all three markets' priorities within months*

**On-slide content**
- **Options matrix** (weighted, scored 1–5, team judgement based on the evidence):

| Criterion (weight) | **A. B2B delivery reliability** | B. AI order intake | C. Store-ops app | D. ERP harmonisation |
|---|---|---|---|---|
| Business impact within 3 yrs (30%) | **5** | 3 | 3 | 3 |
| Fit with all 3 market priorities (25%) | **5** | 3 | 2 | 5 |
| Time to market (20%) | 4 | **5** | 3 | 1 |
| Strength of evidence (15%) | **4** | 3 | 1 | 1 |
| Foundation for future scale (10%) | 4 | 3 | 2 | **5** |
| **Weighted score** | **4.55** | 3.40 | 2.35 | 3.00 |

- **Robustness check:** A still ranks first when the time-to-market weight is raised to **50%** (A 4.34 vs B 4.00).
- **Why A wins:**
  - The pain is proven independently, not by vendor claims.
  - One solution eases each country's priority.
  - It answers a competitor already selling reliability in our pilot market.
- **Why not the others:**
  - **B. AI order intake:** the easiest savings to prove on paper, but it helps mainly Denmark and every ROI figure comes from vendors. → *Year-2 candidate, sized during discovery.*
  - **C. Store-ops app:** no public outcome data, and it treats a symptom.
  - **D. ERP harmonisation:** too slow and risky. Lidl stopped its SAP programme after ~7 years and an estimated **€500M** [cited]. In the year Kingfisher's unified SAP platform went live, its French chain Castorama's sales fell **7.3%** and retail profit **35%** [cited, multi-causal]. → *We reduce fragmentation step by step through an integration layer instead.*

**Visual:** matrix with column A highlighted; the robustness line underneath.

**Speaker note:** Be open that B has the easiest ROI to prove on paper. We chose A for its reach across all three markets, and B stays in the roadmap. The robustness check shows the result does not depend on the weights we picked.

**Footnotes:** Consultancy.uk (2018); Kingfisher RNS (Mar 2019).

---

## Slide 5 — The solution

**Title:** *SiteReady makes Company A the merchant that knows about a delivery problem before the site does*

**On-slide content**
- **Built for construction sites, not parcels (what is new):**
  1. **Day-before readiness check.** The evening before delivery, the system checks stock and picking status for every site order. Shortages are flagged, the AI copilot suggests substitutes or a split delivery, and the contractor hears about it **before** the crew is waiting.
  2. **Site-aware delivery slot.** The slot accounts for crane or unloading needs, gate access and the drop point. If the contractor moves the site date, a link lets them **re-book the slot themselves**.
  3. **Live ETA & proactive alerts.** SMS or web link with no app; an alert ~20 minutes before arrival; automatic delay notices.
  4. **Digital proof of delivery.** Photo of the goods at the drop point, signature and missing-item note, emailed and linked to the invoice.
  5. **Exception dashboard + AI copilot.** Dispatchers see at-risk orders ranked by impact. The copilot explains the cause and drafts the customer message for approval.
- **Architecture (3 layers):**
  - **Channels (local):** SMS / email / web page in DA·NO·SV; branch & dispatcher dashboard; driver app
  - **SiteReady core (global, EU-hosted):** order & delivery event model, readiness check, slot rules, notifications, POD store, AI services
  - **Integration layer (local adapters):** ERP, WMS, telematics, haulier systems through APIs and events. **No core ERP changes.**
- **Buy vs build:**
  - **Buy:** the commodity parts, such as the driver app, telematics and route tracking (proven SaaS for delivery management).
  - **Build:** what differentiates and is specific to Company A, namely the readiness check, the site-aware rules, the B2B customer experience and the integration layer.
- **Benchmark:** Travis Perkins (UK, 550+ branches) has had national live tracking since 2022: 2-hour slot, 20-minute alert, emailed POD [cited]. That is now the standard to match. **The readiness check and the site-aware features are how Company A gets ahead of it.**

**Visual:** five capability icons on the left; three-layer architecture on the right, with buy/build colour coding.

**Speaker note:** The integration layer is the first step against "fragmented systems". Each new adapter makes the next market cheaper, which is a gradual replacement (strangler pattern), not a big bang.

**Footnotes:** Builders Merchants News (Feb 2022); Fleet News (Oct 2015).

---

## Slide 6 — MVP scope and timeline

**Title:** *A 20-store Swedish pilot goes live in ~10 weeks and proves impact against control stores by week 28*

**On-slide content**
- **MVP boundaries:** 🇸🇪 Sweden · one region, **20 stores + 1 DC** · **B2B account customers** · site deliveries only
- **Release plan:**
  - **Release 0, week 10:**
    - Live ETA & delay SMS
    - Digital POD
    - Exception list
    - Built on bought delivery-management SaaS and today's dispatch data
  - **Release 1, week 16:**
    - Day-before readiness check
    - Site-aware slot booking (rule-based)
    - Contractor self-reschedule link
    - **AI exception copilot**
  - **After the pilot:** smart slot promise using machine learning on pilot data, and route optimisation
  - **Won't (now):** B2C, ERP changes, other countries
- **Timeline:**
  - **Weeks 1–6, discovery & consent:** baseline measurement, DPIA, union negotiation (MBL §11), haulier agreements
  - **Weeks 4–10:** SaaS configuration and ERP integration
  - **Week 10:** Release 0
  - **Week 16:** Release 1
  - **Weeks 10–28:** pilot vs matched control stores
  - **Week 28:** go / no-go
- **Pilot success criteria** (conservative targets, calibrated in discovery) [assumption]:
  - Perfect Delivery Rate **+10 pp** vs control
  - "Where is my order?" contacts per 100 deliveries **−30%**
  - Re-delivery rate **−15%**
  - B2B delivery satisfaction **+10 points**
  - ≥ 70% of deliveries with digital POD

**Visual:** release swim-lanes on a Gantt bar; KPI gate box.

**Speaker note:**
- **Why Sweden first:**
  - The delivery pain is highest there.
  - Building investment is forecast to grow **+4% per year** in 2026–27 [cited].
  - Materials-trade volume grew again in 2025 after four years of decline [cited].
  - The competitor is investing there.
- **Cost of stopping at week 28:** at most ~€1.5M [assumption], instead of a multi-year commitment.

**Footnotes:** Byggföretagen via TV4/TT (Mar 2026); Byggmaterialhandlarna via Fastighetstidningen (Jan 2026).

---

## Slide 7 — Where AI creates value

**Title:** *AI from day one where it is proven, always with a human in the loop and data kept in Europe*

**On-slide content**

| AI use | Value | When | EU AI Act tier |
|---|---|---|---|
| **Exception copilot.** Explains why an order is at risk, suggests substitutes or a split delivery, and drafts the customer message for the dispatcher to approve | Faster, consistent handling of problems; contractors are warned early | **MVP (Release 1)** | Minimal |
| **"Where is my order?" assistant.** Answers branch staff and customers from live delivery data | Fewer interruptions in branches | Phase 2 | Limited (must disclose AI, Art. 50) |
| **ETA & shortage prediction.** Learns from pilot data (stock, traffic, weather) | Earlier, more accurate warnings | Phase 2 | Minimal (vehicle level) |
| **AI order intake.** Turns emails, PDFs and BOMs into draft orders | Removes re-keying, especially in DK | Year-2 candidate | Minimal |

- **Evidence:**
  - Generative-AI assistance raised support-agent productivity **14%** on average and **34%** for novices (5,179 agents) [cited, NBER]
  - Document extraction is ~95–97% accurate on line items [cited, vendor benchmark], so a person approves before anything reaches the customer or the ERP
- **Responsible by design:**
  - No driver ranking. AI that scores individual workers counts as "high-risk" under the AI Act from **2 Dec 2027** [cited].
  - Models and data stay in the EU/EEA.

**Visual:** 4-row table; a small loop diagram: AI suggests → person approves → system acts → outcome feeds learning.

**Speaker note:** We start with a low-risk AI the dispatcher sees every day. Each approved suggestion becomes training data, so the AI improves as the pilot runs.

**Footnotes:** Brynjolfsson, Li & Raymond, NBER w31161; Regulation (EU) 2026/1744.

---

## Slide 8 — Business impact

**Title:** *Pays back in 3–4 years on cost savings alone; retention and premium slots are upside*

**On-slide content**
- **Three value levers:**
  - **L1, fewer "where is my order?" calls** = deliveries × calls per delivery × % avoided × cost per call
  - **L2, fewer re-deliveries** = deliveries × OTIF-miss rate × % needing a re-run × % reduction × cost per re-run
  - **L3, retained B2B margin** = B2B revenue delivered to site × retention uplift × gross margin (26.8% [cited])
- **Why L2 uses ~10%, not 62%:** the business case uses the merchant-side failure rate (~10% OTIF miss), because that is the cost Company A actually pays. The 38% contractor view is not a model input.
- **Results:**

| | Conservative | Base |
|---|---|---|
| Pilot (20 stores, 75k deliveries/yr) | €0.19M/yr | €0.70M/yr |
| Full scale (~300 stores) | **€2.9M/yr** | **€10.4M/yr** |
| …of which hard cost savings (L1+L2) | €2.1M/yr | €7.1M/yr |
| One-off investment, incl. SaaS set-up [assumption] | €3.8M | €3.4M |
| Run cost [assumption] | €0.8M/yr | €0.6M/yr |
| **3-year net (25% / 75% / 100% ramp)** | **≈ −€0.4M → break-even early year 4** | **≈ +€15.7M** |

- **Tornado chart: what moves the conservative €2.9M/yr most** [assumption ranges]:

| Driver (low – high) | Annual benefit range |
|---|---|
| Retention uplift (0% – 1.5%) | €2.1M – €4.5M |
| Deliveries per store per day (10 – 20) | €2.2M – €3.6M |
| Cost per re-delivery (€150 – €350) | €2.4M – €3.4M |
| "Where is my order?" calls per delivery (0.3 – 0.8) | €2.6M – €3.4M |

- **Upside not counted:**
  - **Premium slots:** contractors could pay extra for an early-morning or crane-time slot.
  - **AI order intake:** in year 2 it could add an estimated €0.5–2.1M/yr of freed staff capacity [assumption, vendor benchmarks].

**Visual:** stacked bars (L1/L2/L3) for conservative vs base; a tornado chart; a cited vs assumed legend.

**Speaker note:**
- The pilot exists to **measure** the three drivers at the top of the tornado. It is not meant to pay for itself.
- We show the conservative case openly: it breaks even on cost alone in 3–4 years.
- Inputs **cited:** revenue/store anchored on the Nordic market leader (€2.9bn / 265 branches), B2B share 61–62%, gross margin, labour costs.
- Inputs **assumed:** 15 deliveries/store/day, 10% OTIF miss, €250–350 per re-run, calls per delivery, 40% of B2B revenue delivered to site.

**Footnotes:** STARK Group Annual Report 2025; Virke via Konkurransetilsynet; Eurostat; vendor call-deflection benchmarks (low end applied).

---

## Slide 9 — Scale across markets

**Title:** *One solution, three configurations: every market gets the same SiteReady, tuned to its own top priority*

**On-slide content**
- **Rollout waves.** The same solution in each wave; only the local emphasis and the KPI that matters most change:

| Wave | Market | Same SiteReady, local emphasis | KPI the country board cares about | Timing |
|---|---|---|---|---|
| 1 | 🇸🇪 Sweden | Reliability at the site: readiness check, slots, ETA | Perfect Delivery Rate, re-deliveries | Pilot M1–M7 → all SE stores M8–M12 |
| 2 | 🇩🇰 Denmark | Remove manual work: automatic notifications and self-reschedule replace calls and re-planning by hand | Manual touches per order; call volume | M10–M15 |
| 3 | 🇳🇴 Norway | One standard store routine: the readiness check becomes the common way every store prepares and stages delivery orders | Staging errors; consistency across stores | M13–M18 |

- **Gates between waves:** pilot KPIs met · core stable · local baseline measured · consultation completed
- **Global vs local:**
  - **Global:** event model, readiness check, slot rules, notifications, POD, AI copilot, security, KPI definitions
  - **Local:** ERP/WMS and haulier adapters, language, business rules, invoicing format (Norway's B2B e-invoicing becomes mandatory **1 Jan 2027** [cited]), union agreements
- **Change management (employees & customers):**
  - **Employees:** drivers and branch staff help design it; store champions; a "no training required" UX target (Home Depot piloted its store app in ~600 stores before chain rollout [cited]).
  - **Unions:**
    - SE: MBL §11 negotiation before the decision.
    - DK: ≥ 6 weeks' notice for GPS-type controls.
    - NO: early discussion under Working Environment Act §9-2 [cited].
  - **Hauliers:** many drivers may work for third-party hauliers [assumption]. SiteReady then becomes a contract requirement, backed by data-processing agreements and an app that hauliers can use with their own fleets.
  - **Customers:** start with key contractor accounts; no-download links; DIY customers in a later release (with accessibility requirements).

**Visual:** one grey core bar across three country lanes; each lane labelled with its KPI.

**Speaker note:** The brief says "one strategic solution does not necessarily mean one identical implementation". Here we deliver exactly that: one product with three configurations. It is not three products.

**Footnotes:** VATupdate (Mar 2026); Retail Dive; MBL §11; DA/LO via DI; arbeidsmiljøloven §9-2.

---

## Slide 10 — Risks, assumptions and next steps

**Title:** *Risks are designed out early; our first six weeks turn assumptions into facts*

**On-slide content**

| Risk | Mitigation |
|---|---|
| Poor stock/master data → wrong readiness signals | Data-quality check in discovery; start with high-availability SKUs; conservative rules |
| Legacy ERP integration slower than planned | Thin API/event layer; batch fallback; Release 0 needs only dispatch data |
| Third-party hauliers don't adopt the driver app | Make it a contract requirement; haulier-friendly app; integrate haulier systems where they exist |
| Driver privacy & union resistance | GPS only during shifts, with short retention; no driver ranking; DPIA; drivers in the design team |
| Low adoption by branches / contractors | Co-design, store champions, no-download links, branch KPIs visible |
| AI suggests a wrong substitute or message | Human approval on every AI suggestion; confidence thresholds |
| Regulatory change (AI Act, Norway's EEA adoption, data transfers) | Design to the strictest EU standard everywhere; EU hosting |

- **Five numbers we will measure in discovery (weeks 1–6):**
  1. Current Perfect Delivery and OTIF rates (closing the 38% vs ~90% question for Company A)
  2. "Where is my order?" contacts per delivery
  3. Share of B2B revenue delivered to site
  4. Cost per truck-hour and per crane re-booking
  5. Share of deliveries run by third-party hauliers
- **Decision requested from the Board:**
  1. Approve **6-week discovery + 20-store Swedish pilot**, with go/no-go at week 28 (exposure ≤ ~€1.5M [assumption]).
  2. Name a business owner in Sweden, plus local owners in DK and NO.
  3. Commit to "integrate, don't replace": no ERP change in scope.

**Closing line:** *Fix the chain once. Every market feels it.*

**Footnotes:** Arbeidstilsynet/Datatilsynet joint guidance (NO, 2019); Regulation (EU) 2026/1744.

---

## Title check: read only the titles

1. Fix the order-to-site chain once, and every market feels it where it hurts most
2. Merchants think deliveries work; contractors experience a broken chain from order to job site
3. Late deliveries cost contractors real money, and the market leader is already competing on reliability
4. B2B delivery reliability is the one opportunity that eases all three markets' priorities within months
5. SiteReady makes Company A the merchant that knows about a delivery problem before the site does
6. A 20-store Swedish pilot goes live in ~10 weeks and proves impact against control stores by week 28
7. AI from day one where it is proven, always with a human in the loop and data kept in Europe
8. Pays back in 3–4 years on cost savings alone; retention and premium slots are upside
9. One solution, three configurations: every market gets the same SiteReady, tuned to its own top priority
10. Risks are designed out early; our first six weeks turn assumptions into facts

## Mapping to the judging criteria

| Criterion | Where it is proven |
|---|---|
| Problem understanding | Slides 2 (perception gap), 3 |
| Prioritisation & critical thinking | Slide 4 (matrix + robustness check); country priorities treated as hypotheses (slide 2); honest payback (slide 8) |
| Business impact | Slides 3 (cost of doing nothing), 8 (levers, tornado) |
| Feasible solution | Slides 5 (buy vs build), 6 (Release 0 in week 10, go/no-go gate), 10 |
| Structured thinking & innovation | SCQA storyline and action titles; slide 5 (readiness check, site-aware slots); slide 7 (AI copilot in the MVP); slide 9 (one product, three configurations) |

## Anticipated judge questions (prepare answers, not on slides)

| Question | Answer |
|---|---|
| "If you only had budget for Denmark?" | The same solution. Denmark's value is measured as manual touches and calls removed; the core is identical. |
| "Why not just buy a delivery-management tool?" | We do buy the commodity parts. We build only the readiness check, the site-aware rules, the B2B experience and the integration layer. |
| "38% or 90%: which is true?" | Both. They measure different things, and the gap is the insight (slide 2). |
| "What if the pilot fails?" | Go/no-go at week 28; exposure is about €1.5M instead of a multi-year programme. |
| "Isn't tracking table stakes?" | Yes, which is why we match it in Release 0 and differentiate with the readiness check and site-aware slots in Release 1. |
| "Where is AI in the MVP?" | The exception copilot in Release 1, human-approved and low-risk. |
| "What about B2C?" | Later release. B2C orders are smaller and less time-critical, but they reuse the same core. |
| "Drivers are subcontracted?" | That is an explicit assumption we test in discovery. Hauliers are handled through contracts and data-processing agreements. |

## Pre-submission checklist

- [ ] Verify Eurostat SE/NO hourly labour cost (`lc_lci_lev`); add to slide 3 if confirmed
- [ ] Verify AI Act dates against Regulation (EU) 2026/1744 in the Official Journal
- [ ] Re-open STARK Annual Report 2025 (€2,925M / 265 branches / 6.6% / 26.8%)
- [ ] Re-open the UPC OTIF case to confirm "~90%" before using it on slide 2
- [ ] Do **not** cite: Aarhus 23%/66%, Gartner "70% ERP failure", Byggmax "50 hours/day", "70% of B2B orders keyed manually", FMI $177bn
- [ ] Every number on slides tagged [cited] or [assumption]
- [ ] ≤ 60 words of body text per slide; overflow moved to speaker notes
- [ ] ≤ 10 slides, PDF, file named with the exact team name, submitted before 22:00 on 26 Oct 2026
