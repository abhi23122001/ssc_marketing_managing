# scripts/compile_final_evidence.py
import json
import csv
import os
from datetime import datetime

base_dir = r"C:\Users\HP\Desktop\ssc_marketing_managing"

backend_results_path = os.path.join(base_dir, "scripts", "final_master_acceptance_results.json")
browser_results_path = os.path.join(base_dir, "scripts", "final_browser_evidence.json")

with open(backend_results_path, "r", encoding="utf-8") as f:
    backend_data = json.load(f)

with open(browser_results_path, "r", encoding="utf-8") as f:
    browser_data = json.load(f)

# Combine into master matrix
matrix_rows = []

# Backend tests
for idx, test in enumerate(backend_data["tests"], 1):
    matrix_rows.append({
        "Test_ID": f"BE-TEST-{idx:02d}",
        "Category": "Backend / API / Security",
        "Test_Name": test["name"],
        "Execution_Type": "Automated Python / HTTP API",
        "Expected_Result": "Success / Validated State",
        "Actual_Result": test.get("details", "Passed"),
        "Status": "PASSED" if test["passed"] else "FAILED"
    })

# Browser tests
for idx, step in enumerate(browser_data["sections_audited"], 1):
    matrix_rows.append({
        "Test_ID": f"FE-CDP-{idx:02d}",
        "Category": "Frontend / Browser CDP / DOM",
        "Test_Name": step["step"],
        "Execution_Type": "Headless Chrome CDP Automation",
        "Expected_Result": "Rendered & Functional / Zero Errors",
        "Actual_Result": json.dumps(step.get("details", {})),
        "Status": "PASSED" if step["passed"] else "FAILED"
    })

# Add Browser Console Integrity
matrix_rows.append({
    "Test_ID": "FE-CDP-08",
    "Category": "Frontend / Console Integrity",
    "Test_Name": "Zero Console Errors and Zero Page Exceptions",
    "Execution_Type": "Headless Chrome CDP Event Stream",
    "Expected_Result": "0 console errors, 0 page exceptions",
    "Actual_Result": f"{len(browser_data['console_errors'])} errors, {len(browser_data['page_exceptions'])} exceptions",
    "Status": "PASSED" if browser_data["status"] == "PASSED_ZERO_ERRORS" else "FAILED"
})

# Write CSV matrix
csv_path = os.path.join(base_dir, "SHAH_GROUP_FINAL_ACCEPTANCE_TEST_MATRIX.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Test_ID", "Category", "Test_Name", "Execution_Type", "Expected_Result", "Actual_Result", "Status"])
    writer.writeheader()
    writer.writerows(matrix_rows)

print(f"Matrix CSV saved: {csv_path} with {len(matrix_rows)} items")

# Compile complete evidence JSON
final_evidence = {
    "project": "SHAH GROUP AI OS",
    "version": "1.0.0-production-handover",
    "generated_at": datetime.now().isoformat(),
    "base_url": "http://127.0.0.1:8899/",
    "baseline_git_commit": "1b6c3ee",
    "rollback_git_commit": "bb32adc",
    "backup_path": r"C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123",
    "summary": {
        "total_tests": len(matrix_rows),
        "passed_tests": sum(1 for r in matrix_rows if r["Status"] == "PASSED"),
        "failed_tests": sum(1 for r in matrix_rows if r["Status"] == "FAILED"),
        "success_rate": f"{(sum(1 for r in matrix_rows if r['Status'] == 'PASSED') / len(matrix_rows)) * 100:.1f}%",
        "backend_tests_count": len(backend_data["tests"]),
        "browser_steps_count": len(browser_data["sections_audited"]) + 1,
        "browser_console_errors": len(browser_data["console_errors"]),
        "browser_page_exceptions": len(browser_data["page_exceptions"])
    },
    "backend_results": backend_data,
    "browser_results": browser_data,
    "test_matrix": matrix_rows
}

evidence_path = os.path.join(base_dir, "SHAH_GROUP_FINAL_EVIDENCE.json")
with open(evidence_path, "w", encoding="utf-8") as f:
    json.dump(final_evidence, f, indent=2)

print(f"Evidence JSON saved: {evidence_path}")
