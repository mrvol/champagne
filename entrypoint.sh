#!/bin/sh
set -e

# static/, media/, DB/ are bind-mounted from the host and may start out
# empty. static/dist is seeded from the image's baked-in build output
# (produced by the Node frontend stage at `docker build` time) - the
# runtime image itself has no Node.js, so this is a plain file copy.

mkdir -p static media DB

echo "Seeding static/dist from the image's built frontend assets ..."
rm -rf static/dist
cp -r /opt/static-build/dist static/dist

echo "Applying database migrations ..."
uv run python manage.py migrate --noinput

if [ "$LOAD_SAMPLE_DATA" = "1" ] && [ ! -f "DB/db.sqlite3.seeded" ]; then
    echo "Loading sample data ..."
    uv run python manage.py loaddata sample_data.json
    touch DB/db.sqlite3.seeded
fi

echo "Starting server on :8989 ..."
exec uv run python manage.py runserver 0.0.0.0:8989
