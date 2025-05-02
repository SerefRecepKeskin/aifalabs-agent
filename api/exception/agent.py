from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

class AgentProcessingError(Exception):
    """Exception raised for errors during agent processing."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AgentNotFoundError(Exception):
    """Exception raised when a specified agent is not found."""
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.message = f"Agent '{agent_name}' not found"
        super().__init__(self.message)

async def agent_exception_handler(request: Request, exc: AgentProcessingError):
    """Handle agent processing errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )

async def agent_not_found_handler(request: Request, exc: AgentNotFoundError):
    """Handle agent not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )

def register_exception_handlers(app):
    """Register exception handlers with the FastAPI app."""
    app.add_exception_handler(AgentProcessingError, agent_exception_handler)
    app.add_exception_handler(AgentNotFoundError, agent_not_found_handler)
