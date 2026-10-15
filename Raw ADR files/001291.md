# Stripe version

* Status: proposed
* Deciders: Alejandro Garcia Prada
* Date: 2025-11-06

## Context and Problem Statement

Given the type of system we are developing, one of the most essential modules is the payment module. To implement it, we will connect to Stripe through an API call. Therefore, we must choose which version of Stripe we will use and which pricing plan is the most suitable. We'll call to the latest API version (2025-10-29.clover).

## Decision Drivers

RF-10: Conectarse con pasarela de pago


## Considered Options

* 0012-1-Stripe-Payments(Stripe Checkout)
* 0012-1-Stripe-Payments (direct API)

## Decision Outcome

Chosen option: "0012-1-Stripe-Payments (Stripe Checkout)", because it is the simplest, cheapest, and safest way to integrate Stripe with minimal code and maintenance, while still supporting all required payment methods. Stripe Checkout has no monthly cost and only charges the standard transaction fees (e.g., 1.5% + 0.25€ for EU cards), making it the most cost-efficient choice.

### Positive Consequences

* Very low implementation complexity (a single API call (Checkout Session) handles the entire payment flow).
* Lowest operational cost, only the standard Stripe transaction fees apply.
* No need to build a payment form or handle card data.

### Negative Consequences
* Limited UI customization compared to a fully custom payment form.
* Flow depends on redirecting the user to Stripe’s hosted page (cannot embed the form natively without using the Payment Element).
* Advanced multi-step payment scenarios may require additional logic outside of Checkout.



## Pros and Cons of the Options

## 0012-1-Stripe-Payments(Stripe Checkout)

Stripe Checkout is a prebuilt, hosted payment page fully managed by Stripe. The application only needs to create a Checkout Session via API and redirect the user to Stripe. All security validations, 3D Secure, payment method selection, error handling, and form rendering are performed by Stripe. This produces the simplest and cheapest integration.

More info: https://stripe.com/es/pricing#standard-pricing

* Good, because it is the simplest integration path, requiring only one backend API call.
* Good, because it has no monthly fee; costs are identical to normal Stripe Payments (e.g., 1.5% + 0.25€ per EU card).
* Good, because it includes full security and compliance, reducing risk and maintenance.
* Good, because Stripe automatically keeps the UI updated, ensuring high conversion rates.
* Good, because it supports multiple payment methods (cards, SEPA, wallets, etc.) without extra implementation.
* Bad, because customization is limited compared to a custom payment form.
* Bad, because it requires redirecting the user to Stripe instead of keeping the payment flow fully embedded in the application.

## 0012-1-Stripe-Payments (direct API)

Direct Stripe Payments refers to using the full Stripe API without relying on the prebuilt Checkout interface. This would allows us to handle payments fully custom, embedding forms in our app or web, and controlling every step of the payment flow.

* Good, because it provides full control over the payment experience, allowing customizations that Checkout cannot support.
* Good, because it enables advanced automation, such as storing payment methods and handling complex recurring billing.
* Bad, because integration complexity increases, raising the risk of errors and compliance issues.
* Bad, because it requires more development and maintenance effort.
* Bad, because the learning curve is higher compared to Checkout, which can slow down initial delivery.



