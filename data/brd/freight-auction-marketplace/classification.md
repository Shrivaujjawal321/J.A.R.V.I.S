# Classification

> **Jurisdiction corrected 2026-07-29 by Boss: "the system is made for us client. This system use in
> USA."** The first classification assumed India. That was wrong and every India-specific regime
> below has been replaced. Agent parts A1, A2 and A6 were drafted against the India reading and are
> being re-run. No India-derived content survives into the BRD.

- **Business type:** Multi-sided B2B marketplace (US domestic road freight / truckload). Two-sided
  liquidity problem (shippers ⇄ carriers) with a **third, non-transacting participant** (the
  consignee/receiver) who is affected by the outcome but never signs up. Asset-backed physical
  fulfilment — the deliverable is a truck moving freight, not software.

- **Engagement type:** **Client project.** Boss is building this for a client whose operation is in
  the USA. This partially answers the sponsor question — the platform operator is the client, not
  Boss — but the client's own role in the freight chain is still open and is a blocking question
  (see below).

- **Secondary characteristics:**
  - Payments-central — invoice generation is explicitly in the stated flow
  - **Very likely a regulated freight-brokerage operation, not merely software.** In the US, a party
    that arranges transportation for compensation between a shipper and a motor carrier is a
    *property broker* and requires its own FMCSA operating authority, a surety bond, and process
    agents. Whether the client already holds that authority — or intends the platform to be pure
    software used by a licensed broker — is the single most consequential open question in this
    document. It changes the regulatory surface, the money flow, and the liability exposure.
  - Reverse-auction mechanism design — auction integrity is a first-class business concern
  - Custody / liability chain — goods are in someone's possession throughout; loss and damage
    liability is a core requirement area, not an edge case
  - Trust marketplace — strangers transacting on high-value freight, in a market currently
    experiencing severe fraud pressure

- **Compliance surface (candidates only — each to be confirmed or ruled out, never asserted):**
  - **FMCSA operating authority** — motor carrier (MC/USDOT) vs **property broker** authority; the
    OP-1 registration path, the **BMC-84 surety bond / BMC-85 trust fund**, and **BOC-3** process
    agent designation
  - **49 CFR Part 371 — property broker regulations**, including the broker record-keeping duty and
    the transacting parties' right to review the broker's record of each transaction. A marketplace
    that intermediates price has a direct interest in this rule.
  - **Carmack Amendment (49 U.S.C. §14706)** — the governing federal regime for interstate cargo
    loss and damage liability, including claim-filing and suit-limitation minimums. This replaces
    every India-law assumption about cargo liability.
  - **Bill of Lading** — the contract of carriage and the document the delivery signature sits on.
    "POD" in this market is normally a signed BOL / delivery receipt, and whether it is signed
    *clear* or *with exception* is what decides a cargo claim.
  - **49 CFR Part 387 — minimum financial responsibility** (public liability insurance minimums for
    motor carriers; higher tiers for hazmat), plus cargo insurance as a commercial requirement
  - **Hours of Service (49 CFR Part 395) and the ELD mandate** — a hard legal constraint on transit
    time, and a real cause of delay and detention exposure
  - **CDL licensing, drug & alcohol testing, and the FMCSA Clearinghouse** — driver eligibility
  - **FMCSA safety data (SAFER / SMS / CSA BASICs, operating-authority status and age)** — the
    standard inputs to carrier vetting
  - **Negligent selection / vicarious liability exposure for brokers** — US plaintiffs routinely sue
    the broker that selected a carrier involved in a serious accident. **A mechanism that awards
    strictly to the lowest bidder is directly exposed here**, because carrier selection criteria
    become evidence. This is the sharpest collision between the stated design and US law.
  - **Double brokering, carrier identity theft and fictitious pickup** — currently an acute US fraud
    problem, and structurally attracted to open marketplaces that award on price
  - **49 CFR Part 376 — truth-in-leasing**, if owner-operators are leased on
  - **Money transmission / MSB registration and state licensing** — triggers only if the platform
    holds or routes funds between shipper and carrier. Replaces the RBI question entirely.
  - **Freight factoring and Notices of Assignment** — where a carrier has factored its receivable,
    payment is legally directed to the factor. Paying the carrier instead creates real exposure.
  - **Tax and reporting** — W-9 collection and 1099-NEC reporting on carrier payments; state sales
    tax generally does not apply to interstate freight transportation but is state-specific
  - **State privacy law — CCPA/CPRA and the other state comprehensive privacy statutes.** There is
    no federal omnibus law. Driver and consignee personal data are in scope, and the consignee never
    signed up. Replaces DPDP entirely.
  - **Antitrust (Sherman Act §1)** — a repeat-participant lowest-bid auction on fixed lanes has a
    bid-rigging surface
  - **Hazmat (49 CFR 171-180)**, oversize/overweight permits, UCR and IFTA — applicability depends
    on scope decisions still open

- **Initiative size budget:** **LARGE (30-60 pages).** Three roles, a full physical fulfilment
  lifecycle, an auction mechanism, money movement, and a regulated brokerage surface. Budget is a
  ceiling, not a target — padding remains a scored defect.

- **Solution-stated-without-problem?** **PARTIALLY — and this is still the most important gap.**
  Boss supplied a detailed *mechanism* (reverse auction, lowest bid wins) and a *process*, but no
  problem statement. A Five Whys ladder is MANDATORY and blocking, specifically on *why an auction*
  and *why lowest-bid* rather than lowest-among-qualified or best-value. In the US market this is
  sharpened by two facts: incumbent load boards already perform price discovery, and the best-funded
  attempt at digital freight brokerage in this market shut down in 2023 despite roughly a billion
  dollars raised. The premise needs a defensible answer, not an assumption.

- **Template variant:** marketplace/platform. Extra weight: §5 Stakeholders (three-sided), §6/§7
  process, §10 NFRs, §14 Risks, §17 business case. Extra sections warranted: auction mechanism
  design, liability & custody chain, exception handling.
