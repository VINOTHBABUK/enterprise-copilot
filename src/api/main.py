from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from src.api.auth import (
    login_user,
    register_user,
    get_user_from_token,
    can_access_department
)
from src.api.observability import get_usage_stats
from src.chat.router import route
from src.chat.app import execute_tool
from dotenv import load_dotenv
import time

load_dotenv()

app = FastAPI(
    title="Enterprise Copilot API",
    description="Enterprise AI Copilot — production backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


class LoginRequest(BaseModel):
    email:    str
    password: str


class RegisterRequest(BaseModel):
    email:       str
    name:        str
    password:    str
    role:        Optional[str] = "general"
    departments: Optional[list] = ["general"]


class QueryRequest(BaseModel):
    message:    str
    department: Optional[str] = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    user  = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    return user


@app.get("/")
def root():
    return {
        "name":    "Enterprise Copilot API",
        "version": "2.0.0",
        "status":  "running",
        "docs":    "/docs"
    }


@app.get("/health")
def health():
    return {
        "status":    "healthy",
        "timestamp": time.time()
    }


@app.post("/auth/register")
def register(req: RegisterRequest):
    user, error = register_user(
        email       = req.email,
        name        = req.name,
        password    = req.password,
        role        = req.role,
        departments = req.departments
    )
    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )
    return {
        "status":  "success",
        "message": f"User {req.email} registered successfully"
    }


@app.post("/auth/login")
def login(req: LoginRequest):
    token, error = login_user(req.email, req.password)
    if error:
        raise HTTPException(
            status_code=401,
            detail=error
        )
    return {
        "status": "success",
        "token":  token
    }


@app.post("/chat")
def chat(
    req:          QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    if req.department:
        if not can_access_department(
            current_user["role"],
            req.department
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to: {req.department}"
            )

    start   = time.time()
    routing = route(
        req.message,
        user_id=current_user["sub"]
    )

    if req.department and \
       routing["tool"] == "search_knowledge":
        routing["args"]["department"] = req.department

    response = execute_tool(
        routing["tool"],
        routing["args"]
    )
    latency = round((time.time() - start) * 1000)

    return {
        "answer":     response,
        "tool_used":  routing["tool"],
        "user":       current_user["name"],
        "role":       current_user["role"],
        "latency_ms": latency
    }


@app.get("/stats")
def stats(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return get_usage_stats()


@app.get("/users/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):
    return {
        "email":       current_user["sub"],
        "name":        current_user["name"],
        "role":        current_user["role"],
        "departments": current_user["departments"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )