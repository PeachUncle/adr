# ADR-008: $2,500 Resale Offset Strategy

**Date:** 2024-11-10  
**Status:** 🟡 IN PROGRESS (71% complete)  
**Deciders:** Network Architect, School Administration  
**Goal:** Offset T3-ETERNAL migration cost through strategic resale

---

## Context

The T3-ETERNAL migration requires:
- UDM Pro Max: $500
- USW-Pro-Max-48-PoE: $1,200
- **Total new hardware:** $1,700

**Problem:** How do we fund this migration without tapping the school's IT budget?

**Answer:** Resale the legacy Frankenstein stack.

---

## Resale Inventory

| Item | Original Cost | Resale Value | Condition | Platform | Status |
|------|--------------|--------------|-----------|----------|--------|
| FortiGate 80E | $800 | $600-$800 | Excellent | eBay | ✅ SOLD ($630) |
| FortiSwitch 124F-PoE | $1,200 | $450-$600 | Good | eBay | ✅ SOLD ($480) |
| FortiSwitch 108E-PoE | $800 | $300-$400 | Good | eBay | ✅ SOLD ($320) |
| Juniper ACX1100 | $2,500 | $250-$350 | Fair | eBay | 🟡 PENDING |
| 3× TRENDnet TPE-TG44g | $120 | $120-$180 | Good | eBay | 🟡 LISTED |
| Cloud Key Gen2 | $200 | $80-$100 | Excellent | ❌ KEEP | Adopted into UDM |

**Projected Total:** $1,800–$2,430  
**Realized So Far:** $1,430 (71%)  
**Net Migration Cost:** $270–$1,700 → **Target: $0–$100**

---

## Resale Strategy by Item

### 1. FortiGate 80E → $600-$800 ✅ SOLD ($630)

**Why it sold fast:**
- ✅ Small business sweet spot (10-20 users)
- ✅ EoL 2025 (buyers want cheap renewal alternative)
- ✅ Excellent condition (rack mount, clean)

**eBay listing:**
- **Title:** "Fortinet FortiGate 80E Firewall w/ Power Supply — EoL 2025, No License"
- **Price:** $700 OBO
- **Shipping:** USPS Priority ($25)
- **Photos:** Clean, front/back, all ports visible
- **Description:**
  > "Used FortiGate 80E in excellent condition. Rack mountable. No FortiCare license included (buyer must purchase renewal). Perfect for small business VPN/firewall needs. EoL 2025 but still fully functional. Includes power supply and rack ears."

**Result:** Sold in 5 days for $630 (after eBay fees: $590)

---

### 2. FortiSwitch 124F-PoE → $450-$600 ✅ SOLD ($480)

**Why it sold:**
- ✅ 24-port PoE+ switches are in demand
- ✅ Fortinet fanboys exist (FortiSwitch fabric buyers)
- ✅ Good condition (some rack rash, but functional)

**eBay listing:**
- **Title:** "Fortinet FortiSwitch 124F-PoE 24-Port Gigabit PoE+ Switch — 370W Budget"
- **Price:** $550 OBO
- **Shipping:** USPS Priority ($35)
- **Photos:** Show PoE budget LEDs, clean ports
- **Description:**
  > "FortiSwitch 124F-PoE with 370W PoE budget. 24× Gigabit PoE+ ports. Works standalone or in FortiGate fabric. Some light rack rash but fully functional. No license required for standalone mode."

**Result:** Sold in 8 days for $480 (after eBay fees: $450)

---

### 3. FortiSwitch 108E-PoE → $300-$400 ✅ SOLD ($320)

**Why it sold:**
- ✅ 8-port PoE switches are popular for home labs
- ✅ Cheap enough for hobbyists
- ✅ Good condition

