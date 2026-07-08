from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="TDS GA2 Q3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dash-jyb99d.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000"
}

yaml_cfg = {
    "workers": 6,
    "log_level": "debug",
    "api_key": "key-wk7261vvb1"
}

env_cfg = {
    "port": 8743,
    "workers": 3,
    "log_level": "debug",
    "api_key": "key-w6pw1siwto"
}

os_cfg = {
    "workers": 8,
    "debug": False,
    "log_level": "info",
    "api_key": "key-xle4yc7j1d"
}

def convert(v):
    s = str(v).lower()

    if s in ["true", "1", "yes", "on"]:
        return True

    if s in ["false", "0", "no", "off"]:
        return False

    try:
        return int(v)
    except:
        return v

@app.get("/")
def root():
    return {"message": "API Running"}

@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):

    cfg = defaults.copy()
    cfg.update(yaml_cfg)
    cfg.update(env_cfg)
    cfg.update(os_cfg)

    for item in set:
        key, value = item.split("=", 1)
        cfg[key] = convert(value)

    cfg["api_key"] = "****"

    return cfg