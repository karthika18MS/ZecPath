
from adapters.ats_adapter import ATSAdapter

print("\nTESTING ATS RESULT REUSE")
print("=" * 60)

adapter = ATSAdapter()

result = adapter.run(
    reuse_existing_results=True
)

print("\nRESULT REUSE TEST SUMMARY")
print("=" * 60)

print("Status:", result["status"])
print("Total Candidates:", result["total_candidates"])
print("ATS Completed:", result["completed"])
print("ATS Blocked:", result["blocked"])
print("ATS Errors:", result["errors"])
print("Results Reused:", result["results_reused"])
print("Pipelines Executed:", len(result["execution_log"]))

assert result["status"] == "SUCCESS"
assert result["results_reused"] is True
assert len(result["execution_log"]) == 0

print("\nRESULT REUSE TEST: PASSED")
