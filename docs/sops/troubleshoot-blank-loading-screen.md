# SOP: The app loads but shows only a blank/loading skeleton

## Symptom

Opening the app's URL shows the page shell (maybe a spinner, or nothing
at all) but the actual login form / dashboard never appears, no matter
how long you wait.

## Background

This exact symptom happened once before and is fully documented in
[ADR 0004](../adr/0004-cloud-run-direct-not-firebase-hosting.md) and
[ADR 0005](../adr/0005-cloud-run-session-affinity.md). It has two known
root causes, both related to how [Streamlit](../adr/0001-use-streamlit-for-the-ui.md)
requires a persistent WebSocket connection (`/_stcore/stream`) to render
any content after the initial page load.

## Step 1: Check the browser console

Open the browser's DevTools (F12 or right-click → Inspect) → **Console**
tab, and reload the page. Look specifically for a line like:

```
WebSocket connection to 'wss://.../_stcore/stream' failed: ...
```

**If you see this:** the WebSocket isn't connecting at all — go to
Step 2.

**If you don't see this** (WebSocket connects fine, but the UI still
looks broken/wrong): this is a different, likely code-level bug — check
the Cloud Run application logs instead (`gcloud run services logs read
app-tracker --region us-central1`) for a Python traceback, and see the
relevant [module doc](../modules/README.md) for the file involved.

## Step 2: Confirm you're on the direct Cloud Run URL

```bash
gcloud run services describe app-tracker --region us-central1 \
  --format="value(status.url)"
```

**If the URL you're testing doesn't match this exactly** (e.g. you're on
a `*.web.app` or a custom domain), you're likely hitting Firebase
Hosting or another proxy in front of Cloud Run again — see
[ADR 0004](../adr/0004-cloud-run-direct-not-firebase-hosting.md). Fix:
point users at the direct Cloud Run URL, or (if a custom domain is
required) set up a proper HTTPS Load Balancer + Serverless NEG instead
of a Hosting rewrite — do not re-add a `hosting` rewrite to
[`firebase.json`](../modules/firebase.json.md).

## Step 3: Confirm session affinity is enabled

```bash
gcloud run services describe app-tracker --region us-central1 \
  --format="yaml(spec.template.spec.sessionAffinity)"
```

If this doesn't show `sessionAffinity: true`, someone deployed without
`--session-affinity` — see
[ADR 0005](../adr/0005-cloud-run-session-affinity.md). Fix: redeploy
following [`deploy-a-change.md`](deploy-a-change.md), which includes
this flag.

## Step 4: Check application startup logs

```bash
gcloud run services logs read app-tracker --region us-central1 --limit 50
```

Look for `Uvicorn server started` and `You can now view your Streamlit
app in your browser` — these confirm Streamlit itself started
successfully inside the container. If these lines are missing, or there's
a Python traceback instead, the problem is in application startup (check
that `FIREBASE_PROJECT_ID` and `FIREBASE_API_KEY` env vars are set
correctly on the service — a missing/wrong `FIREBASE_PROJECT_ID` can
cause `firebase_admin.initialize_app()` in [`app.py`](../modules/app.py.md)
to fail).

## Verifying a fix worked

The most reliable check is driving the URL with a real browser and
watching for console errors — a plain `curl` won't catch a broken
WebSocket handshake, because `curl` doesn't perform a real browser-style
WebSocket upgrade by default. If you have Playwright available:

```js
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('<service-url>', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  console.log(await page.evaluate(() => document.body.innerText));
  console.log('Console errors:', errors);
  await browser.close();
})();
```

A healthy result: real page text (the login form's "Log in" / "Sign up"
tabs, etc.) and an empty `errors` array.
