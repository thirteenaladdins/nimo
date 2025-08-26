from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from .pipeline import raster_to_svg
from .spirographs import get_daily_spirograph
from datetime import date
import random
from typing import Optional, List

from .db import (
    init_db,
    create_job,
    list_jobs as db_list_jobs,
    reserve_next_job,
    update_job_status,
)

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


@app.on_event("startup")
def _startup() -> None:
    init_db()


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


class CreateJobRequest(BaseModel):
    svg_text: Optional[str] = None


class JobStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


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
    # Convert date string to integer seed for reproducible results
    seed = hash(today) % (2**32)  # Ensure positive 32-bit integer

    # Use spirograph generation for more interesting daily art
    return get_daily_spirograph(seed=seed)


@app.get("/daily-art")
def daily_art():
    """Return a unique SVG for the current day"""
    return {"date": date.today().isoformat(), "svg": generate_daily_svg()}


@app.get("/spirographs")
def generate_spirographs(
    count: int = 8,
    width_mm: float = 80.0,
    height_mm: float = 80.0,
    margin_mm: float = 5.0,
    seed: Optional[int] = None
):
    """Generate a pack of spirograph SVGs"""
    from .spirographs import generate_spirograph_pack

    if seed is None:
        # Use today's date as seed if none provided
        today = date.today().isoformat()
        seed = hash(today) % (2**32)

    svgs = generate_spirograph_pack(
        count=min(count, 20),  # Limit to 20 max
        width_mm=width_mm,
        height_mm=height_mm,
        margin_mm=margin_mm,
        seed=seed
    )

    return {
        "count": len(svgs),
        "seed": seed,
        "dimensions": {"width_mm": width_mm, "height_mm": height_mm, "margin_mm": margin_mm},
        "svgs": svgs
    }


# Jobs API

@app.post("/jobs")
def create_job_endpoint(payload: CreateJobRequest):
    try:
        svg = payload.svg_text if payload.svg_text else generate_daily_svg()
        job_id = create_job(svg)
        return {"job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs")
def list_jobs(limit: int = 20):
    try:
        jobs = db_list_jobs(limit=limit)
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/next")
def next_job(plotter_id: str, resp: Response):
    try:
        job = reserve_next_job(plotter_id=plotter_id)
        if job is None:
            resp.status_code = status.HTTP_204_NO_CONTENT
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/jobs/{job_id}/status")
def set_job_status(job_id: int, payload: JobStatusUpdate):
    try:
        job = update_job_status(job_id, payload.status, payload.notes)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
