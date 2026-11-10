# ZecPath Day 56 - System Performance Analysis

- Candidate ID: candidate_006
- Target role: Backend Developer
- Generated UTC: 2026-10-13T09:31:57.214733+00:00

## 1. Performance Summary

- Total recorded execution time: 53.0720 seconds
- Timing source: End-to-end report summary
- Sum of stage timings: 53.0457 seconds
- Number of stages measured: 12
- Average stage time: 4.4205 seconds
- Failed stages: 0
- Combined share of two slowest stages: 97.38%

## 2. Stage-by-Stage Performance

| Stage | Process Time (s) | Internal Batch Time (s) | Internal Total Elapsed (s) | Model Load (s) | Share of Stage Time | Status |
|---|---:|---:|---:|---:|---:|---|
| Day 18 optimized ATS batch | 25.9294 | 3.1666 | N/A | 10.4200 | 48.88% | PASS |
| Optimized semantic matching batch | 25.7279 | N/A | 13.5900 | 9.5100 | 48.50% | PASS |
| Resume extraction and input validation | 0.4033 | N/A | N/A | N/A | 0.76% | PASS |
| Day 21 eligibility engine | 0.2341 | N/A | N/A | N/A | 0.44% | PASS |
| Day 41 cross-round scoring | 0.1044 | N/A | N/A | N/A | 0.20% | PASS |
| Experience matching | 0.0993 | N/A | N/A | N/A | 0.19% | PASS |
| Day 38 logical reasoning - demonstration data | 0.0989 | N/A | N/A | N/A | 0.19% | PASS |
| Day 37 HR interview scoring - demonstration data | 0.0966 | N/A | N/A | N/A | 0.18% | PASS |
| Education matching | 0.0914 | N/A | N/A | N/A | 0.17% | PASS |
| Final ATS scoring | 0.0893 | N/A | N/A | N/A | 0.17% | PASS |
| Skill matching | 0.0883 | N/A | N/A | N/A | 0.17% | PASS |
| Day 38 scenario evaluation - demonstration data | 0.0828 | N/A | N/A | N/A | 0.16% | PASS |

## 3. Slow Stages

Stages taking five seconds or more are flagged for further investigation.

- **Day 18 optimized ATS batch**: 25.9294 seconds (48.88% of stage time).
- **Optimized semantic matching batch**: 25.7279 seconds (48.50% of stage time).

## 4. Five Slowest Stages

1. **Day 18 optimized ATS batch** - 25.9294 seconds.
2. **Optimized semantic matching batch** - 25.7279 seconds.
3. **Resume extraction and input validation** - 0.4033 seconds.
4. **Day 21 eligibility engine** - 0.2341 seconds.
5. **Day 41 cross-round scoring** - 0.1044 seconds.

## 5. Performance Recommendations

- Investigate 'Day 18 optimized ATS batch', which took 25.9294 seconds. Profile model initialization, inference, file access, and external calls before making changes.
- For the optimized ATS batch, compare process startup time with actual batch-processing time. Measure per-candidate latency separately.
- For semantic matching, measure model loading and inference separately. Reuse the loaded model where appropriate instead of initializing it for each task.
- For the optimized ATS batch, compare process startup time with actual batch-processing time. Measure per-candidate latency separately.
- Repeat the test several times under consistent conditions and calculate minimum, average, and maximum execution times.
- Compare runs using equivalent inputs, hardware, model versions, and cache conditions.
- Measure complete workflow time separately from individual stage timings because their totals may differ.
- Treat these timings as performance observations, not evidence of hiring accuracy or model fairness.

## 6. Limitations

- This report analyzes one recorded test run.
- Stage timings may vary due to model loading, caching, network activity, and system conditions.
- Stages taking five seconds or more are flagged for investigation, not automatically classified as failures.
- Performance timing does not establish AI assessment accuracy.
- Repeated controlled runs are required for reliable benchmarks.

## 7. Conclusion

The analyzer evaluated the recorded execution times and identified stages for further performance investigation. The measurements describe the supplied test run only. Repeated controlled tests are needed before drawing general performance conclusions.
