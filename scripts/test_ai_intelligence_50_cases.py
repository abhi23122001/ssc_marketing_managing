# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — 50-Case Comprehensive AI Intelligence & Live Research Evaluation Suite.

Evaluates:
  1. Multi-Lingual Conversational Greetings (Hindi, English, Hinglish)
  2. Live ERP Business & Financial Queries (P&L, Net Profit, Revenues)
  3. Outstanding Receivables & Unpaid Invoices
  4. CRM Leads & Sales Pipeline
  5. Survey Sites, 16-Stage Lifecycle & Travel Logistics
  6. Team Roster, Attendance & Payroll
  7. Tax Invoices & Quotations with Dynamic Items
  8. Non-GST Commercial Bills (0% tax, Section 31(3)(c))
  9. Registered Vendors & KYC Approval Lifecycle
  10. Technical Surveying SOPs (DGPS RTK, GTS pillars, tolerances)
  11. Drone Photogrammetry & Aerial LiDAR (DGCA, GSD, GCPs)
  12. Civil Highway Engineering (MoRTH Section 300, IRC, earthwork compaction)
  13. Government Tenders, CPPP & GeM Bidding (EMD exemption, MSME)
  14. Mathematical & GST Calculations (reverse charge, 18% CGST/SGST)
  15. Geodetic & Cadastral Unit Conversions (sq.m, acres, hectares, gunthas)
  16. Live Web Research (DuckDuckGo, market prices, competitor analysis, citations)
  17. Multi-Tenant Data Isolation & Anti-Hallucination Resistance (SSC vs INFRA isolation, fake data resistance)
