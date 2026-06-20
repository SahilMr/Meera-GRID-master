from fastapi import FastAPI
from src.router.query_router import router as query_router
from src.router.master_router import router as master_router
from src.router.chat_router import router as chat_router

app = FastAPI(
    title="MEERA API Backend",
    description="Backend service for MEERA application grid master.",
    version="1.0.0"
)

# Root status route
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "MEERA Backend",
        "version": "1.0.0"
    }

# Register API routers with v1 prefix
app.include_router(query_router, prefix="/api/v1")
app.include_router(master_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
