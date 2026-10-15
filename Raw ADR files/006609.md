# ADR 0002 — NAT Gateway Design: Per-AZ vs Shared

## 📖 Context

Private subnets (app and DB tiers) require **outbound internet access** for:

- OS patching
- Package installation
- Pulling container images from ECR
- Accessing AWS APIs (via VPC endpoints where possible)

In AWS, the recommended way to give private subnets outbound internet is a **NAT Gateway** in each Availability Zone.
However, NATs are billed hourly and per-GB, which makes this a **cost vs resilience** tradeoff.

## ✅ Decision

We will provision **one NAT Gateway per Availability Zone** (2 total in our design).
Each private subnet will route to the NAT in the same AZ for egress.

## 🎯 Consequences

**Pros:**

- True high availability: if one AZ (and its NAT) fails, only that AZ’s resources are impacted. Other AZ remains operational.
- Follows AWS best practices for multi-AZ workloads.
- Clean isolation: no cross-AZ routing for outbound traffic.

**Cons:**

- Higher cost: ~$32/month per NAT Gateway + data transfer fees.
- For small dev environments, the extra NAT may feel expensive.

## 💸 Cost Math

- **NAT Gateway hourly:** ~$0.045/hour → ~$32/month each.
- **Two NATs (HA):** ~$64/month baseline, plus usage.
- **One NAT (shared):** ~$32/month baseline, but introduces cross-AZ data transfer fees when instances in the other AZ route through it.
- **Cross-AZ data charges:** $0.01/GB (intra-region data transfer).

For light dev/test environments:

- One NAT could save ~$30/month.
- But risk of single point of failure remains.

For staging/prod:

- Two NATs provide needed resilience; cost justified.

## 🔄 Alternatives Considered

1. **Single shared NAT Gateway (in one AZ)**

   - + Cheaper (~$32/month baseline).
   - – All private subnets depend on one NAT → AZ-level SPOF.
   - – Cross-AZ traffic incurs per-GB charges.
2. **NAT Instances (legacy)**

   - + Could reduce cost for low throughput.
   - – Requires management, patching, scaling. Not recommended by AWS.
3. **No NAT at all**

   - + Zero cost.
   - – Private subnets can’t patch or pull from ECR/S3 without endpoints. Not viable.

## 📌 Status

Accepted — we will deploy **one NAT Gateway per AZ** in staging/prod.
For dev environments, we may toggle down to a **single NAT** to save cost, with the risk clearly noted in docs.
