from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid

app = FastAPI()

EMAIL = "23f3003796@ds.study.iitm.ac.in"

start_time = time.time()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)

logs = []


@app.middleware("http")
async def middleware(request: Request, call_next):
    http_requests_total.inc()

    request_id = str(uuid.uuid4())

    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    })

    if len(logs) > 1000:
        logs.pop(0)

    response = await call_next(request)
    return response


@app.get("/work")
def work(n: int = 1):
    return {
        "email": EMAIL,
        "done": n,
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - start_time,
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return logs[-limit:]