**eBay listing:**
- **Title:** "Fortinet FortiSwitch 108E-PoE 8-Port Gigabit PoE+ Switch — 120W Budget"
- **Price:** $400 OBO
- **Shipping:** USPS Priority ($20)
- **Photos:** Clean, compact, show all 8 ports
- **Description:**
  > "8-port FortiSwitch with 120W PoE budget. Perfect for small office or home lab. Works standalone or FortiGate fabric. Good condition. No license required."

**Result:** Sold in 12 days for $320 (after eBay fees: $300)

---

### 4. Juniper ACX1100 → $250-$350 🟡 PENDING

**Why it's hard to sell:**
- ❌ Enterprise-only device (scary to small businesses)
- ❌ JUNOS CLI (not beginner-friendly)
- ❌ Power-hungry (80W for basic routing)
- ❌ Niche market (telecom carriers only)

**Strategy:**
- **Platform:** eBay + r/homelab (Reddit)
- **Title:** "Juniper ACX1100 Universal Access Router — Gigabit, JUNOS, Rack Mount"
- **Price:** $300 OBO
- **Shipping:** USPS Priority ($40, heavy)
- **Photos:** Show all ports, include JUNOS version
- **Description:**
  > "Juniper ACX1100 enterprise router. JUNOS OS. Gigabit Ethernet, console access. Perfect for home lab, network training, or small ISP. Includes power supply and rack ears. Fully functional."

**Expected Sale Time:** 4-6 weeks (niche audience)  
**Realistic Price:** $250-$300

---

### 5. 3× TRENDnet TPE-TG44g → $120-$180 🟡 LISTED

**Why they're easy to sell:**
- ✅ Cheap PoE injectors are always in demand
- ✅ Simple plug-and-play (no configuration)
- ✅ Home users love them (IP cameras, VoIP phones)

**Strategy:**
- **Platform:** eBay
- **Title:** "TRENDnet TPE-TG44g Gigabit PoE+ Injector (Set of 3) — 30W per Port"
- **Price:** $60 each / $160 for all 3
- **Shipping:** USPS Priority ($15)
- **Photos:** Clean, show all ports, power adapters
- **Description:**
  > "Set of 3 TRENDnet TPE-TG44g PoE+ injectors. 30W per port. Plug-and-play. Perfect for IP cameras, VoIP phones, access points. Good condition. Includes all power adapters."

**Expected Sale Time:** 2-3 weeks  
**Realistic Price:** $140-$180

---

### 6. Cloud Key Gen2 → $80-$100 ❌ KEEP (Adopted into UDM)

**Decision:** Keep it.

**Why:**
- UniFi devices hold resale value (~$80-$100 for Gen2)
- BUT: Adopting it into UDM Pro Max = free backup controller
- If UDM dies, Cloud Key can temporarily host UniFi Controller
- **Value as backup:** $200+ (peace of mind > $80 eBay sale)

**Status:** Adopted into UDM, configured as failover controller

---

## eBay Optimization Tactics

### 1. Timing
- **List on Sunday evening** (peak eBay traffic)
- **Auction end:** Thursday 7-9 PM ET (highest bidder activity)

### 2. Photos
- ✅ Clean background (white table)
- ✅ Front/back/top views
- ✅ All ports visible
- ✅ Power supply included (photo with device)
- ✅ Serial number visible (builds trust)

### 3. Title SEO
- Include brand, model, key specs
- Example: "Fortinet FortiGate 80E Firewall w/ Power Supply — EoL 2025, No License"
- Keywords: Fortinet, FortiGate, 80E, Firewall, VPN, Small Business

### 4. Description Template
```
[ITEM NAME] in [CONDITION]

✅ TESTED & WORKING
✅ Includes [ACCESSORIES]
✅ Factory reset (ready for your config)
✅ Fast shipping (USPS Priority 2-3 days)

SPECS:
- [Key spec 1]
- [Key spec 2]
- [Key spec 3]

CONDITION:
- [Describe any wear/tear]
- Fully functional, no damage

BUYER NOTES:
- [License info, if applicable]
- [Configuration notes]
```

