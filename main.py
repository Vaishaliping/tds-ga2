from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

env_file = {
    "port": 8743,
    "workers": 3,
    "log_level": "debug",
    "api_key": "key-w6pw1siwto"
}

os_env = {
    "workers": 8,
    "debug": False,
    "log_level": "info",
    "api_key": "key-xle4yc7j1d"
}

def convert(v):
    if isinstance(v, bool):
        return v
    s = str(v).lower()
    if s in ["true","1","yes","on"]:
        return True
    if s in ["false","0","no","off"]:
        return False
    try:
        return int(v)
    except:
        return v

@app.get("/effective-config")
def config(set: List[str] = Query(default=[])):
    cfg = defaults.copy()
    cfg.update(yaml_cfg)
    cfg.update(env_file)
    cfg.update(os_env)

    for item in set:
        k, v = item.split("=",1)
        cfg[k] = convert(v)

    cfg["api_key"] = "****"
    return cfg