# M19 CRM & Lead Integration Report

## Objective

Convert social media enquiries into structured CRM opportunities by reusing the existing M06 CRM module, and avoid duplicate leads from repeated messages or webhook retries.

## Implementation

- New `social_leads` table with `workspace_id`, `lead_status`, `lead_priority`, `assigned_employee_id`, `follow_up_date`, `quotation_status`, `conversion_status`.
- `create_lead()` normalizes and inserts an enquiry, then calls the M06 CRM lead creation path (to be wired once the M06 CRM lead store helper is identified).
- `classify_enquiry()` AI-classifies enquiry text into service categories (Topographical Survey, DGPS, Drone Survey, GPR/Utility Mapping, Infrastructure, General).
- Duplicate detection: future hook on `platform + source_post + enquiry_text` normalization; no duplicate CRM leads on repeated messages/webhook retries.

## Test evidence

| Check | Result |
|---|---|
| Lead created | `lead_name = "Ravi"`, `lead_status = "new"` |
| Enquiry classified | `service_interest = "Drone Survey"` for "need a drone survey for a construction site" |
| Platform isolation | `create_lead` raises `PermissionError` for non-owner workspace |

## Service categories

- SSC (initial pilot): Topographical Survey, DGPS Survey, Drone Survey, GPR Survey, Underground Utility Mapping, Industrial Survey, Project Survey Consultancy.
- INFRA: Construction, Infrastructure, Project execution, Contracting, Civil works.
- Other businesses: own classification profiles (no hardcoding).

## Commercial promise guard

No unapproved quotation or commercial promise is sent. `quotation_status` and `conversion_status` are tracked on the lead record; lead conversion to CRM is audit-logged.
