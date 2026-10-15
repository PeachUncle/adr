# ADR 006: Open Source MIT License

**Status:** Accepted

**Date:** 2024-11-12

**Deciders:** Piotr Świderski

**Technical Story:** Need to choose a license that balances portfolio benefits, community growth, and business model protection.

---

## Context

BuildFlow is being developed as both a portfolio project and a potential SaaS business. The licensing decision affects:

### Current Situation
- Primary goal: Portfolio showcase for job seeking
- Secondary goal: Potential SaaS business
- Solo developer (initially)
- Want community contributions
- Need to show code publicly
- Concerned about business value protection

### Requirements
- **Portfolio**: Code must be publicly visible
- **Trust**: Open source shows transparency
- **Business**: Must not prevent SaaS monetization
- **Community**: Allow contributions and derivatives
- **Simplicity**: Easy to understand license
- **Compatibility**: Compatible with common libraries

---

## Decision

**We will license BuildFlow under the MIT License for all repositories.**

### License Text
```
MIT License

Copyright (c) 2024 Piotr Świderski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Implementation
1. Add `LICENSE` file to every repository
2. Add license header to each source file
3. Mention in README.md
4. Add license badge to README

### What MIT Allows
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ✅ Can sublicense
- ✅ Can sell copies

### What MIT Requires
- ⚠️ License and copyright notice must be included
- ⚠️ No warranty provided

---

## Consequences

### Positive
- ✅ **Portfolio Value**: Shows willingness to share code
- ✅ **Trust**: Open source = transparency
- ✅ **Community**: Easiest for contributions
- ✅ **Adoption**: No barriers to trying the software
- ✅ **Compatibility**: Works with most other licenses
- ✅ **Learning**: Others can learn from code
- ✅ **Simple**: Well-understood, not controversial
- ✅ **Business**: SaaS model still viable

### Negative
- ⚠️ **Competition**: Anyone can start competing SaaS
- ⚠️ **Fork Risk**: Someone could fork and rebrand
- ⚠️ **No Copyleft**: Changes don't have to be shared back
- ⚠️ **Attribution**: Only requirement is copyright notice

### Business Model Protection

**Why open source doesn't kill the SaaS business:**

1. **Technical Barrier**
   - Self-hosting requires technical skills
   - Server setup and maintenance
   - Security updates and patches
   - Database management
   - SSL certificates
   - Email service configuration
   - File storage setup
   - Backup management

2. **Ongoing Costs**
   - Server hosting: $50-200/month
   - Email service: $10-50/month
   - File storage: $10-100/month
   - SSL certificate management
   - Developer time for updates
   - **Total**: $70-350/month + time

3. **Convenience Value**
   - SaaS: Click and start using
   - No setup time
   - Automatic updates
   - Guaranteed uptime
   - Professional support
   - Data backup included
   - **Worth**: $20-80/month for peace of mind

4. **Target Market**
   - Construction businesses are NOT tech-savvy
   - 95%+ will choose convenience over cost
   - $29/month is cheaper than DevOps time
   - "Just works" has immense value

5. **Proven Models**
   - **Ghost**: MIT license, $9-200/month SaaS, profitable
   - **GitLab**: MIT license, $15B valuation
   - **Discourse**: GPL license, successful hosting business
   - **Cal.com**: AGPLv3, raised $25M with hosted offering
   - **Supabase**: Apache 2.0, raised $80M

### Risks & Mitigation
- **Risk**: Large company copies and builds competing SaaS
  - **Mitigation**: First mover advantage, construction domain expertise, community
  - **Reality**: Unlikely for niche market
  
- **Risk**: Fork becomes more popular
  - **Mitigation**: Active maintenance, community engagement, better features
  - **Reality**: Original project usually stays dominant
  
- **Risk**: Someone rebrands and sells
  - **Mitigation**: Trademark the name "BuildFlow", build brand recognition
  
- **Risk**: No contributions come back
  - **Mitigation**: Accept this trade-off for simplicity and adoption

---

## Alternatives Considered

### Alternative 1: AGPLv3 (Copyleft)
**Description:** Strong copyleft license requiring source disclosure for network use

**Pros:**
- Protects against competing SaaS (must share code)
- Ensures improvements come back
- Still open source
- Used by Cal.com, Plausible successfully

**Cons:**
- More restrictive
- Scares away corporate contributors
- Complex legal implications
- Less portfolio-friendly (companies avoid AGPL)
- May prevent adoption

**Why rejected:** Portfolio is primary goal. Companies are wary of AGPL. MIT is safer for job seeking.

### Alternative 2: Business Source License (BSL)
**Description:** Source-available but not open source, converts to open source after time

**Pros:**
- Prevents commercial competition for X years
- Code is visible (portfolio benefit)
- Converts to MIT/Apache later
- Used by MariaDB, CockroachDB

**Cons:**
- NOT open source (marketing disadvantage)
- Complex to understand
- May limit contributions
- Unusual choice (less trust)
- Doesn't help with hiring (shows fear)

**Why rejected:** Want true open source status. BSL shows distrust and fear. Not good for portfolio narrative.

### Alternative 3: Dual License (MIT + Commercial)
**Description:** MIT for self-hosting, commercial license for hosted use

**Pros:**
- Revenue from hosted competitors
- Still open source
- Can charge large companies

**Cons:**
- Complex to manage
- Requires legal structure
- Unclear enforcement
- Rare in practice
- Doesn't fit solo developer model

**Why rejected:** Too complex for solo developer. Premature optimization. Can add later if needed.

### Alternative 4: Proprietary (Closed Source)
**Description:** Keep code private, no license

**Pros:**
- Complete control
- No competition from forks
- Protects business value completely

**Cons:**
- No portfolio benefit (can't show code)
- No community contributions
- No trust factor
- Not marketable as open source
- Defeats primary purpose

**Why rejected:** Defeats the entire purpose of the project as portfolio piece.

### Alternative 5: Apache 2.0
**Description:** Similar to MIT but with patent grant

**Pros:**
- Explicit patent grant
- Similar permissiveness to MIT
- Used by many big projects

**Cons:**
- Slightly more complex
- Patent clause can be confusing
- Less common in PHP world

**Why rejected:** MIT is simpler and more common. No significant benefit for this project.

---

## Related Decisions

- [ADR-001](001-multi-repository-strategy.md) - Each repo gets MIT license
- [ADR-009](009-feature-flags-for-tiers.md) - SaaS tiers work with open source

---

## References

- [Choose a License](https://choosealicense.com/)
- [MIT License](https://opensource.org/licenses/MIT)
- [Open Source Business Models](https://monetize.substack.com/p/open-source-business-models)
- [Ghost's Open Source Journey](https://ghost.org/about/)
- [GitLab's Open Core Model](https://about.gitlab.com/company/pricing/)
- [Why Open Source Doesn't Kill SaaS](https://www.youtube.com/watch?v=pNgCDBolSqo)

---

## Notes

### Future Considerations

If competitive pressure emerges, we can:
1. **Trademark**: Register "BuildFlow" trademark
2. **Branding**: Build strong brand identity
3. **Features**: Keep some features closed source (white-label, SSO)
4. **Enterprise**: Offer enterprise features with commercial license
5. **License Change**: Future versions could use different license (but unlikely)

### What Open Source Brings

**For Portfolio:**
- Shows code quality
- Demonstrates best practices
- Proves experience
- Shows confidence in abilities
- Differentiator in job market

**For Project:**
- Free testing by community
- Bug reports and fixes
- Feature suggestions
- Contributors (maybe)
- SEO benefits (GitHub stars)
- Social proof

**For Business:**
- Trust and transparency
- Lower barrier to trial
- Community marketing
- Developer advocates
- Integration ecosystem

### Statistics

- 95%+ of small businesses choose SaaS over self-hosting
- Self-hosting true cost: $100-500/month (server + time)
- SaaS pricing: $20-80/month
- Convenience value: Priceless for non-technical users

### Market Reality

Construction businesses:
- Are NOT tech-savvy
- Value simplicity over cost
- Need "just works" solutions
- Will pay for support
- Don't have DevOps resources

Therefore: Open source does NOT threaten the business model.

---

**Last Updated:** 2024-11-12
