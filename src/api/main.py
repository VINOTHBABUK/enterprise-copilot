from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from src.api.auth import authenticate, can_access_department
from src.api.observability import get_usage_stats, print_dashboard
from src.chat.router import route
from src.chat.app import execute_tool
from dotenv import load_dotenv
import time

load_dotenv()

app = FastAPI(
    title="Enterprise Copilot API",
    description="Enterprise AI Copilot — production backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class QueryRequest(BaseModel):
    message:    str
    username:   str
    password:   str
    department: Optional[str] = None


class ScrapeRequest(BaseModel):
    urls:       list
    department: str
    username:   str
    password:   str


@app.get("/")
def root():
    return {
        "name":    "Enterprise Copilot API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs"
    }


@app.post("/login")
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    return {
        "status":      "success",
        "name":        user["name"],
        "role":        user["role"],
        "departments": user["departments"]
    }


@app.post("/chat")
def chat(req: QueryRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if req.department:
        if not can_access_department(
            user["role"], req.department
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to department: {req.department}"
            )

    start   = time.time()
    routing = route(req.message, user_id=req.username)

    if req.department and routing["tool"] == "search_knowledge":
        routing["args"]["department"] = req.department

    response = execute_tool(routing["tool"], routing["args"])
    latency  = round((time.time() - start) * 1000)

    return {
        "answer":    response,
        "tool_used": routing["tool"],
        "user":      user["name"],
        "role":      user["role"],
        "latency_ms": latency
    }


@app.get("/stats")
def stats(username: str, password: str):
    user = authenticate(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return get_usage_stats()


@app.get("/health")
def health():
    return {
        "status":    "healthy",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )