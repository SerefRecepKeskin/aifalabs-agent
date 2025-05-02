from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.route.agent import chat_router
from chatbot.worker import AgentWorker
from api.exception.agent import register_exception_handlers
from config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services on startup
    app.state.agent_worker = await AgentWorker.create()
    yield
    # Clean up resources if needed

app = FastAPI(
    title="Multi-Domain Chatbot",
    description="API for interacting with specialized domain agents",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
prefix = f'/api/{config.app.version}'
app.include_router(chat_router, prefix=prefix)

if __name__ == "__main__":
    uvicorn.run(app, host=config.app.host, port=config.app.port)
