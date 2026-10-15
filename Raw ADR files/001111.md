# ADR-003: Server-Side Moving Average Calculation

## Revision Log
| Date | Description |
|------|-------------|
| 2025-12-10 | Document created |
| 2025-12-10 | Consolidated by ADR-005 |

## Part of: ADR-005 (Technology Stack Selection)

## Context
Chart visualizations require moving averages (MA5, MA10, MA20, MA50) to display price trends. As the time range increases, calculation complexity grows proportionally, potentially impacting frontend performance and user experience.

## Decision
We pre-compute moving averages in the backend using pandas before returning chart data. API responses include both raw price data and calculated moving average series.

## Consequences

### Benefits
- Pandas provides highly optimized time-series calculation performance
- Frontend focuses purely on rendering without computational overhead
- Consistent calculation logic centralized in one location
- Leverages backend computational resources instead of client device
- Enables server-side caching of calculated results

### Tradeoffs
- Backend computational load increases with each chart data request
- API response payload size grows with additional moving average data
- Backend must handle time-series calculation logic
- Changes to moving average parameters require backend deployment
- Increased memory usage on server for pandas operations

## Implementation
1. Install pandas in backend Python environment
2. Implement moving average calculation function using pandas rolling window
3. Create API endpoint accepting time range and MA period parameters
4. Query price data from database within specified time range
5. Calculate MA5, MA10, MA20, MA50 using pandas DataFrame operations
6. Return JSON response with raw prices and moving average series
7. Frontend chart library consumes pre-calculated data for rendering

## Related Decisions
- **Consolidated by**: ADR-005 - Technology Stack Selection

## Future Considerations
Implement server-side caching (Redis) for frequently requested time ranges to reduce redundant calculations and improve API response times.

## Appendix: Pandas Moving Average Calculation

```python
# backend/services/chart_service.py
import pandas as pd
from datetime import datetime, timedelta
from models import PriceRecord

def calculate_moving_averages(user_id, start_date, end_date, periods=[5, 10, 20, 50]):
    """
    Calculate moving averages for price data using pandas.

    Args:
        user_id: User identifier
        start_date: Start of time range (datetime)
        end_date: End of time range (datetime)
        periods: List of MA periods to calculate

    Returns:
        dict: Contains raw prices and moving averages
    """
    # Query price records from database
    price_records = PriceRecord.query.filter(
        PriceRecord.user_id == user_id,
        PriceRecord.timestamp >= start_date,
        PriceRecord.timestamp <= end_date
    ).order_by(PriceRecord.timestamp).all()

    # Convert to pandas DataFrame
    df = pd.DataFrame([
        {
            'timestamp': record.timestamp,
            'price': record.price
        }
        for record in price_records
    ])

    if df.empty:
        return {'prices': [], 'moving_averages': {}}

    # Calculate moving averages for each period
    moving_averages = {}
    for period in periods:
        ma_key = f'MA{period}'
        df[ma_key] = df['price'].rolling(window=period, min_periods=1).mean()
        moving_averages[ma_key] = df[['timestamp', ma_key]].to_dict('records')

    # Prepare response
    result = {
        'prices': df[['timestamp', 'price']].to_dict('records'),
        'moving_averages': moving_averages
    }

    return result
```

## Appendix: Chart Data API Endpoint

```python
# backend/api/chart.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from services.chart_service import calculate_moving_averages

chart_bp = Blueprint('chart', __name__)

@chart_bp.route('/api/chart/data', methods=['GET'])
def get_chart_data():
    """
    Retrieve price data with pre-calculated moving averages.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    user_id = session['user_id']

    # Parse query parameters
    days = request.args.get('days', default=30, type=int)
    ma_periods = request.args.get('periods', default='5,10,20,50', type=str)

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Parse MA periods
    periods = [int(p.strip()) for p in ma_periods.split(',')]

    # Calculate moving averages
    chart_data = calculate_moving_averages(user_id, start_date, end_date, periods)

    return jsonify({
        'status': 'success',
        'data': chart_data,
        'range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days
        }
    }), 200
```

## Appendix: Frontend Chart Integration

```javascript
// frontend/src/components/PriceChart.jsx
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

const PriceChart = ({ days = 30 }) => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const response = await axios.get('/api/chart/data', {
          params: {
            days: days,
            periods: '5,10,20,50'
          },
          withCredentials: true
        });

        const data = response.data.data;

        // Format data for chart library
        // Backend has already calculated moving averages
        const chartConfig = {
          labels: data.prices.map(p => new Date(p.timestamp).toLocaleDateString()),
          datasets: [
            {
              label: 'Price',
              data: data.prices.map(p => p.price),
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1
            },
            {
              label: 'MA5',
              data: data.moving_averages.MA5.map(m => m.MA5),
              borderColor: 'rgba(255, 99, 132, 0.5)',
              tension: 0.1
            },
            {
              label: 'MA10',
              data: data.moving_averages.MA10.map(m => m.MA10),
              borderColor: 'rgba(54, 162, 235, 0.5)',
              tension: 0.1
            },
            {
              label: 'MA20',
              data: data.moving_averages.MA20.map(m => m.MA20),
              borderColor: 'rgba(255, 206, 86, 0.5)',
              tension: 0.1
            },
            {
              label: 'MA50',
              data: data.moving_averages.MA50.map(m => m.MA50),
              borderColor: 'rgba(153, 102, 255, 0.5)',
              tension: 0.1
            }
          ]
        };

        setChartData(chartConfig);
      } catch (error) {
        console.error('Failed to fetch chart data:', error);
      }
    };

    fetchChartData();
  }, [days]);

  if (!chartData) {
    return <div>Loading chart...</div>;
  }

  return <Line data={chartData} />;
};

export default PriceChart;
```
