# 2. Use freemium model for emergency notifications

Date: 2026-01-13

## Status

Accepted

## Context

The current MVP logs emergency notifications to console only. To make the app production-ready, we need actual delivery mechanisms for emergency alerts.

Notification delivery has real costs:
- SMS: $0.01-0.08 per message (varies by country)
- WhatsApp: $0.005-0.05 per message
- Email: ~$0.001 per message (negligible)
- Telegram: Free (Bot API)

We need a sustainable business model that covers operational costs while keeping the app accessible.

**Options considered:**

1. **Fully free** - Absorb all costs, no revenue
2. **Fully paid** - One-time purchase to use the app
3. **Subscription** - Monthly/yearly fee
4. **Freemium** - Free tier with paid upgrade for premium features

## Decision

We will implement a **freemium model** with rate limiting:

| Tier | Price | Notification Channels |
|------|-------|----------------------|
| Free | $0 | Email + Telegram |
| Premium | $1.99 (one-time) | Email + Telegram + SMS + WhatsApp |

**Key decisions:**

1. **Email + Telegram are free** - Both cost nothing to send, provides real value in free tier
2. **SMS + WhatsApp are premium** - These cost money per message, gated behind paywall
3. **One-time $1.99 payment** - Better margin than $0.99, still impulse-buy friendly
4. **Rate limiting** - Max 1 emergency per 7 days, max 3 contacts, prevents abuse

**Financial analysis:**
- Net revenue after Apple's 30% cut: ~$1.39
- Cost per premium emergency event: ~$0.12-0.18
- Break-even: 8-12 emergency events per user
- Rate limit ensures max ~52 events/year (realistically far fewer)

**Technical architecture:**

- Backend service (serverless) to handle notification dispatch
- SendGrid for email delivery
- Telegram Bot API (free) for Telegram
- Twilio for SMS and WhatsApp (premium only)
- StoreKit 2 for in-app purchases
- Rate limit tracking in UserDefaults + backend enforcement

## Consequences

### Positive

- **Sustainable revenue** - Premium purchases cover SMS/WhatsApp costs
- **Generous free tier** - Email + Telegram provides real value for $0
- **Better margin** - $1.99 vs $0.99 doubles profit per user
- **Rate limiting prevents abuse** - Controls cost exposure
- **Multiple channels increase delivery success** - If one fails, others work
- **No subscription fatigue** - Users pay once, own forever

### Negative

- **Backend complexity** - Need to build and maintain a notification service
- **Rate limiting may frustrate users** - Must communicate clearly in UI
- **Telegram setup requires extra steps** - Bot linking flow adds friction
- **WhatsApp Business API approval** - Requires business verification

### Risks

| Risk | Mitigation |
|------|------------|
| SMS costs exceed revenue | Rate limiting (1/week), $1.99 price |
| Low conversion rate | Free tier is genuinely useful, builds trust |
| Rate limit complaints | Email fallback always works, clear UI |
| Backend downtime | Use reliable serverless provider |

## References

- [PRD-002: Freemium Notification System](../PRD/PRD-002-freemium-notifications.md)
