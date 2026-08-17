// This file creates ONE reusable Postgres connection pool that every
// API route will import, instead of each route opening its own connection.
//
// WHAT TO DO:
// 1. `npm install pg` and `npm install --save-dev @types/pg` (already in
//    package.json — just run npm install)
// 2. Import { Pool } from "pg"
// 3. Create a `new Pool({ connectionString: ... })` using the DATABASE_URL
//    environment variable (see .env.example)
// 4. Export it as the default export
//
// WHY A POOL AND NOT A SINGLE CONNECTION:
// Opening a new database connection is slow. A pool keeps a handful of
// connections open and hands them out to whichever query needs one,
// reusing them across requests. Look up "connection pooling" if the
// concept is new.
//
// GOTCHA: in Next.js dev mode, this file can get re-imported on every hot
// reload, which can create many pools and exhaust your DB's connection
// limit. Search "Next.js pg pool singleton hot reload" if you hit this.
