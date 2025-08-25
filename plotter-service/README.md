# Plotter Service

A FastAPI-based service for handling plotter operations and SVG processing using vpype.

## Features

- SVG file loading and processing
- Raster image to SVG conversion (PNG, JPG, etc.)
- Path optimization for plotting
- RESTful API endpoints
- Docker containerization
- Integration with vpype for vector graphics processing
- ImageMagick, potrace, and autotrace integration

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn
- vpype
- requests

## Installation

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Docker

1. Build the Docker image:
   ```bash
   docker build -t plotter-service .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 plotter-service
   ```

## Usage

### Running the Service

```bash
# Local development
python -m uvicorn app.main:app --reload

# Or directly
python app/main.py
```

The service will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Root endpoint with service status
- `GET /health` - Health check endpoint
- `POST /generate-svg` - Convert raster images to optimized SVG for plotting
- `GET /daily-art` - Get a unique spirograph SVG for the current day
- `GET /spirographs` - Generate packs of spirograph patterns
- `POST /jobs` - Create a new job from today's art or provided SVG
- `GET /jobs` - List recent jobs
- `GET /jobs/next?plotter_id=NIMO-01` - Atomically reserve the next job for a plotter
- `POST /jobs/{id}/status` - Update job status and optional notes
- `GET /docs` - Interactive API documentation (Swagger UI)

### Using the Pipeline

```python
from app.pipeline import PlotterPipeline

pipeline = PlotterPipeline()

# Load an SVG file
success = pipeline.load_svg("path/to/file.svg")

if success:
    # Optimize paths
    pipeline.optimize_paths()
    
    # Get statistics
    stats = pipeline.get_statistics()
    print(f"Total paths: {stats['total_paths']}")
    
    # Export G-code (placeholder)
    pipeline.export_gcode("output.gcode")
```

### Raster to SVG Conversion

The service can convert raster images (PNG, JPG, etc.) to optimized SVG files suitable for plotting:

```python
from app.pipeline import raster_to_svg

# Convert an image URL to SVG
svg_content = raster_to_svg(
    image_url="https://example.com/image.png",
    width_mm=160,
    height_mm=160,
    margin_mm=5,
    simplify_mm=0.2,
    mode="outline"  # or "centerline"
)

# Use the generated SVG
pipeline = PlotterPipeline()
pipeline.load_svg_content(svg_content)
pipeline.optimize_paths()
```

**Conversion Modes:**
- `outline`: Uses potrace for outline tracing (default)
- `centerline`: Uses autotrace for centerline tracing

**Parameters:**
- `width_mm`, `height_mm`: Output dimensions in millimeters
- `margin_mm`: Margin around the content
- `simplify_mm`: Line simplification threshold

### Daily Art Generation

The service includes a daily art endpoint that generates unique procedural SVGs:

```bash
# Get today's unique SVG
curl "https://your-service.com/daily-art"
```

**Features:**
- **Date-seeded randomness**: Same output all day, new one each day
- **Spirograph patterns**: Uses hypotrochoid and epitrochoid mathematical curves
- **Plotter-ready**: Optimized SVG output suitable for plotting
- **Consistent dimensions**: 160x160mm output with proper viewBox

### Spirograph Generation

Generate packs of spirograph patterns:

```bash
# Get 8 spirographs (80x80mm)
curl "https://your-service.com/spirographs?count=8&width_mm=80&height_mm=80"

# Get 12 spirographs with custom dimensions
curl "https://your-service.com/spirographs?count=12&width_mm=100&height_mm=60&margin_mm=10"

# Use specific seed for reproducible results
curl "https://your-service.com/spirographs?seed=12345"
```

**Pattern Types:**
- **Hypotrochoids**: Rolling circle inside fixed circle
- **Epitrochoids**: Rolling circle outside fixed circle
- **Mathematical precision**: Uses LCM calculations for closed curves
- **Optimized sampling**: 4000+ points for smooth lines

## Jobs API

SQLite-backed minimal queue for plotter jobs.

Schema: `id, svg_text, status(queued|reserved|started|completed|failed), plotter_id, created_at, updated_at`.

Examples:

```bash
# Create today's job (uses /daily-art under the hood)
curl -X POST "https://your-service.com/jobs" -H "Content-Type: application/json"

# Create a job from your own SVG
curl -X POST "https://your-service.com/jobs" \
  -H "Content-Type: application/json" \
  -d '{"svg_text": "<svg>...</svg>"}'

# List jobs
curl "https://your-service.com/jobs?limit=10"

# Reserve next job for plotter NIMO-01 (204 if none available)
curl "https://your-service.com/jobs/next?plotter_id=NIMO-01"

# Update job status
curl -X POST "https://your-service.com/jobs/123/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "started", "notes": "sent to GRBL"}'
```

## Project Structure

```
plotter-service/
├─ app/
│  ├─ main.py          # FastAPI application and endpoints
│  └─ pipeline.py      # Plotter pipeline logic
├─ requirements.txt     # Python dependencies
├─ Dockerfile          # Docker configuration
└─ README.md           # This file
```

## Development

### Adding New Endpoints

Add new endpoints in `app/main.py`:

```python
@app.post("/process-svg")
async def process_svg(file_path: str):
    pipeline = PlotterPipeline()
    success = pipeline.load_svg(file_path)
    if success:
        pipeline.optimize_paths()
        return {"status": "success", "stats": pipeline.get_statistics()}
    return {"status": "error", "message": "Failed to load SVG"}
```

### Extending the Pipeline

Add new methods to the `PlotterPipeline` class in `app/pipeline.py`:

```python
def custom_operation(self):
    """Add your custom plotter operation here"""
    pass
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
