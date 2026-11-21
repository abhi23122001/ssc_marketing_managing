import sys, inspect
sys.path.insert(0, r'C:\Users\HP\Desktop\ssc_marketing_managing')
from foundation.store import Store

if hasattr(Store, 'create_client'):
    print(inspect.getsource(Store.create_client))
if hasattr(Store, 'list_clients'):
    print(inspect.getsource(Store.list_clients))
