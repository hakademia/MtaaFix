# MtaaFix — Hackathon Starter

MtaaFix is a beginner-friendly Flask + SQLite prototype for reporting and tracking community problems.

## Features
- Submit a community report
- Categorize issues (road damage, garbage, water, streetlights, other)
- View all reports and filter by category
- Track status: Reported, In Progress, Resolved
- Simple dashboard counters
- SQLite database is created automatically

## Run on Ubuntu / Linux

1. Open a terminal in this folder.
2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

If `python3 -m venv .venv` fails on Ubuntu, install the venv package with:
`sudo apt install python3-venv`

## Quick test checklist
- [ ] Home page loads
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
