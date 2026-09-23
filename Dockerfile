FROM python:3.12-slim

WORKDIR /app

# Copy ONLY requirements first — this is a deliberate layer-caching trick.
# Docker caches each instruction as a layer; if requirements.txt hasn't
# changed, Docker reuses the cached pip install layer instead of
# re-running it, even if your actual application code changed. Copying
# everything at once would invalidate this cache on every single code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn apps.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
