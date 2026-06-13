FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS production
COPY . .
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
EXPOSE 5000
# Entrypoint wsgi:app -> applique automatiquement les migrations en attente au
# démarrage (run_auto_migrations), sérialisé entre workers par un verrou Postgres.
# Workers gthread : psycopg2 libère le GIL pendant l'I/O DB, donc les threads
# offrent de la concurrence sans le piège gevent+psycopg2 bloquant.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gthread", "--threads", "4", "--timeout", "120", "wsgi:app"]
