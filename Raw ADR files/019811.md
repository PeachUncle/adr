---
title: "ADR 016: Business Intelligence UI Integration"
type: "architecture"
audience: "developer"
status: "proposed"
priority: "high"
version: "1.0.0"
created: "2025-12-31"
updated: "2025-12-31"
reviewers: ["@antigravity"]
related: ["014-centralized-ui-design-system.md"]
tags: ["architecture", "ui", "business-intelligence"]
---

# ADR 016: Business Intelligence UI Integration

## Status
**Proposed** - Awaiting implementation

## Date
2025-12-31

## Context

VibeCoder currently focuses on technical architecture analysis and portfolio management. With the creation of comprehensive business documentation (marketing strategy, customer personas, campaigns), we need a way to:

1. **Visualize business metrics** alongside technical metrics
2. **Link business strategy** to technical implementation
3. **Track marketing campaigns** and their ROI
4. **Display customer personas** to inform product decisions
5. **Connect to Business Intelligence Hub** for centralized knowledge management

### Current State
- Business docs exist in `docs/04-business/`
- No UI visualization of business data
- No connection between technical and business metrics
- Business Intelligence Hub is separate repository

### Desired State
- Business Intelligence tab in VibeCoder UI
- Real-time business metrics dashboard
- Integration with Business Intelligence Hub
- Unified view of technical + business health

---

## Decision

We will implement a **Business Intelligence Tab** in the VibeCoder UI that:

