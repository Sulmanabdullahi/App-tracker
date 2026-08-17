# `Dockerfile`

The recipe used to build the container image that runs on Cloud Run.
You never run this file directly — `gcloud run deploy --source .` reads
it, builds an image from it (via Google Cloud Build), and deploys that
image. See [`sops/deploy-a-change.md`](../sops/deploy-a-change.md) for
the actual deploy command.

## Line-by-line

```dockerfile
FROM python:3.12-slim
```
Start from an official, minimal Python 3.12 base image (`-slim` means it
skips a lot of OS packages a full image would include, keeping the
final image smaller and the build faster).

```dockerfile
WORKDIR /app
```
Every following command runs from `/app` inside the container — this is
just an organizational choice (could be any path).

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Copies **only** `requirements.txt` first and installs dependencies
before copying the rest of the source code. This is a standard Docker
optimization: Docker caches each step, keyed on its inputs. As long as
`requirements.txt` hasn't changed, Docker reuses the cached "dependencies
installed" layer even if the application code changes — so rebuilding
after a code-only change doesn't re-download and reinstall every Python
package from scratch. `--no-cache-dir` tells `pip` not to keep its own
download cache, which would otherwise bloat the image for no benefit
(nothing rebuilds `pip`'s cache inside a fresh container anyway).

```dockerfile
COPY . .
```
Copies the rest of the repository into the image. What gets excluded
from this copy is controlled by [`.dockerignore`](../../.dockerignore)
(notably: `.git`, `.env`, `.venv`, and anything else that shouldn't ship
inside the container — secrets in particular must never end up baked
into an image, since images can be pulled/inspected by anyone with
registry access).

```dockerfile
ENV PORT=8080
EXPOSE 8080
```
Cloud Run expects containers to listen on the port given by the `PORT`
environment variable (which Cloud Run itself sets at runtime — this
`ENV PORT=8080` is really just a sensible default for running the image
outside of Cloud Run, e.g. locally with `docker run`). `EXPOSE` is
documentation-only in Docker; it doesn't actually open the port by
itself.

```dockerfile
CMD ["sh", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true"]
```
The command that runs when the container starts. Broken down:

- `streamlit run app.py` — start the app (see [`app.py.md`](app.py.md)).
- `--server.port=$PORT` — listen on whatever port Cloud Run assigned
  (read via the `sh -c` shell, which is why this is a shell command
  string rather than Docker's plain exec-form array — `$PORT` needs
  shell expansion to be substituted).
- `--server.address=0.0.0.0` — listen on all network interfaces, not
  just `localhost`. Without this, the container would only accept
  connections from *inside itself*, which Cloud Run's routing could
  never reach.
- `--server.headless=true` — don't try to open a local browser window
  (the default behavior when you run `streamlit run` on your own
  machine) — there's no browser to open inside a server container, and
  Streamlit would otherwise error trying.
