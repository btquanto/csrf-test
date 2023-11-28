import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SessionMiddleware,
    secret_key="__secret__",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        dict(
            detail=exc.detail,
            session_csrf_token=request.session.get("csrf_token", "N/A"),
            cookies_csrf_token=request.cookies.get("csrf_token", "N/A"),
        ),
        status_code=403, 
    )


# Create a depends function to check authentication header
def require_csrf(request: Request):
    if "X-CSRF-Token" not in request.headers:
        raise HTTPException(status_code=403, detail="Missing CSRF Token")
    csrf_token = request.headers["X-CSRF-Token"]
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")
    return True


def generate_csrf_token(request: Request):
    if "csrf_token" not in request.session:
        csrf_token = secrets.token_urlsafe(16)
        request.session["csrf_token"] = csrf_token
    else:
        csrf_token = request.session["csrf_token"]
    return csrf_token


@app.get("/")
def index(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    return response


@app.get("/get_csrf_token")
def get_csrf_token(response: Response, csrf_token: str = Depends(generate_csrf_token)):
    response.set_cookie(
        "csrf_token", csrf_token, samesite="lax", httponly=True, secure=True
    )
    return {"csrf_token": csrf_token}


@app.post("/secrets", dependencies=[Depends(require_csrf)])
def api_secrets(request: Request):
    return {
        "detail": "Access Secret API successfully",
        "session_csrf_token": request.session.get("csrf_token", "N/A"),
        "cookies_csrf_token": request.cookies.get("csrf_token", "N/A"),
    }