1. **Parses business docs** from `docs/04-business/` using frontmatter metadata
2. **Displays key metrics** (ARR targets, MRR, campaign budgets, persona LTV)
3. **Links to Business Intelligence Hub** for detailed analysis
4. **Integrates with existing analytics** to show business impact of technical decisions

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VibeCoder UI (Next.js)                    │
│                                                              │
│  ┌────────────┬────────────┬────────────┬─────────────────┐ │
│  │ Portfolio  │  Reports   │ Analytics  │ Business Intel  │ │
│  └────────────┴────────────┴────────────┴─────────────────┘ │
│                                              │               │
│                                              ▼               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Business Intelligence Dashboard               │   │
│  │                                                       │   │
│  │  📊 Marketing Overview                               │   │
│  │  ├─ Target ARR: $250K                               │   │
│  │  ├─ Current MRR: $0                                 │   │
│  │  └─ Q1 Budget: $17,700                              │   │
│  │                                                       │   │
│  │  👥 Customer Personas (4)                            │   │
│  │  ├─ CTO Chris (LTV: $18K)                           │   │
│  │  ├─ DevOps Dana (LTV: $24K)                         │   │
│  │  ├─ Maintainer Mike (LTV: $600)                     │   │
│  │  └─ Founder Fiona (LTV: $3.6K)                      │   │
│  │                                                       │   │
│  │  📣 Active Campaigns (6)                             │   │
│  │  ├─ Product Hunt Launch ($2K)                       │   │
│  │  ├─ Lead Magnet ($3K/mo)                            │   │
│  │  └─ Webinar Series ($1K/mo)                         │   │
│  │                                                       │   │
│  │  🔗 [Open in Business Intelligence Hub]             │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ API Routes
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              API Layer (Next.js API Routes)                  │
│                                                              │
│  /api/business-intelligence/                                │
│  ├── /overview          → Marketing metrics                │
│  ├── /personas          → Customer persona data            │
│  ├── /campaigns         → Campaign status & budgets        │
│  └── /metrics           → Aggregated business KPIs         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ File System / GitHub API
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Sources                               │
│                                                              │
│  📁 Local: docs/04-business/*.md                            │
│  🌐 Remote: Business Intelligence Hub (GitHub API)          │
│  📊 Parsed: Frontmatter metadata + content                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: API Layer (Week 1)

#### 1.1 Create Business Intelligence API Routes

**File:** `app/api/business-intelligence/overview/route.ts`

```typescript
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

export async function GET() {
  try {
    // Read Marketing-Strategy.md
    const strategyPath = path.join(process.cwd(), 'docs/04-business/Marketing-Strategy.md');
    const strategyContent = fs.readFileSync(strategyPath, 'utf-8');
    const { data: strategyMeta } = matter(strategyContent);

    // Extract key metrics from frontmatter or content
    const overview = {
      product: strategyMeta.product || 'VibeCoder Architect Reviewer',
      version: strategyMeta.version || '2.17.1',
      targetARR: '$250,000', // Parse from content
      currentMRR: '$0',
      q1Budget: '$17,700',
      status: strategyMeta.status || 'approved',
      lastUpdated: strategyMeta.updated || new Date().toISOString()
    };

    return NextResponse.json(overview);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to load business overview' }, { status: 500 });
  }
}
```

**File:** `app/api/business-intelligence/personas/route.ts`

```typescript
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

interface Persona {
  name: string;
  title: string;
  ltv: string;
  willingnessToPay: string;
  painPoints: string[];
  priority: 'primary' | 'secondary' | 'tertiary';
}

export async function GET() {
  try {
    const personasPath = path.join(process.cwd(), 'docs/04-business/Customer-Personas.md');
    const personasContent = fs.readFileSync(personasPath, 'utf-8');
    const { data: personasMeta, content } = matter(personasContent);

    // Parse personas from markdown content
    const personas: Persona[] = [
      {
        name: 'CTO Chris',
        title: 'Scale-Up Technical Leader',
        ltv: '$18,000',
        willingnessToPay: '$200-$500/month',
        painPoints: ['Manual audits', 'Inconsistent standards', 'Hidden technical debt'],
        priority: 'primary'
      },
      {
        name: 'DevOps Dana',
        title: 'Consultancy Operations Lead',
        ltv: '$24,000',
        willingnessToPay: '$500-$2,000/month',
        painPoints: ['Client reporting overhead', 'Context switching', 'Audit fatigue'],
        priority: 'primary'
      },
      {
        name: 'Maintainer Mike',
        title: 'Open Source Polyglot',
        ltv: '$600',
        willingnessToPay: '$0-$50/month',
        painPoints: ['Dependency hell', 'Security alerts', 'Upgrade fatigue'],
        priority: 'tertiary'
      },
      {
        name: 'Founder Fiona',
        title: 'Solo SaaS Builder',
        ltv: '$3,600',
        willingnessToPay: '$50-$200/month',
        painPoints: ['Time scarcity', 'Technical decisions', 'Quality vs speed'],
        priority: 'secondary'
      }
    ];

    return NextResponse.json({ personas, lastUpdated: personasMeta.updated });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to load personas' }, { status: 500 });
  }
}
```

**File:** `app/api/business-intelligence/campaigns/route.ts`

```typescript
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

interface Campaign {
  name: string;
  type: string;
  budget: string;
  status: 'planned' | 'active' | 'completed';
  goal: string;
  startDate?: string;
  endDate?: string;
}

export async function GET() {
  try {
    const campaignsPath = path.join(process.cwd(), 'docs/04-business/Campaigns.md');
    const campaignsContent = fs.readFileSync(campaignsPath, 'utf-8');
    const { data: campaignsMeta } = matter(campaignsContent);

    const campaigns: Campaign[] = [
      {
        name: 'Product Hunt Launch',
        type: 'Product Launch',
        budget: '$2,000',
        status: 'planned',
        goal: '#1 Product of the Day, 500+ upvotes',
        startDate: '2025-01-15'
      },
      {
        name: 'Architecture Debt Calculator',
        type: 'Lead Generation',
        budget: '$3,000/month',
        status: 'active',
        goal: '500 qualified leads/month'
      },
      {
        name: 'Architecture Office Hours',
        type: 'Webinar Series',
        budget: '$1,000/month',
        status: 'active',
        goal: '100 attendees/webinar, 20% trial conversion'
      },
      {
        name: 'State of Repository Management 2025',
        type: 'Research Report',
        budget: '$5,000',
        status: 'planned',
        goal: '1,000 downloads, 10 press mentions',
        startDate: '2025-02-01'
      },
      {
        name: 'Partner Integration Showcase',
        type: 'Co-Marketing',
        budget: '$2,000/partner',
        status: 'planned',
        goal: '100 signups per integration'
      },
      {
        name: 'VibeCoder for Open Source',
        type: 'Community Program',
        budget: '$500/month',
        status: 'active',
        goal: '500 OSS users, 50 testimonials'
      }
    ];

    return NextResponse.json({ campaigns, lastUpdated: campaignsMeta.updated });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to load campaigns' }, { status: 500 });
  }
}
```

---

### Phase 2: UI Components (Week 2)

#### 2.1 Business Intelligence Page

**File:** `app/business-intelligence/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Card, Title, Text, Metric, Flex, Grid, Badge, ProgressBar } from '@tremor/react';
import { 
  CurrencyDollarIcon, 
  UserGroupIcon, 
  MegaphoneIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';

interface Overview {
  product: string;
  targetARR: string;
  currentMRR: string;
  q1Budget: string;
  status: string;
}

interface Persona {
  name: string;
  title: string;
  ltv: string;
  willingnessToPay: string;
  priority: 'primary' | 'secondary' | 'tertiary';
}

interface Campaign {
  name: string;
  type: string;
  budget: string;
  status: 'planned' | 'active' | 'completed';
  goal: string;
}

export default function BusinessIntelligencePage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [overviewRes, personasRes, campaignsRes] = await Promise.all([
          fetch('/api/business-intelligence/overview'),
          fetch('/api/business-intelligence/personas'),
          fetch('/api/business-intelligence/campaigns')
        ]);

        const overviewData = await overviewRes.json();
        const personasData = await personasRes.json();
        const campaignsData = await campaignsRes.json();

        setOverview(overviewData);
        setPersonas(personasData.personas);
        setCampaigns(campaignsData.campaigns);
      } catch (error) {
        console.error('Failed to fetch business intelligence data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8">Loading business intelligence...</div>;
  }

  const activeCampaigns = campaigns.filter(c => c.status === 'active');
  const totalQ1Budget = 17700; // Parse from campaigns

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <Title>Business Intelligence</Title>
        <Text>Marketing strategy, customer personas, and campaign performance</Text>
      </div>

      {/* Marketing Overview */}
      <Grid numItemsMd={2} numItemsLg={4} className="gap-6">
        <Card decoration="top" decorationColor="violet">
          <Flex justifyContent="start" className="space-x-4">
            <CurrencyDollarIcon className="w-8 h-8 text-violet-500" />
            <div>
              <Text>Target ARR (Year 1)</Text>
              <Metric>{overview?.targetARR}</Metric>
            </div>
          </Flex>
        </Card>

        <Card decoration="top" decorationColor="blue">
          <Flex justifyContent="start" className="space-x-4">
            <ChartBarIcon className="w-8 h-8 text-blue-500" />
            <div>
              <Text>Current MRR</Text>
              <Metric>{overview?.currentMRR}</Metric>
              <Text className="text-xs text-gray-500">Starting phase</Text>
            </div>
          </Flex>
        </Card>

        <Card decoration="top" decorationColor="amber">
          <Flex justifyContent="start" className="space-x-4">
            <MegaphoneIcon className="w-8 h-8 text-amber-500" />
            <div>
              <Text>Q1 2025 Budget</Text>
              <Metric>{overview?.q1Budget}</Metric>
            </div>
          </Flex>
        </Card>

        <Card decoration="top" decorationColor="emerald">
          <Flex justifyContent="start" className="space-x-4">
            <UserGroupIcon className="w-8 h-8 text-emerald-500" />
            <div>
              <Text>Customer Personas</Text>
              <Metric>{personas.length}</Metric>
              <Text className="text-xs text-gray-500">Defined segments</Text>
            </div>
          </Flex>
        </Card>
      </Grid>

      {/* Customer Personas */}
      <Card>
        <Title>Customer Personas</Title>
        <Text className="mb-4">Target customer segments with LTV and willingness to pay</Text>
        
        <Grid numItemsMd={2} numItemsLg={4} className="gap-4">
          {personas.map((persona) => (
            <Card key={persona.name} decoration="left" decorationColor={
              persona.priority === 'primary' ? 'violet' :
              persona.priority === 'secondary' ? 'blue' : 'gray'
            }>
              <Text className="font-semibold">{persona.name}</Text>
              <Text className="text-xs text-gray-500 mb-2">{persona.title}</Text>
              
              <Flex className="mt-4">
                <div>
                  <Text className="text-xs">LTV</Text>
                  <Text className="font-bold">{persona.ltv}</Text>
                </div>
                <div>
                  <Text className="text-xs">WTP</Text>
                  <Text className="font-bold text-xs">{persona.willingnessToPay}</Text>
                </div>
              </Flex>

              <Badge 
                color={persona.priority === 'primary' ? 'violet' : 'blue'}
                className="mt-2"
              >
                {persona.priority}
              </Badge>
            </Card>
          ))}
        </Grid>
      </Card>

      {/* Active Campaigns */}
      <Card>
        <Title>Marketing Campaigns</Title>
        <Text className="mb-4">Q1 2025 campaign overview and budget allocation</Text>

        <div className="space-y-4">
          {campaigns.map((campaign) => (
            <Card key={campaign.name} decoration="left" decorationColor={
              campaign.status === 'active' ? 'emerald' :
              campaign.status === 'completed' ? 'blue' : 'gray'
            }>
              <Flex>
                <div className="flex-1">
                  <Text className="font-semibold">{campaign.name}</Text>
                  <Text className="text-xs text-gray-500">{campaign.type}</Text>
                  <Text className="text-xs mt-1">{campaign.goal}</Text>
                </div>
                <div className="text-right">
                  <Badge color={
                    campaign.status === 'active' ? 'emerald' :
                    campaign.status === 'completed' ? 'blue' : 'gray'
                  }>
                    {campaign.status}
                  </Badge>
                  <Text className="font-bold mt-2">{campaign.budget}</Text>
                </div>
              </Flex>
            </Card>
          ))}
        </div>

        <div className="mt-6">
          <Text>Total Q1 Budget Allocation</Text>
          <ProgressBar value={100} color="violet" className="mt-2" />
          <Text className="text-xs text-gray-500 mt-1">
            ${totalQ1Budget.toLocaleString()} allocated across {campaigns.length} campaigns
          </Text>
        </div>
      </Card>

      {/* Business Intelligence Hub Link */}
      <Card className="bg-gradient-to-r from-violet-50 to-blue-50 dark:from-violet-950 dark:to-blue-950">
        <Flex>
          <div className="flex-1">
            <Title>Business Intelligence Hub</Title>
            <Text className="mb-4">
              Access the full Business Intelligence Hub for detailed analysis, Obsidian vault, and cross-repository insights.
            </Text>
          </div>
          <a 
            href="https://github.com/skquievreux/business-intelligence-hub" 
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors h-fit"
          >
            Open Hub →
          </a>
        </Flex>
      </Card>
    </div>
  );
}
```

---

#### 2.2 Add Navigation Link

**File:** `app/components/Navbar.tsx` (Update)

```typescript
// Add to navigation items
const navItems = [
  { name: 'Portfolio', href: '/' },
  { name: 'Reports', href: '/report' },
  { name: 'Analytics', href: '/analytics' },
  { name: 'Business Intelligence', href: '/business-intelligence' }, // NEW
];
```

---

### Phase 3: Advanced Features (Week 3-4)

#### 3.1 Real-time Sync with Business Intelligence Hub

**File:** `lib/business-intelligence/sync.ts`

```typescript
import { Octokit } from '@octokit/rest';

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

