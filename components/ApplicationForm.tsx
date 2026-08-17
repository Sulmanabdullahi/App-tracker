// Form for adding a new application (and optionally reusing it for
// editing an existing one).
//
// WHAT TO DO:
// 1. "use client" at the top.
// 2. Build controlled inputs (useState per field, or one state object)
//    for company, role, job_link, status, notes, source, location,
//    salary_range.
// 3. On submit: POST to /api/applications with the form data as JSON,
//    including the Authorization header with the user's Firebase token.
// 4. Handle the response: on success, clear the form and notify the
//    parent (a callback prop like onCreated) so the dashboard can
//    refresh its list. On failure, show the error.
// 5. Basic validation before sending: company and role must not be
//    empty (your API route also checks this — that's intentional
//    defense in depth, not duplication for no reason).
//
// STRETCH GOAL: make this same component handle EDITING an existing
// application too, by accepting an optional `existingApplication` prop
// that pre-fills the fields and switches the submit handler to PATCH
// instead of POST.
