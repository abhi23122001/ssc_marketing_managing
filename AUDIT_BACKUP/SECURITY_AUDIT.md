# SHAH Group AI OS — Security Audit Report

**Date of Audit**: 2026-11-20  
**Target Environment**: Windows 11 / Localhost `127.0.0.1:8899`  
**Database**: SQLite (`data/sgcc_foundation.sqlite`)

---

## 1. Executive Summary
The security model was evaluated against the requirements specified in Part 6 and Part 7 of the Master Handover document:
- Authentication & Password Security
- Role-Based Access Control (RBAC) & Principle of Least Privilege
- Multi-Tenant Workspace Data Isolation
- Session Management & Expiration
- Injection & Input Validation
- Audit Logging & Traceability

---

## 2. Findings and Remediation

### Finding SEC-01: Deactivated User Session Lifespan (RESOLVED IN PHASE 2)
- **Classification**: High
- **Description**: `Store.decode_session()` previously did not verify the user's active status from the `users` table. If an admin marked a user as inactive, their existing session tokens remained valid until expiration.
- **Remediation**: 
  1. Updated `decode_session()` to join `users` and verify `u.active = 1`.
  2. Updated `authenticate()` to verify `u.active = 1`.
  3. Added session purge in `deactivate_user(id)`.

### Finding SEC-02: Password Storage
- **Classification**: Good (Standard Compliant)
- **Description**: Passwords are never stored in plaintext. Passwords use PBKDF2-HMAC-SHA256 with 100,000 iterations and per-user cryptographic salts (`foundation/store.py`).
- **Remediation Note**: Demo accounts are explicitly documented as local development placeholders in `foundation/config.py` and must be rotated in production.

### Finding SEC-03: Multi-Tenant Workspace Isolation
- **Classification**: Good (Strictly Enforced)
- **Description**: `foundation/isolation.py` and API route handlers verify the caller's assigned `workspace_id`. Cross-workspace reads return HTTP 403 unless the caller holds the `Owner` role.
- **Verification**: Verified via test case F03a in `run_foundation_tests.py` and test 6a in `test_integration.py`.

### Finding SEC-04: Parameterized SQL & Injection Prevention
- **Classification**: Good
- **Description**: SQLite queries across `foundation/store.py`, `foundation/domains/m19_core.py`, and `foundation/domains/m19_workflow.py` use parameterized `?` placeholders. No string concatenation is used in SQL statements.

### Finding SEC-05: Audit Trail Integrity
- **Classification**: Good
- **Description**: Sensitive state changes (approval creation/transitions, user account edits, lead creations, social account connections) write immutable records to the `audit_logs` table with actor ID, username, action, timestamp, and workspace ID.
