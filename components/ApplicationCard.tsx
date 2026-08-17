// A single card representing one application, shown inside a dashboard
// column.
//
// WHAT TO DO:
// 1. Accept a prop for the application object (company, role, status,
//    applied_date, etc.) and a callback prop like onStatusChange.
// 2. Render the company name, role, and applied date.
// 3. Give the user a way to change status — a dropdown, or drag handles
//    if you want to build real drag-and-drop later (start with a
//    dropdown, it's much simpler).
// 4. When status changes, call a PATCH /api/applications/:id request
//    with { status: newStatus } in the body — then call the callback
//    prop so the parent dashboard knows to update.
// 5. Optional: a small delete button that calls DELETE
//    /api/applications/:id.
//
// KEEP THIS COMPONENT "DUMB": it shouldn't know how to fetch data itself
// beyond making the specific update/delete call for its own card — the
// dashboard page owns the full list and passes data down as props.
