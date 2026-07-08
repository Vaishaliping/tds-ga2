import time
import uuid
import jwt
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── Q1 config ────────────────────────────────────────────────────────────────
EMAIL = "25ds3000064@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-jyb99d.example.com"

# ── Q2 config ────────────────────────────────────────────────────────────────
ISSUER   = "https://idp.exam.local"
AUDIENCE = "tds-jvsf5hjz.apps.exam.local"

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI()


# ── Middleware (Q1) ───────────────────────────────────────────────────────────
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start_time = time.time()
    origin = request.headers.get("origin", "")

    # Handle CORS preflight manually for strict per-origin policy
    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            response = Response(status_code=200)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
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
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    # Always add middleware headers
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.time() - start_time:.6f}"

    return response


# ── Root health check ─────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "endpoints": ["/stats", "/verify"]}


# ── Q1: Stats endpoint ────────────────────────────────────────────────────────
@app.get("/stats")
def get_stats(values: str = Query(..., description="Comma-separated integers")):
    nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    n = len(nums)
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": n,
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / n,
    }


# ── Q2: JWT verify endpoint ───────────────────────────────────────────────────
class TokenRequest(BaseModel):
    token: str


@app.post("/verify")
def verify_token(body: TokenRequest):
    # First decode WITHOUT verification to see raw claims (debug only)
    try:
        unverified = jwt.decode(
            body.token,
            options={"verify_signature": False},
            algorithms=["RS256"],
        )
    except Exception as e:
        return JSONResponse(status_code=401, content={"valid": False, "debug_error": f"Cannot decode token at all: {e}"})

    # Now verify properly
    try:
        payload = jwt.decode(
            body.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        return {
            "valid": True,
            "email": payload.get("email", ""),
            "sub": payload.get("sub", ""),
            "aud": payload.get("aud", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=401, content={
            "valid": False,
            "debug_error": str(e),
            "token_claims": unverified,   # shows what iss/aud/exp actually are
        })