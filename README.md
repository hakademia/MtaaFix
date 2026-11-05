# MtaaFix

> [A short, clear description of what your project does.]

A community project developed within **Hakademia**.

## Overview

MtaaFix is a beginner-friendly Flask + SQLite prototype for reporting and tracking community problems.

## Features

- Submit a community report
- Categorize issues (road damage, garbage, water, streetlights, other)
- View all reports and filter by category
- Track status: Reported, In Progress, Resolved
- Simple dashboard counters
- SQLite database is created automatically

## Getting started

### Requirements

- python3 
- sqlite3
- Flask

### Installation (Run on Ubuntu / Linux)

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

### Usage

4. Start the app:

   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

If `python3 -m venv .venv` fails on Ubuntu, install the venv package with:
`sudo apt install python3-venv`


## Project credits

This repository is hosted within Hakademia. Hosting alone does not determine copyright ownership or authorship. See [AUTHORS.md](AUTHORS.md) for individual credits.

## Contributing

Contributions are welcome! Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request.

## License

This project is licensed under the [MIT License](LICENSE), provided that the project creator has chosen to use it and updated the copyright notice.

---

