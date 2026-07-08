import time
import uuid
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from typing import List

EMAIL = "25ds3000064@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-jyb99d.example.com"

app = FastAPI()


@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.time()

    # Handle CORS preflight (OPTIONS) manually for strict per-origin policy
    origin = request.headers.get("origin", "")

    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            response = Response(status_code=200)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["X-Request-ID"] = str(uuid.uuid4())
            response.headers["X-Process-Time"] = f"{time.time() - start_time:.6f}"
            return response
        else:
            # Reject preflight from other origins — no ACAO header
            response = Response(status_code=403)
            response.headers["X-Request-ID"] = str(uuid.uuid4())
            response.headers["X-Process-Time"] = f"{time.time() - start_time:.6f}"
            return response

    response = await call_next(request)

    # Add CORS header only for the allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    # Always add these middleware headers
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


@app.get("/stats")
def get_stats(values: str = Query(..., description="Comma-separated integers")):
    nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    n = len(nums)
    total = sum(nums)
    minimum = min(nums)
    maximum = max(nums)
    mean = total / n

    return {
        "email": EMAIL,
        "count": n,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "mean": mean,
    }