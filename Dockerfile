# ---- frontend build stage: only stage that touches Node.js ----
FROM node:22-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Tailwind v4's Vite plugin auto-scans the whole project (no tailwind.config.js
# content list here) - it needs the Django templates present, not just src/,
# or classes only used server-side would be missing from the built CSS.
COPY . .
RUN npm run build

# ---- runtime stage: Python only, no Node.js/npm anywhere in this image ----
FROM python:3.13-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Dependency manifest first so `docker build` can cache installs across
# source-only changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Baked-in reference copy of the built frontend assets. static/, media/, DB/
# are bind-mounted from the host at runtime (see docker-compose.yml) and may
# start out empty, so the entrypoint copies from here into static/dist on
# every start rather than relying on anything being pre-populated on the
# host - no Node.js needed to do that, just `cp`.
COPY --from=frontend /app/static/dist /opt/static-build/dist

RUN mkdir -p static media DB

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8989

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
