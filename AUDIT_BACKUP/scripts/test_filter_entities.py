import sys
sys.path.insert(0, r'C:\Users\HP\Desktop\ssc_marketing_managing')
from foundation.store import Store
from foundation.domains import filter_system

st = Store(r'C:\Users\HP\Desktop\ssc_marketing_managing\data\sgcc_foundation.sqlite')
entities = ["tasks", "sites", "estimates", "quotations", "work_orders", "invoices", "expenses", "leads", "media", "studio"]

for ent in entities:
    try:
        res = filter_system.query_filtered_records(st, ent, "SSC", {"search": "test"})
        print(f"Entity '{ent}' query OK: {res['pagination']['total_count']} results")
    except Exception as e:
        print(f"Entity '{ent}' ERROR: {e}")
