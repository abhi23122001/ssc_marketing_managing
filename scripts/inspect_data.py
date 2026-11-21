import sys, os
sys.path.insert(0, r'C:\Users\HP\Desktop\ssc_marketing_managing')
from foundation.store import Store

st = Store(r'C:\Users\HP\Desktop\ssc_marketing_managing\data\sgcc_foundation.sqlite')
clients = st.fetchall("SELECT id, client_workspace_id, company_name FROM social_client_profiles")
print("Clients:", clients)

sites = st.fetchall("SELECT id, workspace_id, code, name FROM sites")
print("Sites:", sites)

leads = st.fetchall("SELECT id, workspace_id, lead_name, company FROM social_leads")
print("Leads:", leads)
