# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from event_api.routes import router

# app = FastAPI(title="QuickCart Event Gateway")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://localhost:5174"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(router)


# @app.get("/")
# def health_check():
#     return {
#         "status": "QuickCart Event Gateway Running"
#     }


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from event_api.routes.product_routes import router as product_router
from event_api.routes.auth_routes import router as auth_router
from event_api.routes.order_routes import router as order_router
from event_api.routes.activity_routes import router as activity_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product APIs
app.include_router(product_router)

# Authentication APIs
app.include_router(auth_router)

# Order APIs
app.include_router(order_router)

app.include_router(activity_router)

# --- ADD THIS BACK IN ---
@app.get("/")
def health_check():
    """
    Root endpoint to verify the API is online.
    """
    return {"status": "QuickCart API is running!"}