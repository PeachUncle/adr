# ADR-007: Trading Features Implementation

## Revision Log
| Date | Description |
|------|-------------|
| 2025-12-11 | Document created |
| 2025-12-11 | Consolidated by ADR-005 |

## Part of: ADR-005 (Technology Stack Selection)

## Context
The Weight Stock Platform 2.0 requires comprehensive trading functionality including profit and loss tracking for buyers, balance management for sellers, real-time UI updates after transactions, and improved data visualization. The system needs to display realized and unrealized gains, manage monetary balances across user roles, and provide clear visual feedback for price trends versus moving averages.

## Decision
We implement four core trading features: (1) buyer P&L calculation using average cost method with separate realized and unrealized gains tracking, (2) seller balance system with automatic balance updates on buy/sell transactions, (3) TradeHistory component refresh mechanism using React state-based triggers, and (4) price chart UI enhancements with prominent price lines and subtle moving average indicators.

## Consequences

### Benefits
- Buyers can track investment performance with accurate P&L metrics
- Sellers maintain clear visibility of earnings and current balance
- Trade history updates immediately after transactions without manual refresh
- Chart visualizations prioritize price data with clear trend indicators
- Average cost method simplifies P&L calculations and tax reporting
- Balance system enforces transactional integrity across user roles
- React state-based refresh prevents stale data in UI components
- Enhanced chart styling improves data readability and user experience

### Tradeoffs
- Average cost method may not match specific lot identification for tax optimization
- P&L calculations add computational overhead to buyer dashboard loading
- Balance system requires careful transaction handling to prevent race conditions
- RefreshKey state management adds complexity to parent-child component communication
- Thicker price lines and styling increase chart rendering cost marginally
- Additional API endpoints increase backend surface area
- Frontend components become more tightly coupled to trading state

## Implementation
1. Add calculate_total_pnl() method to Buyer model with average cost calculation
2. Create GET /buyer/total-pnl API endpoint returning realized and unrealized P&L
3. Implement Balance model initialization in user registration flow
4. Add balance update logic in trade execution (buyer decrease/seller increase on buy, reverse on sell)
5. Create GET /seller/balance and GET /seller/earnings API endpoints
6. Add refreshKey state in parent component triggering TradeHistory re-render
7. Increment refreshKey after successful trade submission
8. Update PriceChart component with strokeWidth: 3 for price line and dashed MA lines
9. Enhance Tooltip styling with larger font and bold price display
10. Add row-level locking (with_for_update()) in recharge() method to prevent race conditions
11. Implement division-by-zero protection in calculate_total_pnl()

## Related Decisions
- **Depends on**: ADR-002 - Session-Based Authentication (trading requires authenticated user sessions)
- **Consolidated by**: ADR-005 - Technology Stack Selection

## Future Considerations
Evaluate implementing FIFO (First-In-First-Out) or specific lot identification methods if users require more sophisticated tax optimization. Consider WebSocket-based real-time updates for TradeHistory instead of state-triggered refresh for better scalability with high transaction volumes.

## Appendix: Buyer P&L Calculation

### Average Cost Method
```python
# backend/app/models/buyer.py
def calculate_total_pnl(self):
    """
    Calculate total P&L using average cost method.
    Returns dict with realized_pnl, unrealized_pnl, total_pnl.
    """
    from app.models.transaction import Transaction
    from app.models.price_record import PriceRecord
    from sqlalchemy import func

    # Get all buyer transactions (buy and sell)
    transactions = Transaction.query.filter_by(buyer_id=self.id).all()

    # Calculate average cost and current holdings
    total_quantity = 0
    total_cost = 0
    realized_pnl = 0

    for tx in transactions:
        if tx.transaction_type == 'buy':
            total_quantity += tx.quantity
            total_cost += tx.total_price
        elif tx.transaction_type == 'sell':
            # Calculate realized gain on this sale
            if total_quantity > 0:
                avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
                realized_pnl += (tx.price_per_unit - avg_cost) * tx.quantity

                # Update holdings
                total_quantity -= tx.quantity
                total_cost -= avg_cost * tx.quantity

    # Calculate unrealized P&L on remaining holdings
    unrealized_pnl = 0
    if total_quantity > 0:
        # Get latest market price
        latest_price_record = PriceRecord.query.filter_by(
            user_id=self.id
        ).order_by(PriceRecord.timestamp.desc()).first()

        if latest_price_record:
            current_value = latest_price_record.price * total_quantity
            avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
            unrealized_pnl = current_value - (avg_cost * total_quantity)

    return {
        'realized_pnl': round(realized_pnl, 2),
        'unrealized_pnl': round(unrealized_pnl, 2),
        'total_pnl': round(realized_pnl + unrealized_pnl, 2)
    }
```

