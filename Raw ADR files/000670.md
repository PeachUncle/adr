# ADR-002: Apache Spark over Apache Flink

## Status

Accepted

## Context

We need a distributed processing framework for both stream and batch processing of auction data. The system must handle real-time bid validation and daily batch aggregations.

### Options Considered

1. **Apache Spark (Structured Streaming + Batch)**
2. **Apache Flink**
3. **AWS Glue (Spark-based)**

## Decision

We chose **Apache Spark** with Structured Streaming for the following reasons:

### Comparison Matrix

| Factor | Spark | Flink | Winner |
|--------|-------|-------|--------|
| Latency | ~100ms micro-batch | True streaming | Flink |
| Batch Processing | Excellent | Good | Spark |
| Python API (PySpark) | Mature, full-featured | PyFlink less mature | Spark |
| Community/Resources | Massive | Growing | Spark |
| Job Market Demand | Very High | High | Spark |
| AWS Integration | Native (EMR, Glue) | Kinesis Analytics | Spark |
| Learning Curve | Moderate | Steep | Spark |

### Key Reasons

1. **Portfolio Value**: Spark skills are more widely requested in job postings

2. **Unified API**: Same DataFrame API for both batch and streaming:
   ```python
   # Streaming
   df = spark.readStream.format("kafka")...
   
   # Batch
   df = spark.read.format("parquet")...
   ```

3. **Latency is Sufficient**: Auction systems can tolerate 100-500ms latency for most operations. True millisecond streaming (Flink's strength) isn't required.

4. **Python First**: PySpark is mature and well-documented; PyFlink is still catching up.

5. **Resource Availability**: More tutorials, Stack Overflow answers, and example code available for Spark.

### When We'd Choose Flink

- Sub-millisecond latency requirements
- Complex event processing (CEP) needs
- Exactly-once semantics critical
- Team already has Flink expertise

## Consequences

### Positive

- Strong portfolio differentiation
- Unified batch and stream codebase
- Excellent Python support
- Abundant learning resources

### Negative

- Higher latency than Flink (~100ms vs ~10ms)
- Micro-batch semantics vs true streaming
- Heavier resource footprint for small workloads

## Implementation Notes

```python
# Our streaming pattern
spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "auction.bids")
    .load()
    .writeStream
    .foreachBatch(process_batch)
    .start()
```

## References

- [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [Spark vs Flink Benchmark](https://www.datanami.com/2020/02/12/comparing-apache-spark-and-apache-flink/)