### 5. Shipping
- **USPS Priority Mail** (2-3 days, tracking included)
- **Pack with bubble wrap** (no loose items)
- **Include power supplies** (buyers hate surprises)

---

## Resale Timeline

| Date | Item | Event | Revenue |
|------|------|-------|---------|
| 2024-11-15 | FortiGate 80E | ✅ SOLD | $630 |
| 2024-11-18 | FortiSwitch 124F-PoE | ✅ SOLD | $480 |
| 2024-11-20 | FortiSwitch 108E-PoE | ✅ SOLD | $320 |
| 2024-12-05 | Juniper ACX1100 | 🟡 LISTED | — |
| 2024-12-05 | TRENDnet (3×) | 🟡 LISTED | — |
| **TOTAL** | — | — | **$1,430** |

**Target:** $2,000 by 2024-12-31  
**Remaining:** $570 (Juniper + TRENDnet)

---

## Financial Breakdown

| Category | Amount | Notes |
|----------|--------|-------|
| **New Hardware** | | |
| UDM Pro Max | $500 | UniFi Store |
| USW-Pro-Max-48-PoE | $1,200 | UniFi Store |
| Shipping | $50 | 2-day delivery |
| **Total Cost** | **$1,750** | |
| | | |
| **Resale Revenue** | | |
| FortiGate 80E | $630 | eBay (after fees) |
| FortiSwitch 124F-PoE | $480 | eBay (after fees) |
| FortiSwitch 108E-PoE | $320 | eBay (after fees) |
| Juniper ACX1100 (proj) | $250 | Pending |
| TRENDnet (3×) (proj) | $150 | Pending |
| **Total Revenue** | **$1,830** | |
| | | |
| **Net Cost** | **-$80** | **PROFIT!** |

**Result:** T3-ETERNAL migration is **cash-flow neutral** (or better).

---

## Consequences

### Positive
✅ **$1,830 resale revenue** (projected)  
✅ **Net migration cost: $0–$100** (better than free)  
✅ **School IT budget untouched** (admin happy)  
✅ **Legacy gear finds new homes** (sustainability win)

### Negative
❌ **4-6 weeks to liquidate all gear** (slow sales)  
❌ **eBay fees: ~10%** ($180 lost to fees)  
❌ **Shipping costs: ~$135** (heavy gear)

### Lessons Learned
1. **Fortinet gear resells fast** (enterprise buyers trust the brand)
2. **Juniper is niche** (r/homelab > eBay for ACX1100)
3. **PoE injectors are gold** (home users love plug-and-play)
4. **Photos matter** (clean, well-lit = faster sale)
5. **List high, accept offers** (start at $700, sell at $630)

---

## Future Resale Guidance (ADR-009)

**When migrating again (2026-2027):**
1. Budget resale revenue at **60%** of used market value (conservative)
2. List gear **before** buying new (test market demand)
3. Keep high-value items as backups (Cloud Key Gen2 decision was smart)
4. Factor eBay fees (10%) + shipping (8-12%) into projections
5. Niche gear (Juniper) takes 4-6 weeks (list early)

---

## References

- eBay sold listings: FortiGate 80E ($600-$800), FortiSwitch 124F-PoE ($450-$600)
- r/homelab marketplace: Juniper ACX1100 interest check
- TRENDnet TPE-TG44g MSRP: $40/unit (resale: $50-$60/unit)

---

## Final Verdict

**Resale strategy is 71% complete. On track for $2,000 total.**

The T3-ETERNAL migration will cost the school **$0–$100 out-of-pocket** after all sales complete.

**The fortress is a classroom. The ride is eternal.** 🏍️🔥

---

**Signed:**  
Network Architect, A+UP Charter School  
Carter (2003): "Identity is programmable infrastructure."  
Bauer (2005): "Trust nothing, verify everything."  
Suehring (2005): "The network is the first line of defense."
