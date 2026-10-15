# ADR-001: Client-Side Price Calculation

## Revision Log
| Date | Description |
|------|-------------|
| 2025-12-10 | Document created |
| 2025-12-10 | Consolidated by ADR-005 |

## Part of: ADR-005 (Technology Stack Selection)

## Context
The PRD mandates that user weight data must not be transmitted to the server due to privacy concerns and data ownership principles. However, the system requires price calculations based on weight measurements for the stock platform functionality.

## Decision
We execute price calculation logic in the frontend WeightInput component. The backend receives only the final computed price value, never the raw weight data.

## Consequences

### Benefits
- User weight data has zero server-side exposure, ensuring complete privacy
- Backend computation load reduced by eliminating server-side price calculations
- Compliance with data minimization principle (GDPR-aligned architecture)
- Faster perceived performance as calculations happen locally without network round-trip

### Tradeoffs
- Frontend source code can be inspected, exposing the pricing algorithm publicly
- Backend cannot verify price calculation correctness or detect manipulation
- Price formula changes require frontend deployment
- Calculation logic must be maintained in JavaScript instead of backend language

## Implementation
1. Implement price calculation function in WeightInput React component
2. Configure component to accept weight input and pricing parameters
3. Execute calculation on user input change event
4. Transmit only computed price to backend API endpoint
5. Backend accepts price as opaque value without validation

## Related Decisions
- **Consolidated by**: ADR-005 - Technology Stack Selection

## Future Considerations
Consider implementing optional server-side verification using homomorphic encryption or secure multi-party computation if price integrity becomes critical business requirement.

## Appendix: Price Calculation Example

```javascript
// frontend/src/components/WeightInput.jsx
import React, { useState, useEffect } from 'react';

const WeightInput = ({ onPriceCalculated, pricingConfig }) => {
  const [weight, setWeight] = useState('');
  const [price, setPrice] = useState(null);

  useEffect(() => {
    if (weight && !isNaN(weight)) {
      // Price calculation logic - stays in frontend
      const calculatedPrice = calculatePrice(parseFloat(weight), pricingConfig);
      setPrice(calculatedPrice);
      onPriceCalculated(calculatedPrice); // Only price sent to parent
    }
  }, [weight, pricingConfig]);

  const calculatePrice = (weightValue, config) => {
    // Example pricing formula (business logic)
    const basePrice = config.basePrice || 10;
    const pricePerUnit = config.pricePerUnit || 2;
    return basePrice + (weightValue * pricePerUnit);
  };

  return (
    <div>
      <input
        type="number"
        value={weight}
        onChange={(e) => setWeight(e.target.value)}
        placeholder="Enter weight"
      />
      {price && <p>Calculated Price: ${price.toFixed(2)}</p>}
    </div>
  );
};

export default WeightInput;
```

## Appendix: Backend API Contract

```python
# backend/api/price_endpoint.py
from flask import Blueprint, request, jsonify
from flask_session import Session

price_bp = Blueprint('price', __name__)

@price_bp.route('/api/price/submit', methods=['POST'])
def submit_price():
    """
    Accept price calculation from frontend.
    Note: Weight data is never transmitted or stored.
    """
    data = request.get_json()

    # Backend receives only the final price
    price = data.get('price')

    if price is None:
        return jsonify({'error': 'Price is required'}), 400

    # Store price without weight information
    # No validation of calculation correctness
    user_id = session.get('user_id')
    save_price_record(user_id, price)

    return jsonify({'status': 'success', 'price': price}), 201

def save_price_record(user_id, price):
    # Database storage logic
    # Only price is persisted, weight never appears in database
    pass
```
