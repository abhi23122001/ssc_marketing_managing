import sys, os
sys.path.insert(0, os.path.abspath("."))
from foundation.store import Store
from foundation.domains import google_sheets_sync

s = Store()
status = google_sheets_sync.get_google_sheets_status(s, "SSC")
print("Spreadsheet ID:", status["spreadsheet_id"])
print("Spreadsheet Title:", status["spreadsheet_title"])
print("Cloud Sync:", status["cloud_sync"])
print("Local Staging:", status["local_staging"])
print("Owner Sheet Inspection:", status["owner_sheet_inspection"])

res = google_sheets_sync.execute_sheets_sync(s, "SSC", "all")
print("Sync Result OK:", res["ok"])
print("Total Records Pushed:", res["total_records_pushed"])
print("Cloud Sync Status:", res["cloud_sync_status"])
print("Local Staging Status:", res["local_staging_status"])
