# Application Tracker — learning scaffold

Every file in this project (except package.json and .env.example) contains
ONLY comments — no working code. Each comment block explains what the file
needs to do, why, and what to look up. You write the actual code.

## Suggested build order

1. `db/schema.sql` — write the three CREATE TABLE statements. Run this
   against a real Postgres database before writing anything else; you
   can't test any API route without tables to query.
2. `lib/db.ts` — get a working Postgres connection. Test it with a
   throwaway script that just runs `SELECT 1`.
3. `app/api/applications/route.ts` and `.../[id]/route.ts` — build these
   WITHOUT auth first (skip the getUidFromRequest check, hardcode a
   uid string) so you can test CRUD with curl/Postman before auth adds
   complexity.
4. `lib/firebase-client.ts` and `app/login/page.tsx` — get login working
   on its own, confirm you can see a user object in the browser console.
5. `lib/firebase-admin.ts` — go back and add real auth checks to your
   API routes now that you have real tokens to test with.
6. `app/page.tsx`, `components/ApplicationCard.tsx`,
   `components/ApplicationForm.tsx` — wire the dashboard to the working
   API routes.
7. `python/analyze.py` — write the stats logic, run it by hand, check
   the `stats` table filled in correctly.
8. `app/api/stats/route.ts` and `components/StatsPanel.tsx` — display
   what Python computed.

## Folder structure

- `db/schema.sql` — the three tables (applications, status_history, stats)
- `lib/db.ts` — Postgres connection
- `lib/firebase-admin.ts` — server-side: verify who's making a request
- `lib/firebase-client.ts` — browser-side: log in/out
- `app/api/applications/` — REST: list + create
- `app/api/applications/[id]/` — REST: get, update, delete one
- `app/api/stats/` — serves whatever python/analyze.py last computed
- `app/login/page.tsx` — login screen
- `app/page.tsx` — dashboard
- `components/` — Card, Form, StatsPanel
- `python/analyze.py` — standalone stats script, run by hand

## Setup once you've written the code

1. Create a Postgres database, run your finished `db/schema.sql`.
2. Create a Firebase project, enable Authentication, generate a service
   account key.
3. Copy `.env.example` to `.env.local`, fill in your values.
4. `npm install && npm run dev`
5. `cd python && pip install -r requirements.txt --break-system-packages
   && python analyze.py`
