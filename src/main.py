from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.router.query_router import router as query_router
from src.router.master_router import router as master_router
from src.router.chat_router import router as chat_router
from src.db.init_db import init_db
from src.core.singletons import get_faiss_index

# Initialize database and tables
init_db()

# Cold boot FAISS and Embedding singletons on startup
get_faiss_index()

app = FastAPI(
    title="MEERA API Backend",
    description="Backend service for MEERA application grid master.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)