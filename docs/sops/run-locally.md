# SOP: Run the app locally

For first-time setup (creating a Firebase project, getting credentials
for the first time), use [`quickstart.md`](../quickstart.md) instead —
this SOP assumes that's already done once, and you just want the
day-to-day commands to start developing.

## Prerequisites (one-time only)

- [ ] Python 3.12+ installed
- [ ] `.env` exists in the repo root with real values (see
      [`modules/env-files.md`](../modules/env-files.md))
- [ ] `service-account.json` exists in the repo root (see
      [`quickstart.md`](../quickstart.md) step 4)

## Steps

1. Create/activate the virtual environment:
   ```bash
   python3 -m venv .venv        # only if .venv doesn't already exist
   source .venv/bin/activate
   ```

2. Install/update dependencies (only needed if
   [`requirements.txt`](../modules/requirements.txt.md) changed since
   you last ran this):
   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:
   ```bash
   streamlit run app.py
   ```

4. Streamlit prints a local URL (usually `http://localhost:8501`) and
   opens it automatically. Leave this command running in its terminal —
   Ctrl+C to stop it.

5. Streamlit **auto-reloads** the page when it detects you've saved a
   change to `app.py` (or any file it imports). You'll usually just need
   to refresh the browser tab, or click "Rerun" if Streamlit prompts you
   in the top-right corner.

## Notes

- This connects to your **real** Firebase project (whichever one
  `FIREBASE_PROJECT_ID` in `.env` points at) — there's no local/emulated
  Firestore in this setup. Data you create while testing locally is
  real, persists, and is visible from the deployed app too (same
  database). Use a personal test account, not a real one, if that
  matters to you.
- If you need a clean slate, see
  [`delete-a-user-and-their-data.md`](delete-a-user-and-their-data.md).
