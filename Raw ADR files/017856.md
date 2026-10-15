# ADR 007: EC2 Spot Instances for Cost Optimization

**Date**: 2026-01-13  
**Status**: Accepted

## Context

EC2 costs can be significant for a starter project. Options:

1. **On-Demand instances** - Pay full price, always available
2. **Reserved instances** - 1-3 year commitment, 30-60% discount
3. **Spot instances** - Unused capacity, up to 90% discount
4. **Savings Plans** - Flexible commitment, 30-70% discount

## Decision

**Use EC2 Spot instances with "stop" interruption behavior.**

Configuration:
```hcl
# terraform/ec2.tf
instance_market_options {
  market_type = "spot"
  spot_options {
    max_price                      = "0.015"  # ~70% of on-demand
    spot_instance_type             = "persistent"
    instance_interruption_behavior = "stop"   # NOT terminate!
  }
}
```

## Consequences

### Pros
- **60-90% cost savings**: t3.small ~$4.50/month vs ~$15/month
- **Same performance**: Identical to on-demand instances
- **Data preserved**: "stop" behavior keeps EBS volume

### Cons
- **Interruption risk**: AWS can reclaim with 2-minute warning
- **Not guaranteed**: May not be available in all AZs
- **Slight complexity**: Must handle interruptions

### Interruption Handling

```
Spot Interruption (rare for t3.small):
1. AWS sends 2-minute warning
2. Instance STOPS (not terminates)
3. EBS volume preserved
4. Instance restarts when capacity available
5. Elastic IP re-attaches
6. Docker containers restart (restart: always)
```

**In practice**: t3.small interruptions are extremely rare (<1% monthly).

## Cost Comparison (eu-central-1)

| Instance | On-Demand | Spot | Savings |
|----------|-----------|------|---------|
| t3.micro | $9.50/mo | $2.85/mo | 70% |
| t3.small | $19.00/mo | $4.50/mo | 76% |
| t3.medium | $38.00/mo | $11.40/mo | 70% |

## Safety Measures

1. **Elastic IP**: Stable address survives restarts
2. **EBS volumes**: Data persists across stop/start
3. **Docker restart policy**: `restart: always`
4. **Spot type**: `persistent` (auto-restarts when capacity returns)
5. **Lifecycle ignore**: Terraform won't replace instance on AMI changes

```hcl
lifecycle {
  ignore_changes = [ami, user_data]
}
```

## When to Use On-Demand

Switch to On-Demand when:
- Running critical production with SLA requirements
- Instance type has high interruption rate (check Spot Advisor)
- Need guaranteed availability during specific time windows

## Monitoring Spot Status

```bash
# Check spot request status
aws ec2 describe-spot-instance-requests \
  --filters "Name=instance-id,Values=i-xxxxx"

# Check interruption history (CloudTrail)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=BidEvictedEvent
```

## References

- [AWS Spot Instances](https://aws.amazon.com/ec2/spot/)
- [Spot Instance Advisor](https://aws.amazon.com/ec2/spot/instance-advisor/)
- [Spot Interruption Handling](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html)


