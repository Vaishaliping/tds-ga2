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
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okDHspNjgA+2rTLbeuY
cx1P/hGBC6Sb91wg3y1LAA4HCnpITchWCSe1bvbYGuc3EbNy4xFyF5Cbj5DHJMID
EkryQgvd2g1IIIBOUBJ8S63uGcnRpOBh9NFatFNwheKuzsRuVNldu6A9cNteNpXc
Wy3jG2axVfmq7lGSuKr13oWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcnNNo/WVfJ4xyCL5f0BCOgdTgW6PdaChd119VDetJZVEgCStkyVXsfI
SI6IyrYbKRNEB5qq4XkadEjsCs4F1Rncs54LlgnIT7GlkL9Mce3b0wGLs9/7ZIX
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
    try:
        payload = jwt.decode(
            body.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["exp", "iss", "aud"]},
        )
        return {
            "valid": True,
            "email": payload.get("email", ""),
            "sub": payload.get("sub", ""),
            "aud": payload.get("aud", ""),
        }
    except Exception:
        return JSONResponse(status_code=401, content={"valid": False})