# ADR-005: Reporting and Analytics Strategy

## Status
Accepted

## Context
Lead Tracker needs comprehensive reporting capabilities:
- Pipeline funnel analysis with conversion rates
- Sales performance metrics over time periods
- Lead source effectiveness tracking
- User activity and productivity reports
- Real-time dashboards for management oversight
- Export capabilities for external analysis

## Decision
We will implement a **hybrid approach** combining real-time queries with pre-calculated metrics:

### Architecture Components:
1. **Real-time queries** for current data and small datasets
2. **Pre-calculated aggregations** for historical trends and large datasets
3. **Background jobs** for metric calculation and caching
4. **Chart.js** for frontend data visualization
5. **Export services** for PDF/Excel report generation

### Report Types:

#### 1. Pipeline Funnel Report
```csharp
public class PipelineFunnelReport
{
    public class FunnelStage
    {
        public string StageName { get; set; }
        public int LeadCount { get; set; }
        public decimal TotalValue { get; set; }
        public decimal ConversionRate { get; set; } // From previous stage
        public decimal OverallConversionRate { get; set; } // From first stage
    }
    
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public List<FunnelStage> Stages { get; set; }
    public decimal TotalPipelineValue { get; set; }
    public int TotalLeads { get; set; }
}
```

#### 2. Sales Performance Report
```csharp
public class SalesPerformanceReport
{
    public class PeriodMetrics
    {
        public DateTime Period { get; set; }
        public int LeadsCreated { get; set; }
        public int DealsWon { get; set; }
        public int DealsLost { get; set; }
        public decimal Revenue { get; set; }
        public decimal AverageDealSize { get; set; }
        public int AverageSalesCycle { get; set; } // Days
    }
    
    public ReportPeriod PeriodType { get; set; } // Daily, Weekly, Monthly
    public List<PeriodMetrics> Periods { get; set; }
    public decimal TotalRevenue { get; set; }
    public int TotalDeals { get; set; }
}
```

#### 3. Lead Source Analysis
```csharp
public class LeadSourceReport
{
    public class SourceMetrics
    {
        public string SourceName { get; set; }
        public int LeadCount { get; set; }
        public int ConvertedCount { get; set; }
        public decimal ConversionRate { get; set; }
        public decimal Revenue { get; set; }
        public decimal CostPerLead { get; set; }
        public decimal ROI { get; set; }
    }
    
    public List<SourceMetrics> Sources { get; set; }
    public string BestPerformingSource { get; set; }
    public decimal OverallConversionRate { get; set; }
}
```

### Data Layer Implementation:

#### 1. Report Repository Pattern
```csharp
public interface IReportRepository
{
    Task<PipelineFunnelReport> GetPipelineFunnelAsync(Guid orgId, DateTime startDate, DateTime endDate);
    Task<SalesPerformanceReport> GetSalesPerformanceAsync(Guid orgId, ReportPeriod period, int periodCount);
    Task<LeadSourceReport> GetLeadSourceAnalysisAsync(Guid orgId, DateTime startDate, DateTime endDate);
}

public class ReportRepository : IReportRepository
{
    public async Task<PipelineFunnelReport> GetPipelineFunnelAsync(Guid orgId, DateTime startDate, DateTime endDate)
    {
        // Optimized query with proper indexing
        var query = from stage in _context.Stages
                   where stage.OrganizationId == orgId
                   orderby stage.Order
                   select new FunnelStage
                   {
                       StageName = stage.Name,
                       LeadCount = stage.Leads.Count(l => l.CreatedAt >= startDate && l.CreatedAt <= endDate),
                       TotalValue = stage.Leads.Where(l => l.CreatedAt >= startDate && l.CreatedAt <= endDate)
                                              .Sum(l => l.Value ?? 0)
                   };
        
        var stages = await query.ToListAsync();
        
        // Calculate conversion rates
        for (int i = 1; i < stages.Count; i++)
        {
            stages[i].ConversionRate = stages[i-1].LeadCount > 0 
                ? (decimal)stages[i].LeadCount / stages[i-1].LeadCount * 100 
                : 0;
        }
        
        return new PipelineFunnelReport { Stages = stages };
    }
}
```

#### 2. Cached Metrics for Performance
```csharp
public class MetricsCacheService
{
    private readonly IMemoryCache _cache;
    private readonly IReportRepository _reportRepository;
    
    public async Task<T> GetCachedReportAsync<T>(string cacheKey, Func<Task<T>> reportGenerator, TimeSpan? expiry = null)
    {
        if (_cache.TryGetValue(cacheKey, out T cachedReport))
        {
            return cachedReport;
        }
        
        var report = await reportGenerator();
        _cache.Set(cacheKey, report, expiry ?? TimeSpan.FromMinutes(15));
        return report;
    }
}
```

