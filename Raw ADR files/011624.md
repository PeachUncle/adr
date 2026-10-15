# **ADR: Row-Level Security Architecture and Auth User Mapping**

**Status:** Accepted
**Date:** 2025-01-xx
**Context:** Supabase application with three actor roles: `admin`, `focal_point`, and `farmer`.

---

## **1. Problem**

The application stores sensitive, farmer-linked survey data. Different users must only access data they are authorized to see. Supabase provides Row-Level Security (RLS), but effective RLS requires a stable and explicit way to link authenticated users to domain-level entities such as farmers and focal points.

Supabase Auth users may be created before or after rows appear in the `farmer` or `focal_point` tables. Emails and names are unreliable for identity linkage and cannot safely drive RLS.

We need:

* A consistent access model for all tables.
* A secure method for admins to assign roles and connect authenticated users to domain entities.
* A simple, maintainable RLS implementation that avoids ambiguity or accidental data exposure.

---

## **2. Decision**

### **2.1 Store `auth_user_id` inside domain tables**

Both `farmer` and `focal_point` tables now include a nullable column:

```
auth_user_id uuid references auth.users(id)
```

This column is populated when an authenticated user is linked to an existing farmer or focal point record. It becomes the authoritative identity key for RLS checks.

Benefits:

* Explicit and stable user–entity mapping.
* No reliance on email matching or external profile tables.
* Simplifies RLS logic to straightforward equality conditions.

---

### **2.2 Role-specific RLS policies**

#### **Admin**

Admins bypass RLS entirely.
This is implemented through a JWT claim (`role = 'admin'`) checked at the policy level.

#### **Farmer**

A farmer may only view or modify data belonging to themselves.
RLS conditions reference:

```
farmer.auth_user_id = auth.uid()
```

and, for all submission-derived tables:

```
submission.farmer_id in (
  select farmer_id from farmer
  where auth_user_id = auth.uid()
)
```

#### **Focal Point**

A focal point may view data for farmers assigned to them.
RLS conditions reference:

```
farmer.focal_point_id in (
  select focal_point_id from focal_point
  where auth_user_id = auth.uid()
)
```

and inherited relationships through submission tables.

#### **Reference Tables**

Lookup tables (crop, category, usage, season, application_method, etc) remain publicly readable to support client UI. Writes are restricted to admin and focal points.

---

### **2.3 RLS is enforced on all farmer-linked and submission-linked tables**

This includes:

* `farmer`
* `submission`
* `submission_crop`
* `yield_impact`
* `fertilizer_usage`
* `biochar_application`
* `biochar_application_method`
* `farmer_feedback`
* All junction tables that reference `submission_crop` or `submission`

Reference and configuration tables do not enforce row restrictions but do restrict writes.

---

## **3. Consequences**

### **Positive**

* Clear and predictable security boundaries.
* A single identity anchor (`auth_user_id`) eliminates ambiguity.
* All sensitive data is protected by RLS with minimal duplication of logic.
* Admin paths remain simple and unrestricted.
* The design scales with future surveys and data tables.

### **Negative**

* Domain rows cannot be associated with a user until `auth_user_id` is assigned.
* Admin tooling or UI is required to map new accounts to existing farmer or focal point rows.
* The architecture assumes one-to-one mapping between auth users and domain entities, which may need refinement if future workflows introduce shared or delegated accounts.