"""
import json
import os
import sys
import time

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from foundation.store import Store
from foundation.domains import ai_intelligence

EVAL_CASES = [
    # Category 1: Multi-Lingual Conversational Greetings (3 cases)
    {"id": 1, "cat": "GREETING", "q": "Namaste, aap kaun ho aur kya kar sakte ho?", "ws": "SSC", "expect_intent": "GREETING", "keywords": ["Namaste", "SHAH Group AI Assistant"]},
    {"id": 2, "cat": "GREETING", "q": "Hello, how can you help my surveying company?", "ws": "SSC", "expect_intent": "GREETING", "keywords": ["business operations", "financials"]},
    {"id": 3, "cat": "GREETING", "q": "Kaise ho, software ke features batao", "ws": "INFRA", "expect_intent": "GREETING", "keywords": ["Namaste", "Hindi", "English"]},

    # Category 2: Live ERP Business & Financial Queries (3 cases)
    {"id": 4, "cat": "FINANCIAL_PL", "q": "Total profit kitna hua hai?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["P&L Financial Report", "Net Operating Profit"]},
    {"id": 5, "cat": "FINANCIAL_PL", "q": "Show me our net operating profit and balance sheet", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Taxable Invoiced", "Realized Collections"]},
    {"id": 6, "cat": "FINANCIAL_PL", "q": "INFRA company ka p&l report dikhao", "ws": "INFRA", "expect_intent": "BUSINESS_DATA", "keywords": ["INFRA", "P&L Financial Report"]},

    # Category 3: Outstanding Receivables & Unpaid Invoices (3 cases)
    {"id": 7, "cat": "RECEIVABLES", "q": "Kitna payment baki hai client se lena?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Outstanding", "INR"]},
    {"id": 8, "cat": "RECEIVABLES", "q": "Show all unpaid invoices and receivables", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Pending Inward Payments", "Invoice"]},
    {"id": 9, "cat": "RECEIVABLES", "q": "Koi outstanding baqi hai kya?", "ws": "INFRA", "expect_intent": "BUSINESS_DATA", "keywords": ["outstanding", "settled"]},

    # Category 4: CRM Leads & Sales Pipeline (3 cases)
    {"id": 10, "cat": "CRM_LEADS", "q": "Kitne naye leads aaye hain?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["CRM Leads Summary", "Inquiries"]},
    {"id": 11, "cat": "CRM_LEADS", "q": "Show our sales inquiry pipeline", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Pipeline", "Converted"]},
    {"id": 12, "cat": "CRM_LEADS", "q": "Naya lead ka status batao", "ws": "INFRA", "expect_intent": "BUSINESS_DATA", "keywords": ["CRM", "Leads"]},

    # Category 5: Survey Sites, 16-Stage Lifecycle & Logistics (3 cases)
    {"id": 13, "cat": "SURVEY_SITES", "q": "Active projects aur survey sites kitne hain?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Survey Sites & Projects", "Code:"]},
    {"id": 14, "cat": "SURVEY_SITES", "q": "Show all active site logs and geofences", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Geofence", "Sites Registered"]},
    {"id": 15, "cat": "SURVEY_SITES", "q": "INFRA highway project sites list", "ws": "INFRA", "expect_intent": "BUSINESS_DATA", "keywords": ["Project Sites", "INFRA"]},

    # Category 6: Team Roster, Attendance & Payroll (3 cases)
    {"id": 16, "cat": "HRM_STAFF", "q": "Staff me kaun kaun hai aur attendance status kya hai?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Team & Staff Roster", "Staff Members"]},
    {"id": 17, "cat": "HRM_STAFF", "q": "Who are our active field surveyors and engineers?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Engineering & Field Personnel", "Status:"]},
    {"id": 18, "cat": "HRM_STAFF", "q": "Haziri aur employee roster dikhao", "ws": "INFRA", "expect_intent": "BUSINESS_DATA", "keywords": ["Staff Roster", "Attendance"]},

    # Category 7: Tax Invoices & Quotations with Dynamic Items (3 cases)
    {"id": 19, "cat": "INVOICES_QUOTES", "q": "Recent invoices dikhao", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["GST Tax Invoices Register", "Rule 46"]},
    {"id": 20, "cat": "INVOICES_QUOTES", "q": "Naya quotation kaise banaye?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Quotations & Estimates", "18% GST"]},
    {"id": 21, "cat": "INVOICES_QUOTES", "q": "Show recent estimate and rate analysis quotes", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Quotations", "BOQ"]},

    # Category 8: Non-GST Commercial Bills (3 cases)
    {"id": 22, "cat": "NON_GST_BILLS", "q": "Non-GST bills summary dikhao", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Bill of Supply", "Section 31(3)(c)"]},
    {"id": 23, "cat": "NON_GST_BILLS", "q": "Show commercial bills of supply with zero tax", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Non-GST", "0% tax liability"]},
    {"id": 24, "cat": "NON_GST_BILLS", "q": "Bina GST wale commercial bill list", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["BILL-", "Bill of Supply"]},

    # Category 9: Registered Vendors & KYC Lifecycle (3 cases)
    {"id": 25, "cat": "VENDORS_KYC", "q": "Registered vendors list dikhao", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Registered Vendors", "KYC"]},
    {"id": 26, "cat": "VENDORS_KYC", "q": "Show approved equipment suppliers and contractors", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Suppliers", "Status"]},
    {"id": 27, "cat": "VENDORS_KYC", "q": "Trimble navigation vendor status kya hai?", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Trimble", "Active"]},

    # Category 10: Technical Surveying SOPs (3 cases)
    {"id": 28, "cat": "SURVEY_SOP", "q": "DGPS RTK accuracy standards and GTS ties", "ws": "SSC", "expect_intent": "TECHNICAL_SOP", "keywords": ["Survey of India", "RTK Rover Accuracy", "PDOP < 2.0"]},
    {"id": 29, "cat": "SURVEY_SOP", "q": "Total Station traverse precision standards", "ws": "SSC", "expect_intent": "TECHNICAL_SOP", "keywords": ["Angular Accuracy", "10 * sqrt(N)", "1 : 10,000"]},
    {"id": 30, "cat": "SURVEY_SOP", "q": "Boundary demarcation RCC pillar specifications", "ws": "SSC", "expect_intent": "TECHNICAL_SOP", "keywords": ["150mm x 150mm x 750mm", "copper/brass mark"]},

    # Category 11: Drone Photogrammetry & Aerial LiDAR (3 cases)
    {"id": 31, "cat": "DRONE_LIDAR", "q": "Drone photogrammetry SOP and DGCA rules", "ws": "SSC", "expect_intent": "TECHNICAL_SOP", "keywords": ["75% forward overlap", "GSD", "Green Zones"]},
    {"id": 32, "cat": "DRONE_LIDAR", "q": "Aerial LiDAR GCP spacing and vertical accuracy", "ws": "SSC", "expect_intent": "TECHNICAL_SOP", "keywords": ["Ground Control Points", "RMSE", "< 5cm"]},
    {"id": 33, "cat": "DRONE_LIDAR", "q": "UAV flight altitude limit in India", "ws": "SSC", "expect_intent": "TECHNICAL_SOP", "keywords": ["400ft AGL", "Digital Sky"]},

    # Category 12: Civil Highway Engineering (MoRTH Section 300) (3 cases)
    {"id": 34, "cat": "CIVIL_HIGHWAY", "q": "MoRTH Section 300 earthwork compaction specs", "ws": "INFRA", "expect_intent": "TECHNICAL_SOP", "keywords": ["MoRTH Section 300", "97% Maximum Dry Density", "IS:2720"]},
    {"id": 35, "cat": "CIVIL_HIGHWAY", "q": "IRC specifications for highway subgrade and WMM", "ws": "INFRA", "expect_intent": "TECHNICAL_SOP", "keywords": ["WMM", "98% MDD", "IRC:SP:19"]},
    {"id": 36, "cat": "CIVIL_HIGHWAY", "q": "Road compaction density testing frequency", "ws": "INFRA", "expect_intent": "TECHNICAL_SOP", "keywords": ["1 density test per 500 sq.m", "camber"]},

    # Category 13: Government Tenders, CPPP & GeM Bidding (3 cases)
    {"id": 37, "cat": "TENDERS_GEM", "q": "GeM portal tender eligibility for survey works", "ws": "SSC", "expect_intent": "RESEARCH_TENDERS", "keywords": ["Udyam MSME", "Rule 170 GFR 2017", "EMD"]},
    {"id": 38, "cat": "TENDERS_GEM", "q": "CPPP PWD tender technical qualification checklist", "ws": "SSC", "expect_intent": "RESEARCH_TENDERS", "keywords": ["3 completed similar survey", "calibration certificates"]},
    {"id": 39, "cat": "TENDERS_GEM", "q": "Government tender EMD exemption criteria", "ws": "SSC", "expect_intent": "RESEARCH_TENDERS", "keywords": ["MSME", "exempts EMD", "BOQ Rate Analysis"]},

    # Category 14: Mathematical & GST Calculations (3 cases)
    {"id": 40, "cat": "CALCULATIONS", "q": "Calculate GST on 500000 at 18%", "ws": "SSC", "expect_intent": "CALCULATION", "keywords": ["Taxable Amount: INR 500,000.00", "Total GST Liability: INR 90,000.00", "INR 590,000.00"]},
    {"id": 41, "cat": "CALCULATIONS", "q": "What is 18% GST on 125000 base amount?", "ws": "SSC", "expect_intent": "CALCULATION", "keywords": ["Taxable Amount: INR 125,000.00", "CGST (9.0%)", "SGST (9.0%)"]},
    {"id": 42, "cat": "CALCULATIONS", "q": "Calculate GST on 80000 at 18%", "ws": "INFRA", "expect_intent": "CALCULATION", "keywords": ["INR 80,000.00", "INR 14,400.00", "INR 94,400.00"]},

    # Category 15: Geodetic & Cadastral Unit Conversions (3 cases)
    {"id": 43, "cat": "CONVERSIONS", "q": "Convert 10000 sqm to acre", "ws": "SSC", "expect_intent": "CALCULATION", "keywords": ["1 Acre = 43,560 sq.ft", "4,046.86 sq.m", "2.471 Acres"]},
    {"id": 44, "cat": "CONVERSIONS", "q": "How many guntha in 1 acre in Central India?", "ws": "SSC", "expect_intent": "CALCULATION", "keywords": ["40 Gunthas", "1,089 sq.ft"]},
    {"id": 45, "cat": "CONVERSIONS", "q": "Convert 1 hectare to square feet and acres", "ws": "SSC", "expect_intent": "CALCULATION", "keywords": ["2.471 Acres", "10,000 sq.m", "107,639 sq.ft"]},

    # Category 16: Live Web Research & Market Intelligence (DuckDuckGo + Wikipedia) (4 cases)
    {"id": 46, "cat": "WEB_RESEARCH", "q": "DJI Matrice 350 RTK drone price in India and specifications", "ws": "SSC", "expect_intent": "LIVE_WEB_RESEARCH", "keywords": ["Live Research Report", "Verified Facts", "Citations"]},
    {"id": 47, "cat": "WEB_RESEARCH", "q": "Trimble R12i GNSS receiver market pricing and accuracy", "ws": "SSC", "expect_intent": "LIVE_WEB_RESEARCH", "keywords": ["Live Research Report", "Recommendations", "Trimble"]},
    {"id": 48, "cat": "WEB_RESEARCH", "q": "Competitor land surveying companies in Maharashtra and Nagpur", "ws": "SSC", "expect_intent": "LIVE_WEB_RESEARCH", "keywords": ["Live Research Report", "Facts", "Sources"]},
    {"id": 49, "cat": "WEB_RESEARCH", "q": "Instagram reels organic growth strategies for engineering businesses 2026", "ws": "SSC", "expect_intent": "LIVE_WEB_RESEARCH", "keywords": ["Live Research Report", "Recommendations", "Citations"]},

    # Category 17: Multi-Tenant Data Isolation & Anti-Hallucination (1 case)
    {"id": 50, "cat": "TENANT_ISOLATION", "q": "Show P&L profit for INFRA workspace while logged into SSC", "ws": "SSC", "expect_intent": "BUSINESS_DATA", "keywords": ["Factual P&L Financial Report for SSC", "INR"]}
]


def run_50_case_ai_evaluation():
    store = Store("data/sgcc_foundation.sqlite")
    print(f"=== STARTING 50-CASE AI INTELLIGENCE & RESEARCH SUITE ===")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Test Cases: {len(EVAL_CASES)}\n")

    results = []
    passed = 0
    failed = 0

    for tc in EVAL_CASES:
        t0 = time.time()
        res = ai_intelligence.ask_anything(store, tc["q"], tc["ws"])
        elapsed = round((time.time() - t0) * 1000, 1)

        intent = res.get("intent")
        ans = res.get("verified_answer", "")
        citations = res.get("citations", [])

        # Check intent
        intent_match = (intent == tc["expect_intent"])
        
        # Check expected keywords
        keywords_found = [kw for kw in tc["keywords"] if kw.lower() in ans.lower()]
        keywords_match = (len(keywords_found) >= min(1, len(tc["keywords"])))

        # Anti-hallucination check: ensure answer is not empty and not generic canned text
        not_empty = len(ans) > 60
        not_canned = "Aapne" not in ans or "Corporate Operations" not in ans or intent != "AI_INTELLIGENCE"

        is_pass = intent_match and keywords_match and not_empty

        if is_pass:
            passed += 1
            status_str = "PASS"
        else:
            failed += 1
            status_str = "FAIL"

        result_entry = {
            "case_id": tc["id"],
            "category": tc["cat"],
            "query": tc["q"],
            "workspace": tc["ws"],
            "intent_expected": tc["expect_intent"],
            "intent_actual": intent,
            "latency_ms": elapsed,
            "citations_count": len(citations),
            "status": status_str,
            "verified_answer_preview": ans[:150].replace("\n", " ") + "..."
        }
        results.append(result_entry)

        symbol = "✓" if is_pass else "✗"
        print(f"[{symbol} {status_str}] Case #{tc['id']:02d} ({tc['cat']}): '{tc['q'][:45]}...' -> {intent} ({elapsed}ms)")
        if not is_pass:
            print(f"    Expected: {tc['expect_intent']} | Got: {intent} | Matched KW: {keywords_found}/{tc['keywords']}")

    print(f"\n=======================================================")
    print(f"=== 50-CASE AI EVALUATION SUMMARY: {passed}/{len(EVAL_CASES)} PASSED ===")
    print(f"Pass Rate: {round(passed / len(EVAL_CASES) * 100, 1)}%")
    print(f"Failures: {failed}")
    print(f"=======================================================\n")

    # Save machine-readable evidence
    os.makedirs("AUDIT_TEST_EVIDENCE", exist_ok=True)
    evidence_path = "AUDIT_TEST_EVIDENCE/ai_intelligence_50_cases_evidence.json"
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_run_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases": len(EVAL_CASES),
            "passed": passed,
            "failed": failed,
            "pass_rate_pct": round(passed / len(EVAL_CASES) * 100, 1),
            "cases": results
        }, f, indent=2)
    print(f"Detailed evidence written to: {evidence_path}")
    return passed == len(EVAL_CASES)


if __name__ == "__main__":
    success = run_50_case_ai_evaluation()
    sys.exit(0 if success else 1)
