# ADR-020 – QR Code Implementation: Activation-Time Generation with Cosmos DB Storage

**Status:** Accepted  
**Date:** 2025-12-03  
**Author:** Niklas Häll

---

## Context

The ticketing system requires QR code functionality for ticket validation during transportation boarding. QR codes need to be generated for activated tickets to enable scanning by inspectors. The system must balance performance (fast QR code retrieval), data efficiency (avoid unnecessary storage), and functionality (include validity period information in the QR code).

Key requirements:
- QR codes should only be generated when tickets are activated (not for unactivated tickets)
- QR codes must include validity period information (activation time, valid until) for validation
- QR codes should be stored in Cosmos DB for fast retrieval without regeneration
- QR codes should be easily accessible via UI for users to display during boarding

---

## Decision

We implement QR code generation **at activation time** with **storage in Cosmos DB** within the booking document. The QR code will be generated when a ticket is activated via the activation API endpoint, encoded with booking information and validity period, and stored as a base64-encoded image string in the booking document.

**Implementation Details:**
- **Library:** QRCoder NuGet package (popular .NET QR code library)
- **Generation Trigger:** QR code generated during ticket activation (`POST /api/bookings/{bookingId}/activate`)
- **Data Encoding:** JSON-encoded data containing:
  - Booking ID
  - Customer ID
  - Activation timestamp
  - Validity period (ValidFrom, ValidTo)
  - Status
- **Storage:** Base64-encoded PNG image stored in `Booking.QrCodeData` field in Cosmos DB
- **UI Display:** "Show QR Code" button appears for activated tickets, opens modal/popup with QR code image
- **Retrieval:** QR code loaded from Cosmos DB (no regeneration needed, instant display)

**Benefits:**
- **Instant Display:** QR code stored in database enables fast retrieval without regeneration
- **Data Efficiency:** QR codes only generated for activated tickets (not for all bookings)
- **Validity Information:** QR code includes validity period, enabling offline validation
- **Performance:** No computation needed on display (just retrieve and show)
- **Demo Value:** Immediate visual feedback for activated tickets

---

## Consequences

**Advantages:**
- **Fast Retrieval:** QR code stored in Cosmos DB enables instant display without regeneration
- **Data Efficiency:** Only activated tickets have QR codes, reducing unnecessary storage
- **Validity Embedded:** QR code contains validity period information for validation
- **Simple Implementation:** Generation happens at activation, storage is straightforward
- **Demo-Ready:** Immediate visual feedback enhances demo experience

**Disadvantages:**
- **Storage Cost:** Base64-encoded images increase booking document size (~2-5 KB per QR code)
- **No Regeneration:** If QR code format changes, existing QR codes remain in old format (requires migration)
- **Base64 Encoding:** Slightly larger storage than binary, but simpler for JSON serialization

**Trade-offs:**
- **Storage vs Performance:** Storing QR codes increases document size but enables instant display. For MVP, this trade-off is acceptable.
- **Generation Time:** Generating at activation adds minimal processing time (~50-100ms), but provides better user experience than on-demand generation.

---

## Risks / Mitigations

- **Risk:** QR code data increases Cosmos DB document size, potentially increasing storage costs.
  **Mitigation:** Monitor document sizes and storage costs. For MVP scale, the increase is minimal (~2-5 KB per activated ticket). If needed, can compress QR code images or use lower resolution.

- **Risk:** QR code format changes require migration of existing QR codes.
  **Mitigation:** QR code data format is versioned in the encoded JSON. Future changes can include version field and handle multiple formats during validation.

- **Risk:** Base64 encoding increases storage size compared to binary storage.
  **Mitigation:** For MVP scale, the size increase is acceptable. Cosmos DB handles base64 strings well in JSON documents. If storage becomes an issue, can migrate to binary storage in Azure Blob Storage.

- **Risk:** QR code generation adds processing time to activation endpoint.
  **Mitigation:** QRCoder library is fast (~50-100ms for generation). Activation is not a high-frequency operation, so the added latency is acceptable.

---

## Alternatives

- **Alternative 1: Generate on-demand (no storage)** – Generate QR code when requested via API endpoint.
  - **Rejected because:** Requires computation on every display, slower user experience, no validity information embedded in QR code without database lookup.

- **Alternative 2: Store QR code in separate container** – Store QR codes in separate Cosmos DB container or Azure Blob Storage.
  - **Rejected because:** Adds complexity (separate queries, additional storage account), slower retrieval (requires separate query), unnecessary for MVP scale.

- **Alternative 3: Generate QR code on frontend** – Generate QR code in browser using JavaScript library.
  - **Rejected because:** Requires embedding booking data in frontend (security concern), no validity information without API call, inconsistent with server-side architecture.

- **Alternative 4: Store QR code as binary in Cosmos DB** – Store QR code as binary attachment.
  - **Rejected because:** Cosmos DB doesn't support binary attachments natively, would require Azure Blob Storage integration, adds complexity for minimal benefit.

---

## Implementation Details

**QR Code Data Structure (JSON):**
```json
{
  "bookingId": "guid",
  "customerId": "guid",
  "activatedAt": "2025-12-03T10:00:00Z",
  "validFrom": "2025-12-03T10:00:00Z",
  "validTo": "2025-12-03T11:30:00Z",
  "status": "Activated",
  "version": "1.0"
}
```

**Booking Model Extension:**
- Add `QrCodeData` (string, nullable) field to `Booking` model
- Field populated during activation, null for unactivated tickets

**Files to Create:**
- `src/web/Ticketing.Web/Helpers/QrCodeHelper.cs` – QR code generation helper

**Files to Modify:**
- `src/shared/Ticketing.Contracts/Bookings/Booking.cs` – Add `QrCodeData` field
- `src/web/Ticketing.Web/Controllers/BookingsController.cs` – Generate QR code during activation
- `src/web/Ticketing.Web/Components/BookingTable.razor` – Add "Show QR Code" button and modal

**NuGet Package:**
- `QRCoder` (version 1.6.0 or later)

---

## References

- [QRCoder NuGet Package](https://www.nuget.org/packages/QRCoder/)
- [Week 6 Action Plan - QR Code Generation](../journal/week_six_action_plan.md#32-qr-code-generation)
- [Ticket Activation Implementation](../journal/week_six.md#ticket-activation-timer-implementation-steps-1-3-complete)

