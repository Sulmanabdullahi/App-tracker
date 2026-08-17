"""
Application Tracker — analysis script.

Run by hand for now:  python analyze.py

Job: read applications + status_history from Postgres, compute stats per
user, write the results into the "stats" table. The web app never runs
this logic itself — it just reads what this script last wrote.

WHAT TO BUILD, STEP BY STEP:

1. CONNECT TO THE DATABASE
   - Use psycopg2 (pip install psycopg2-binary --break-system-packages)
   - Read the connection string from the DATABASE_URL environment
     variable (os.environ) — same one the Next.js app uses.

2. FIND EVERY USER WHO HAS APPLICATIONS
   - SELECT DISTINCT firebase_uid FROM applications
   - You'll loop over each one and compute their stats separately —
     stats are per-user, not global.

3. FOR EACH USER, COMPUTE:
   a. total_applications
      - simple COUNT(*) WHERE firebase_uid = <uid>
   b. response_rate
      - what fraction of applications have moved past "applied"?
      - COUNT(*) FILTER (WHERE status != 'applied') / COUNT(*)
      - watch out for divide-by-zero if a user has 0 applications
   c. avg_days_to_response
      - for each application, how many days between applied_date and its
        first non-"applied" status_history entry?
      - this needs a JOIN between applications and status_history
      - average that across all applications that DID get a response
   d. needs_followup
      - applications still stuck on "applied" status where last_update
        is older than some threshold (try 14 days)
      - collect id, company, role, and how many days it's been pending

4. WRITE RESULTS INTO THE stats TABLE
   - One row per user (firebase_uid is the primary key)
   - Use "INSERT ... ON CONFLICT (firebase_uid) DO UPDATE SET ..." so
     re-running the script overwrites the old numbers instead of piling
     up duplicate rows. Look up "upsert" if that's new.
   - Store needs_followup as JSON (json.dumps(...)) since the column
     type is JSONB.

5. PRINT A SUMMARY TO THE TERMINAL
   - Helpful for sanity-checking your own work before the frontend ever
     reads this data.

DESIGN QUESTION TO THINK ABOUT:
This script currently has to run manually, on your own machine, to
update the stats. Where would you eventually want this to run instead
so it stays fresh automatically? (cron, GitHub Actions, etc. — no need
to build that yet, just have an opinion.)
"""