#### 3. Background Metric Calculation
```csharp
public class MetricsCalculationJob
{
    [RecurringJob("0 2 * * *")] // Daily at 2:00 AM
    public async Task CalculateDailyMetrics()
    {
        var organizations = await _context.Organizations.Where(o => o.IsActive).ToListAsync();
        
        foreach (var org in organizations)
        {
            // Calculate and cache key metrics
            await CalculateOrganizationMetrics(org.Id);
        }
    }
    
    private async Task CalculateOrganizationMetrics(Guid orgId)
    {
        var yesterday = DateTime.UtcNow.Date.AddDays(-1);
        
        // Pre-calculate common report data
        var dailyMetrics = new DailyMetrics
        {
            OrganizationId = orgId,
            Date = yesterday,
            LeadsCreated = await _context.Leads.CountAsync(l => l.OrganizationId == orgId && l.CreatedAt.Date == yesterday),
            DealsWon = await _context.Leads.CountAsync(l => l.OrganizationId == orgId && l.Status == LeadStatus.Won && l.UpdatedAt.Date == yesterday),
            Revenue = await _context.Leads.Where(l => l.OrganizationId == orgId && l.Status == LeadStatus.Won && l.UpdatedAt.Date == yesterday).SumAsync(l => l.Value ?? 0)
        };
        
        _context.DailyMetrics.Add(dailyMetrics);
        await _context.SaveChangesAsync();
    }
}
```

### Frontend Implementation:

#### 1. Chart Components
```typescript
// components/reports/PipelineFunnelChart.tsx
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface PipelineFunnelChartProps {
  data: FunnelStage[];
}

export function PipelineFunnelChart({ data }: PipelineFunnelChartProps) {
  const chartData = {
    labels: data.map(stage => stage.stageName),
    datasets: [
      {
        label: 'Number of Leads',
        data: data.map(stage => stage.leadCount),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        borderColor: 'rgba(53, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: 'Pipeline Value (€)',
        data: data.map(stage => stage.totalValue),
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        yAxisID: 'y1',
      }
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: true, text: 'Pipeline Funnel Analysis' },
    },
    scales: {
      y: { type: 'linear' as const, display: true, position: 'left' as const },
      y1: { type: 'linear' as const, display: true, position: 'right' as const, grid: { drawOnChartArea: false } },
    },
  };

  return <Bar data={chartData} options={options} />;
}
```

#### 2. Report Dashboard
```typescript
// pages/reports/dashboard.tsx
export default function ReportsDashboard() {
  const [dateRange, setDateRange] = useState({ start: subDays(new Date(), 30), end: new Date() });
  const [loading, setLoading] = useState(false);
  
  const { data: funnelData } = useSWR(
    `/api/reports/pipeline-funnel?start=${dateRange.start.toISOString()}&end=${dateRange.end.toISOString()}`,
    fetcher,
    { refreshInterval: 5 * 60 * 1000 } // Refresh every 5 minutes
  );
  
  const { data: salesData } = useSWR(
    `/api/reports/sales-performance?period=monthly&count=12`,
    fetcher
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reports Dashboard</h1>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Funnel</CardTitle>
          </CardHeader>
          <CardContent>
            {funnelData && <PipelineFunnelChart data={funnelData.stages} />}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Sales Performance</CardTitle>
          </CardHeader>
          <CardContent>
            {salesData && <SalesPerformanceChart data={salesData.periods} />}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### Export Functionality:

#### 1. PDF Export Service
```csharp
public class ReportExportService
{
    public async Task<byte[]> ExportToPdfAsync<T>(T report, string templateName)
    {
        var html = await RenderReportTemplate(report, templateName);
        return await GeneratePdfFromHtml(html);
    }
    
    public async Task<byte[]> ExportToExcelAsync<T>(T report)
    {
        using var workbook = new XLWorkbook();
        var worksheet = workbook.Worksheets.Add("Report");
        
        // Populate worksheet based on report type
        PopulateWorksheet(worksheet, report);
        
        using var stream = new MemoryStream();
        workbook.SaveAs(stream);
        return stream.ToArray();
    }
}
```

## Performance Optimizations

### 1. Database Indexes
```sql
-- Optimized indexes for reporting queries
CREATE INDEX idx_leads_org_created_status ON leads(organization_id, created_at, status);
CREATE INDEX idx_leads_org_updated_status ON leads(organization_id, updated_at, status);
CREATE INDEX idx_leads_org_stage_value ON leads(organization_id, stage_id, value);
```

### 2. Query Optimization
- Use projection to select only required fields
- Implement pagination for large result sets
- Use compiled queries for frequently executed reports
- Consider read replicas for heavy reporting workloads

### 3. Caching Strategy
- Cache report results for 15-30 minutes
- Use Redis for shared caching in production
- Implement cache invalidation on data changes
- Pre-generate common reports during off-peak hours

## Consequences

### Positive:
- **Performance**: Pre-calculated metrics for fast loading
- **Scalability**: Background processing doesn't block UI
- **Flexibility**: Multiple export formats
- **User Experience**: Interactive charts and real-time updates

### Negative:
- **Complexity**: Multiple data sources and caching layers
- **Storage**: Additional tables for pre-calculated metrics
- **Consistency**: Potential delays in metric updates

### Implementation Checklist:
- [ ] Create report repository interfaces and implementations
- [ ] Implement background jobs for metric calculation
- [ ] Build Chart.js components for data visualization
- [ ] Create export services for PDF/Excel
- [ ] Add caching layer for performance
- [ ] Optimize database queries and indexes
- [ ] Implement real-time dashboard updates
- [ ] Add report scheduling and email delivery