export async function syncFromBusinessHub() {
  try {
    // Fetch latest business docs from Business Intelligence Hub
    const { data } = await octokit.repos.getContent({
      owner: 'skquievreux',
      repo: 'business-intelligence-hub',
      path: 'repositories/vibecoder-architect-reviewer'
    });

    // Parse and cache locally
    // ... implementation
    
    return { success: true };
  } catch (error) {
    console.error('Failed to sync from Business Hub:', error);
    return { success: false, error };
  }
}
```

#### 3.2 Business Metrics Widget for Dashboard

Add a small widget to the main dashboard showing key business metrics:

```typescript
<Card>
  <Title>Business Health</Title>
  <Grid numItemsMd={3} className="gap-4 mt-4">
    <div>
      <Text>Target ARR</Text>
      <Metric>$250K</Metric>
    </div>
    <div>
      <Text>Active Campaigns</Text>
      <Metric>3</Metric>
    </div>
    <div>
      <Text>Q1 Budget</Text>
      <Metric>$17.7K</Metric>
    </div>
  </Grid>
  <a href="/business-intelligence" className="text-violet-600 text-sm mt-4 block">
    View full business intelligence →
  </a>
</Card>
```

---

## Consequences

### Positive
1. ✅ **Unified View:** Technical and business metrics in one place
2. ✅ **Data-Driven Decisions:** Easy access to customer personas when planning features
3. ✅ **Campaign Tracking:** Monitor marketing ROI alongside technical health
4. ✅ **Stakeholder Communication:** Export business metrics for investor updates
5. ✅ **Integration:** Links to Business Intelligence Hub for deep analysis

### Negative
1. ⚠️ **Maintenance Overhead:** Need to keep business docs in sync
2. ⚠️ **Parsing Complexity:** Extracting metrics from markdown requires robust parsing
3. ⚠️ **Data Duplication:** Business docs exist in both repos (mitigated by sync script)

### Mitigations
- **Automated Sync:** GitHub Actions sync every 6 hours
- **Frontmatter Standards:** Use consistent metadata format for easy parsing
- **API Caching:** Cache parsed business data to reduce file system reads
- **Fallback UI:** Graceful degradation if business docs are unavailable

---

## Implementation Checklist

### Week 1: API Layer
- [ ] Create `/api/business-intelligence/overview/route.ts`
- [ ] Create `/api/business-intelligence/personas/route.ts`
- [ ] Create `/api/business-intelligence/campaigns/route.ts`
- [ ] Add `gray-matter` dependency for frontmatter parsing
- [ ] Test API endpoints with Postman/Thunder Client

### Week 2: UI Components
- [ ] Create `app/business-intelligence/page.tsx`
- [ ] Add navigation link in `Navbar.tsx`
- [ ] Design persona cards with Tremor UI
- [ ] Design campaign status cards
- [ ] Add Business Intelligence Hub link

### Week 3: Integration
- [ ] Implement GitHub API sync for Business Hub
- [ ] Add business metrics widget to main dashboard
- [ ] Create export functionality for investor reports
- [ ] Add filtering/sorting for campaigns

### Week 4: Polish
- [ ] Add loading states and error handling
- [ ] Implement dark mode support
- [ ] Add tooltips and help text
- [ ] Write documentation
- [ ] Deploy to production

---

## Alternatives Considered

### Alternative 1: Embed Obsidian Vault
**Rejected:** Too complex, requires Obsidian server or iframe embedding

### Alternative 2: Static JSON Export
**Rejected:** Loses markdown formatting and requires manual updates

### Alternative 3: Separate Business Dashboard App
**Rejected:** Increases maintenance burden, fragments user experience

---

## Related Documents
- [[014-centralized-ui-design-system|Centralized UI Design System]]
- [[Marketing-Strategy|Marketing Strategy]]
- [[Customer-Personas|Customer Personas]]
- [[Campaigns|Marketing Campaigns]]

---

**Decision Date:** 2025-12-31  
**Status:** Proposed  
**Next Review:** 2025-01-07  
**Owner:** [@quievreux](https://github.com/skquievreux)
