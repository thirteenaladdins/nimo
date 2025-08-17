FROM python:3.11-slim

# System deps: imagemagick, potrace, autotrace (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick potrace autotrace curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Safer ImageMagick defaults sometimes block PDFs; we only use raster→pbm
# (No policy changes needed here.)

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
