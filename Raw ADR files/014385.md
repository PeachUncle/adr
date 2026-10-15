## Context

The current implementation uses Stripe's legacy `CardElement` component, which only collects card details (number, expiry, CVC) and requires manual collection of billing address information including postal code. This creates a non-standard experience where users must enter postal code separately, which feels disconnected from typical Stripe integrations.

Stripe's `PaymentElement` is the modern, recommended approach that:

- Automatically collects billing address (including postal code) within the component
- Provides better 3D Secure support
- Offers a more unified, PCI-compliant payment experience
- Supports multiple payment methods (cards, wallets) if needed in the future

## Goals / Non-Goals

**Goals:**

- Migrate from CardElement to PaymentElement for better UX
- Automatically collect billing address including postal code
- Maintain existing shipping address collection flow (separate from billing)
- Improve 3D Secure authentication handling
- Align with Stripe's recommended best practices

**Non-Goals:**

- Not changing shipping address collection (remains in earlier step)
- Not adding support for additional payment methods beyond cards (future enhancement)
- Not changing payment intent creation logic significantly (mostly frontend change)

## Decisions

**Decision: Use PaymentElement instead of CardElement**

- **Rationale**: PaymentElement is Stripe's modern, recommended component that automatically handles billing address collection, provides better UX, and improves 3D Secure support.
- **Alternatives considered**:
  - Continue using CardElement with manual billing address fields - rejected because it creates non-standard UX
  - Use separate Stripe Address Element - rejected because PaymentElement integrates billing address more seamlessly

**Decision: Keep shipping address collection separate**

- **Rationale**: Shipping address is collected earlier in the order flow (before payment) and stored with the order. Billing address is only needed for payment processing and is collected via PaymentElement.
- **Alternatives considered**:
  - Collect billing address manually before payment - rejected because PaymentElement handles this automatically and more securely

**Decision: Use `confirmPayment` instead of `confirmCardPayment`**

- **Rationale**: PaymentElement requires `confirmPayment` method which supports PaymentElement instances. `confirmCardPayment` is specific to CardElement.
- **Alternatives considered**: None - this is required by PaymentElement API

## Risks / Trade-offs

**Risk: Breaking change for existing users**

- **Mitigation**: This is primarily a UI/UX change. Payment processing logic remains the same. Test thoroughly with test cards before deployment.

**Risk: Styling adjustments needed**

- **Mitigation**: PaymentElement has different default styling than CardElement. Review and adjust Tailwind classes as needed to maintain design consistency.

**Risk: Billing address data handling**

- **Mitigation**: Ensure billing address from PaymentElement is properly sent to Stripe with payment confirmation. Verify webhook handlers continue to work correctly.

## Migration Plan

1. **Frontend Changes**:

   - Update `CheckoutPage.jsx` to import and use `PaymentElement` instead of `CardElement`
   - Replace `confirmCardPayment` with `confirmPayment`
   - Remove any manual postal code/billing address form fields
   - Update form styling to accommodate PaymentElement

2. **Backend Verification**:

   - Verify payment intent creation supports PaymentElement (should work as-is)
   - Ensure webhook handlers process PaymentElement confirmations correctly
   - Test payment intent metadata is correctly stored

3. **Testing**:

   - Test with Stripe test cards (success, 3D Secure, decline scenarios)
   - Verify billing address is collected and sent correctly
   - Confirm shipping address remains separate and correct
   - Test error handling and retry flows

4. **Deployment**:
   - Deploy frontend changes
   - Monitor payment success rates
   - Verify no increase in payment failures

## Open Questions

- Should we pre-fill billing address with shipping address if available? (Consider UX vs. accuracy)
- Do we need to store billing address separately in our database, or is Stripe's record sufficient?
