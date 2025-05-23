from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import auth, routes, database
from jose import jwt
from database import Base, engine
from models import User, Log

app = FastAPI()

Base.metadata.create_all(bind=engine)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = database.SessionLocal()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/auth") or request.url.path.startswith("/me"):
        user = None
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            try:
                payload = jwt.decode(token.split(" ")[1], auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                user_id = payload.get("user_id")
                user = db.query(User).get(user_id)
            except:
                pass
        action = f"Запрос: {request.method} {request.url}"
        if user:
            db.add(Log(user_id=user.id, action=action))
            db.commit()
    return response

app.include_router(auth.router)
app.include_router(routes.router)

# @app.on_event("startup")
# async def startup_event():
#     await database.get_db()

# if __name__ == "__main__":
#     import uvicorn
#     asyncio.run(database.get_db())
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)