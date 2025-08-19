from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from .pipeline import raster_to_svg
from datetime import date
import random

app = FastAPI(
    title="Plotter Service",
    description="A service for handling plotter operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Plotter Service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


class Job(BaseModel):
    image_url: HttpUrl
    width_mm: float = 160
    height_mm: float = 160
    margin_mm: float = 5
    simplify_mm: float = 0.2
    mode: str = "outline"  # "outline" or "centerline"


@app.post("/generate-svg")
def generate_svg(job: Job):
    try:
        svg = raster_to_svg(
            image_url=str(job.image_url),
            width_mm=job.width_mm,
            height_mm=job.height_mm,
            margin_mm=job.margin_mm,
            simplify_mm=job.simplify_mm,
            mode=job.mode,
        )
        return {"svg": svg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_daily_svg():
    """Generate a unique SVG for the current day using procedural generation"""
    # Seed randomness by date so it's stable
    today = date.today().isoformat()
    random.seed(today)

    # Example: generate a spiral path
    w, h = 160, 160
    svg = f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
    x, y = w/2, h/2
    path = f'<path d="M{x},{y} '
    for i in range(200):
        angle = i * 0.2
        r = 2 + i * 0.3
        px = x + r * random.uniform(0.9, 1.1) * \
            (1.2 * random.choice([1, -1])) * (i % 2)
        py = y + r * random.uniform(0.9, 1.1) * \
            (1.2 * random.choice([1, -1])) * (i % 2)
        path += f'L{px},{py} '
    path += '" stroke="black" fill="none"/>'
    svg += path + "</svg>"
    return svg


@app.get("/daily-art")
def daily_art():
    """Return a unique SVG for the current day"""
    return {"date": date.today().isoformat(), "svg": generate_daily_svg()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
