# Standard Operating Procedures (SOPs)

Step-by-step instructions for tasks someone maintaining this app will
need to do. Unlike the [module docs](../modules/README.md) (which
explain *what a file is*) or the [ADRs](../adr/README.md) (which explain
*why a decision was made*), these are task-oriented — start here when
you know what you need to *do*.

| SOP | When to use it |
|---|---|
| [run-locally.md](run-locally.md) | Setting up and running the app on your own machine for development |
| [deploy-a-change.md](deploy-a-change.md) | Shipping a code or config change to the live app |
| [rotate-the-firebase-api-key.md](rotate-the-firebase-api-key.md) | The Web API key or a service account key may have leaked, or you're doing routine credential hygiene |
| [add-or-remove-a-status-column.md](add-or-remove-a-status-column.md) | Adding a new Kanban column (e.g. "Ghosted") or removing an existing one |
| [delete-a-user-and-their-data.md](delete-a-user-and-their-data.md) | Someone wants their account and data removed, or you need to clean up a test/spam account |
| [troubleshoot-blank-loading-screen.md](troubleshoot-blank-loading-screen.md) | The app loads its outer shell but never shows real content |