### Buyer P&L API Endpoint
```python
# backend/app/routes/buyer.py
@buyer_bp.route('/total-pnl', methods=['GET'])
def get_total_pnl():
    """Get buyer's total profit and loss"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    buyer = Buyer.query.get(user_id)
    if not buyer:
        return jsonify({'error': 'Buyer not found'}), 404

    pnl_data = buyer.calculate_total_pnl()
    return jsonify(pnl_data), 200
```

### Frontend P&L Display
```typescript
// frontend/src/components/buyer/PnLCard.tsx
interface PnLData {
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
}

const PnLCard: React.FC = () => {
  const [pnlData, setPnlData] = useState<PnLData | null>(null);

  useEffect(() => {
    const fetchPnL = async () => {
      const response = await apiClient.get('/buyer/total-pnl');
      setPnlData(response.data);
    };
    fetchPnL();
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Profit & Loss</Typography>
        <Typography>Realized: ${pnlData?.realized_pnl}</Typography>
        <Typography>Unrealized: ${pnlData?.unrealized_pnl}</Typography>
        <Typography variant="h5">
          Total: ${pnlData?.total_pnl}
        </Typography>
      </CardContent>
    </Card>
  );
};
```

## Appendix: Seller Balance System

### Balance Model Initialization
```python
# backend/app/routes/auth.py
@auth_bp.route('/register', methods=['POST'])
def register():
    # ... user creation logic ...

    # Create balance record for all users
    from app.models.balance import Balance
    new_balance = Balance(user_id=new_user.id, balance=0.0)
    db.session.add(new_balance)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201
```

### Transaction Balance Updates
```python
# backend/app/routes/trade.py
@trade_bp.route('/execute', methods=['POST'])
def execute_trade():
    data = request.get_json()
    buyer_id = session.get('user_id')
    seller_id = data.get('seller_id')
    quantity = data.get('quantity')
    price = data.get('price')
    tx_type = data.get('type')  # 'buy' or 'sell'

    total_amount = quantity * price

    # Update balances based on transaction type
    buyer_balance = Balance.query.filter_by(user_id=buyer_id).first()
    seller_balance = Balance.query.filter_by(user_id=seller_id).first()

    if tx_type == 'buy':
        # Buyer pays, seller receives
        buyer_balance.balance -= total_amount
        seller_balance.balance += total_amount
    elif tx_type == 'sell':
        # Buyer receives, seller pays back
        buyer_balance.balance += total_amount
        seller_balance.balance -= total_amount

    db.session.commit()
    return jsonify({'status': 'success'}), 200
```

### Seller Balance API Endpoints
```python
# backend/app/routes/seller.py
@seller_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get seller's current balance"""
    user_id = session.get('user_id')
    balance = Balance.query.filter_by(user_id=user_id).first()
    return jsonify({'balance': balance.balance}), 200

@seller_bp.route('/earnings', methods=['GET'])
def get_earnings():
    """Calculate seller's total earnings from transactions"""
    user_id = session.get('user_id')

    # Sum all incoming payments (from buy transactions)
    buy_earnings = db.session.query(func.sum(Transaction.total_price)).filter(
        Transaction.seller_id == user_id,
        Transaction.transaction_type == 'buy'
    ).scalar() or 0

    return jsonify({'total_earnings': buy_earnings}), 200
```

## Appendix: TradeHistory Refresh Mechanism

### Parent Component RefreshKey State
```typescript
// frontend/src/pages/BuyerDashboard.tsx
const BuyerDashboard: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTradeSuccess = () => {
    // Increment refreshKey to trigger TradeHistory refresh
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div>
      <TradeForm onTradeSuccess={handleTradeSuccess} />
      <TradeHistory key={refreshKey} />
    </div>
  );
};
```

