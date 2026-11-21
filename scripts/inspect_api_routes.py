# scripts/inspect_api_routes.py
import re

content = open("foundation/api.py", encoding="utf-8").read()

routes = re.findall(r'elif\s+path\.startswith\([\'"]([^\'"]+)[\'"]\)', content)
routes += re.findall(r'if\s+path\.startswith\([\'"]([^\'"]+)[\'"]\)', content)
routes += re.findall(r'elif\s+path\s*==\s*[\'"]([^\'"]+)[\'"]', content)
routes += re.findall(r'if\s+path\s*==\s*[\'"]([^\'"]+)[\'"]', content)

print("Unique routes matched:", sorted(set(routes)))
