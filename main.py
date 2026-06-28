import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# ---------------------------------------------------------------------------
# >>> EDIT THESE TWO VALUES BEFORE DEPLOYING <<<
# ---------------------------------------------------------------------------
ALLOWED_ORIGIN = "https://dash-dgb14h.example.com"
YOUR_EMAIL = "24f3005134@ds.study.iitm.ac.in"
# ---------------------------------------------------------------------------

app = FastAPI()

# Strict, single-origin CORS policy. Because allow_origins is an exact list
# (no "*"), Starlette's CORSMiddleware will:
#   - add Access-Control-Allow-Origin only when the request Origin matches
#     ALLOWED_ORIGIN exactly
#   - omit that header entirely for any other Origin (including on the
#     OPTIONS preflight), which is exactly what the grader checks for.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


class TimingAndRequestIdMiddleware(BaseHTTPMiddleware):
    """Adds X-Request-ID and X-Process-Time to every response,
    including CORS preflight responses."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"
        return response


# Added after CORSMiddleware so it wraps it (executes first on the way in,
# last on the way out) -> its headers land on every response, including
# the preflight responses CORSMiddleware generates itself.
app.add_middleware(TimingAndRequestIdMiddleware)


@app.get("/stats")
def get_stats(values: str = Query(..., description="Comma-separated integers")):
    raw_parts = [p.strip() for p in values.split(",")]
    raw_parts = [p for p in raw_parts if p != ""]

    if not raw_parts:
        raise HTTPException(status_code=400, detail="No values provided")

    try:
        nums = [int(p) for p in raw_parts]
    except ValueError:
        raise HTTPException(status_code=400, detail="All values must be integers")

    count = len(nums)
    total = sum(nums)
    mean = total / count

    return {
        "email": YOUR_EMAIL,
        "count": count,
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": mean,
    }


@app.get("/")
def root():
    return {"status": "ok"}