### TradeHistory Component
```typescript
// frontend/src/components/trade/TradeHistory.tsx
const TradeHistory: React.FC = () => {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    const fetchTrades = async () => {
      const response = await apiClient.get('/trade/history');
      setTrades(response.data);
    };
    fetchTrades();
  }, []); // Re-runs when component remounts due to key change

  return (
    <Table>
      {trades.map(trade => (
        <TableRow key={trade.id}>
          <TableCell>{trade.date}</TableCell>
          <TableCell>{trade.type}</TableCell>
          <TableCell>{trade.quantity}</TableCell>
        </TableRow>
      ))}
    </Table>
  );
};
```

## Appendix: Price Chart UI Enhancements

### Chart Configuration
```typescript
// frontend/src/components/chart/PriceChart.tsx
const chartOptions = {
  datasets: [
    {
      label: 'Price',
      data: priceData,
      borderColor: '#1976D2',      // Prominent blue
      borderWidth: 3,              // Thick line for visibility
      pointRadius: 4,
      pointBackgroundColor: '#1976D2',
      fill: false
    },
    {
      label: 'MA5',
      data: ma5Data,
      borderColor: 'rgba(255, 159, 64, 0.5)',  // Light orange
      borderWidth: 1.5,                         // Thin line
      borderDash: [5, 5],                       // Dashed pattern
      pointRadius: 0,                           // No points
      fill: false
    },
    {
      label: 'MA10',
      data: ma10Data,
      borderColor: 'rgba(75, 192, 192, 0.5)',  // Light teal
      borderWidth: 1.5,
      borderDash: [5, 5],
      pointRadius: 0,
      fill: false
    }
  ]
};
```

### Tooltip Styling
```typescript
// Chart.js tooltip configuration
const tooltipOptions = {
  callbacks: {
    label: function(context) {
      const label = context.dataset.label || '';
      const value = context.parsed.y;

      // Format price with larger font and bold
      if (label === 'Price') {
        return `Price: $${value.toFixed(2)}`;
      }
      return `${label}: $${value.toFixed(2)}`;
    }
  },
  bodyFont: {
    size: 14,
    weight: 'bold'  // Bold for price values
  }
};
```

## Appendix: Security Enhancements

### Race Condition Prevention in Recharge
```python
# backend/app/models/balance.py
from sqlalchemy import select

def recharge(self, amount):
    """
    Add funds to balance with row-level locking to prevent race conditions.
    """
    from app import db

    # Acquire row lock before updating
    balance = db.session.query(Balance).with_for_update().filter_by(
        user_id=self.user_id
    ).first()

    if not balance:
        raise ValueError(f"Balance record not found for user {self.user_id}")

    balance.balance += amount
    db.session.commit()

    return balance.balance
```

### Division-by-Zero Protection
```python
# backend/app/models/buyer.py (updated calculate_total_pnl)
def calculate_total_pnl(self):
    # ... transaction processing ...

    # Protect against division by zero
    avg_cost = total_cost / total_quantity if total_quantity > 0 else 0

    # Ensure valid calculation
    if total_quantity > 0 and latest_price_record:
        current_value = latest_price_record.price * total_quantity
        unrealized_pnl = current_value - (avg_cost * total_quantity)
    else:
        unrealized_pnl = 0  # No holdings, no unrealized P&L

    return {
        'realized_pnl': round(realized_pnl, 2),
        'unrealized_pnl': round(unrealized_pnl, 2),
        'total_pnl': round(realized_pnl + unrealized_pnl, 2)
    }
```

### Error Message Improvements
```python
# backend/app/routes/buyer.py
@buyer_bp.route('/total-pnl', methods=['GET'])
def get_total_pnl():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required. Please log in.'}), 401

    buyer = Buyer.query.get(user_id)
    if not buyer:
        return jsonify({'error': 'Buyer account not found. Please contact support.'}), 404

    try:
        pnl_data = buyer.calculate_total_pnl()
        return jsonify(pnl_data), 200
    except Exception as e:
        return jsonify({'error': f'Failed to calculate P&L: {str(e)}'}), 500
```
