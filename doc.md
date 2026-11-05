## Quick test checklist
- [x] Home page loads
- [ ] Empty state appears before any reports
- [ ] Submit a report with all fields
- [ ] New report appears on the home page
- [ ] Category filter works
- [ ] Status can be changed and remains changed after refresh
- [ ] `/health` returns `{"status":"ok","app":"MtaaFix"}`

## Important security note
This is a local hackathon demo, not a production-ready public service. The status update endpoint has no login protection. Before deploying publicly, add coordinator authentication, authorization, input protections, backups, and a privacy policy. Do not collect sensitive personal data.

## Suggested next improvements
1. Add image upload with file-size/type validation.
2. Add coordinator login and role-based status updates.
3. Add a map only after the core reporting workflow is reliable.
4. Add duplicate-report detection and a community impact dashboard.
