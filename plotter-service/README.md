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
