"""Domain layer (M15-M18 + SHAH AI Brain foundation).

All domain methods are workspace-scoped. The workspace_id is taken from the
authenticated request; the Owner reaches every workspace. No domain method
hardcodes a business name.
"""
from __future__ import annotations

from . import ai_brain, attendance, employee, expense, payroll, m19_schema, m19_core, m19_media, m19_workflow
from .migrate import create_domain_tables, seed_domain_demo

__all__ = [
    "employee", "attendance", "expense", "payroll", "ai_brain",
    "m19_schema", "m19_core", "m19_media", "m19_workflow",
    "migrate", "create_domain_tables", "seed_domain_demo",
]

# Re-exported domain functions, imported so consumers can do
#   from foundation.domains import employee
# and call employee.create_department(store, actor_id, workspace_id, ...).
from . import employee as _employee  # noqa: F401
from . import attendance as _attendance  # noqa: F401
from . import expense as _expense  # noqa: F401
from . import payroll as _payroll  # noqa: F401
from . import ai_brain as _ai_brain  # noqa: F401
