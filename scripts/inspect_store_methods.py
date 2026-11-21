import sys, inspect
sys.path.insert(0, r'C:\Users\HP\Desktop\ssc_marketing_managing')
from foundation.store import Store

methods = ['list_clients', 'list_sites', 'list_estimates', 'list_quotations', 
           'list_work_orders', 'list_invoices', 'list_payments', 'list_approvals',
           'list_vendors', 'list_expense_claims', 'list_resources']

for m in methods:
    if hasattr(Store, m):
        fn = getattr(Store, m)
        sig = inspect.signature(fn)
        print(f"{m}{sig}")
