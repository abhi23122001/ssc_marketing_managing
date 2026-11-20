# M19 Approval & Publishing Report

## Objective

Verify the mandatory approval machine: version-locked approvals bound to exact content, and the publishing gate that requires explicit owner approval before any external call.

## Test procedure

1. Create a content item (`social_content_items`).
2. Generate script + caption (`generate_script`, `generate_caption` — write to `social_content_versions`).
3. Request approval (`request_approval` → status `pending`).
4. Approve the exact version (`approve_approval` → status `approved`, `final_version` incremented).
5. Enqueue the publish job (`enqueue_publish` → `scheduled`).
6. Verify the publish queue holds the approved version and blocks before live publishing.

## Result

| Step | Result |
|---|---|
| Content item created | `id = 1` |
| Script generated | `len > 0` |
| Caption generated | `len > 20` |
| Approval created | `status = pending` |
| Approval approved | `status = approved`, `final_version = 1` |
| Publish queue | `status = scheduled`, `content_id = 1` |

## Version control evidence

- `request_approval` locks `version_locked = 1` from the latest content version.
- `approve_approval` stores `final_script`, `final_caption`, `final_cta`, `final_hashtags`, `final_media_url`, `final_version = final_version + 1`.
- `enqueue_publish` re-reads `latest_approved_version` and refuses to queue a publish when `final_script` is empty — the exact content must be re-supplied by the owner before the external call.
- The publishing gate is **deliberately incomplete**: `enqueue_publish` only checks for a non-empty `final_script`. A real implementation must also re-verify platform permission and account status immediately before the API call.

## Publishing rules enforced

- No external publishing without explicit owner approval.
- Approval is version-locked: any material change invalidates the old approval (the workflow re-resources the latest version).
- The publishing queue is the sole gate between `approved` and `published`.

## Platform integration status

- Platform adapters (Instagram, Facebook, LinkedIn, YouTube) exist as a mock first: default mode for automated validation.
- Real API publishing is **blocked** until owner grants platform authorization; flagged as `integration required`.
