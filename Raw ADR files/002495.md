---
date: { 2024-10-10 }
written-by: { Ayman Sammo }
decision-makers: { Ahmed Sulaimon, Ayman Sammo, Nayan Stanley }
---

# Hosting Platform

## Context and Problem Statement

- Where should the website be hosted?

## Considered Options

- [Digital Ocean (VPS)](#digital-ocean-vps)
- [Hostinger (Web Hosting)](#hostinger-web-hosting)
- [Hostinger (VPS)](#hostinger-vps)
- [Vercel (NextJS)](#vercel)

<!-- Look at cloud options AWS/Azure-->

## Decision Outcome

**Chosen option:** Digital Ocean (VPS)  
**Rationale:** This option offers the best balance of cost, scalability, and customization. [See below for pros and cons](#pros-cons).

### Consequences

- **Positive:** Affordable starting costs.
- **Positive:** Can be upgraded as needed.
- **Positive:** Highly customizable.
- **Positive:** Can host multiple websites on a single VPS.
- **Positive:** Supports web apps built in any language.
- **Negative:** Cannot be dynamically scaled as demand increases.
- **Negative:** Requires manual setup for SSL, HTTPS, and domain forwarding.

### Confirmation

<!-- Is this valid option for the project & why -->

<a name="pros-cons"></a>

## Pros and Cons of the Options

<a name="digital-ocean-vps"></a>

### Digital Ocean (VPS)

- **Pros:**
  - Very affordable starting cost (as low as $4).
  - Easily upgradable.
  - Highly customizable.
  - Can host multiple websites on a single VPS.
  - Supports various programming languages.
- **Cons:**
  - Cannot be dynamically scaled as demand increases.
  - Requires manual setup for SSL, HTTPS, and domain forwarding.

<a name="hostinger-web-hosting"></a>

### Hostinger (Web Hosting)

- **Pros:**
  - Easy to run PHP applications.
- **Cons:**
  - Short-term plans are expensive; only long-term plans (3-4 years) are cost-effective.
  - Primarily suited for PHP projects.

<a name="hostinger-vps"></a>

### Hostinger (VPS)

- **Pros:**
  - Easily upgradable.
  - Highly customizable.
  - Can host multiple websites on a single VPS.
  - Supports various programming languages.
- **Cons:**
  - Can be expensive for short-term use; long-term plans are more affordable.
  - Cannot be dynamically scaled as demand increases.
  - Requires manual setup for SSL, HTTPS, and domain forwarding.

<a name="vercel"></a>

### Vercel (Next.js)

- **Pros:**
  - Optimized for Next.js applications.
  - Allows database integration on a single platform.
  - Runs on edge servers, scaling automatically with demand.
  - Comes pre-configured with HTTPS and port forwarding.
- **Cons:**
  - Can become costly for high-traffic applications.
  - Best suited for Next.js applications only.

## More Information

<!-- How did the team come up with the decision -->
