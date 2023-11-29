from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette_csrf import CSRFMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SessionMiddleware,
    secret_key="__secret__"
)

app.add_middleware(
    CSRFMiddleware,
    secret="__secret__",
    cookie_name="csrf_token",
    header_name="X-CSRF-Token",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def index(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    return response


@app.post("/secrets")
def api_secrets(request: Request):
    return {
        "detail": "Access Secret API successfully"
    }
