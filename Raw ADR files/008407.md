---
status: accepted
date: 2025-05-18
decision-makers: [Manan Ahmad]
---
# Add to Cart Interaction 

---

## Context & Goals

We want to:

* let users add all the ingredients of a recipe to a *shopping list / cart* in one click;
* display that list in a dedicated **Shopping** page so they can tick items off at the store or jump to an online checkout;
* keep everything **client-side** (for now) to stay within our MVP scope and offline-friendly design.

The question is **how should we implement the Add-to-Cart flow and where should the data live?**

---

## Considered Options

| # | Option | Summary |
|:-:|--------|---------|
| 1 | **Inline “Buy ingredients” button → Local cart (LocalStorage)** | A button on each recipe card pushes that recipe’s ingredients into a cart array stored in `localStorage`. A separate `/shop` page reads that array and renders the list. |
| 2 | **Dedicated Shopping Page with Session-storage cart** | Same as (1) but cart lives in `sessionStorage` so it resets per browser session. |
| 3 | **Redirect to third-party grocery API (Instacart, Kroger, etc.)** | Clicking “Shop ingredients” opens an external service with the items pre-selected via URL parameters. No local cart. |
| 4 | **Hybrid: Local cart + affiliate links on /shop** | Use option 1 for state, but also show buttons that build affiliate URLs to partner grocery sites for potential revenue. |

---

## Decision Outcome

**Chosen option: 1 – Inline “Buy ingredients” button → Local cart (LocalStorage).**  
This is the smallest slice that delivers real value within our sprint scope and lets us iterate quickly.

*Why not option 3 alone?* It sacrifices the offline usefulness/chance to tick off items.  
*Why not option 2?* Losing persistence across sessions would annoy users.  
Option 4 is fine but might be troublesome/task-heavy being allowed to use affiliates and find for every ingredient.

---

## Consequences

* **Good** – Fastest time‑to‑feature; we can demo in the next sprint review.  
* **Good** – Minimal testing surface (just JSON round‑trip and simple UI).  
* **Good** – Supports offline grocery shopping (phone in airplane mode at the store).  
* **Bad** - No cross-device sync; users on a new device will see an empty cart.
* **Bad** - LocalStorage quota (5‑10 MB) could overflow in extreme cases (unlikely)
* **Trade-off** –  Future monetisation (affiliate links) or multi‑user sharing will require additional work later.

---

## Implementation Plan 

1. **Data model**

   ```ts
   type CartItem = { id: string; name: string; qty?: number; unit?: string };
   type Cart = CartItem[]; // stored as JSON
   // stored under localStorage['recipeCart'] 
  
 2. **cart.js module**
  * addRecipe(recipe) – merges recipe.ingredients into cart (no duplicates).
  * remove(id) / clear() / list() helpers.
  * dispatch a cart:update CustomEvent whenever the cart changes.
  
3. RecipeCard UI
  * Add <button class="buy-ingredients">Buy ingredients</button> inside each card; clicking calls Cart.addRecipe(thisRecipe).

4. Shopping Page (shop.html)
  * Read Cart.list() and render as an unordered list with check‑boxes.
  * Check‑box toggling simply hides the item (does not change storage)—keeps logic simple.
  * "Clear cart" button empties storage.
  
5. Testing
  * Jest unit tests for cart.js
  
6. Accessibility & Mobile polish
  * Ensure buttons have aria-label(for some use cases)
  * Use CSS overflow-y:auto so long lists scroll nicely on phone screens.
  ## References 
  * [Instacart Checkout](https://docs.instacart.com/storefront/learn_about_your_storefront/cart_and_checkout/checkout/)
  * [Spoontacular Extract](https://spoonacular.com/food-api/docs#Extract-Recipe-From-Website)
  
