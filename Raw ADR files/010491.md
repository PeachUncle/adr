# ADR 002: Product Recommendation Engine Architecture

## Status
Accepted

## Context
We need to recommend supplements to users based on their age (40-70+) and health concerns (Joints, Energy, Sleep, etc.). Without a dedicated backend, we need a lightweight, fast solution that can be hosted statically.

## Decision
We will implement a **Client-Side Recommendation Engine** powered by a static JSON product database.

1.  **Data Storage**: A `products.json` file (or TypeScript constant) containing the full catalog.
2.  **Schema**:
    ```typescript
    interface Product {
      id: string;
      name: string;
      brand: string;
      category: 'Joints' | 'Energy' | 'Sleep' | 'Immunity' | 'Multivitamin';
      targetAgeGroup: ('40-49' | '50-59' | '60-69' | '70+')[];
      healthConcerns: string[]; // e.g., ['knee pain', 'fatigue']
      affiliateLink: string;
      image: string;
      priceRange: '$' | '$$' | '$$$';
      rating: number;
    }
    ```
3.  **Matching Algorithm**:
    -   Input: User selects Age Group + Primary Health Concern.
    -   Process: Filter `products` where `targetAgeGroup` includes User Age AND `healthConcerns` includes User Concern.
    -   Ranking: Sort by `rating` (desc) or "Recommended" flag.

4.  **Affiliate Integration**:
    -   Links are stored directly in the product object.
    -   "Buy Now" button opens the `affiliateLink` in a new tab.

## Detailed Implementation
-   **State Management**: Use React Context or Zustand to hold the user's selection (Age, Concern).
-   **UI**: A multi-step wizard or a filterable grid view.
-   **Performance**: Since the catalog is small (<100 items initially), client-side filtering is instant and requires no API calls.

## Consequences
-   **Positive**: Zero latency, no backend costs, easy to maintain for small catalogs.
-   **Negative**: Not scalable to thousands of products (would need search index like Algolia later). Product data is exposed in client bundle (not an issue for public affiliate data).
