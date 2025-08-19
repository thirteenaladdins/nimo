FROM python:3.11-slim

# Native deps (no autotrace on trixie)
RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick potrace \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
    libgomp1 ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
