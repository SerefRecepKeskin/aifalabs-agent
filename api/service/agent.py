from typing import Dict, Any
from llama_index.core import Settings
from agents import SupervisorAgent,CityAgent,ResearchAgent,ProductAgent 
from util.client import GeminiClient
from db.setup_database import setup_database
from util import logger

class AgentService:
    def __init__(self):
        self.agents = {}
        self.supervisor = None
        logger.info("AgentService instance created")

    @classmethod
    async def create(cls) -> 'AgentService':
        """Factory method to create and initialize the AgentService."""
        logger.info("Creating AgentService using factory method")
        service = cls()
        try:
            await service.initialize()
            logger.info("AgentService initialization completed")
            return service
        except Exception as e:
            logger.error(f"Failed to create AgentService: {str(e)}")
            raise
    
    async def initialize(self):
        try:
            # Initialize LLM
            logger.info("Initializing LLM client")
            llm = GeminiClient()
            Settings.llm = llm
            
            # Set up database
            logger.info("Setting up database connection")
            try:
                await setup_database()
            except Exception as db_error:
                logger.error(f"Database setup failed: {str(db_error)}")
                raise
            
            # Initialize agents
            logger.info("Initializing individual agents")
            try:
                city_agent = CityAgent()
                research_agent = ResearchAgent()
                product_agent = ProductAgent()
                
                self.agents = {
                    "CityAgent": city_agent,
                    "ResearchAgent": research_agent,
                    "ProductAgent": product_agent
                }
            except Exception as agent_error:
                logger.error(f"Failed to initialize agents: {str(agent_error)}")
                raise
            
            # Initialize supervisor agent
            logger.info("Initializing supervisor agent")
            try:
                self.supervisor = SupervisorAgent(agents=self.agents)
                logger.info("All agents initialized successfully")
            except Exception as supervisor_error:
                logger.error(f"Failed to initialize supervisor agent: {str(supervisor_error)}")
                raise
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise
    
    async def process_chat(self, message: str) -> Dict[str, Any]:
        """Process a chat message and return the response with agent info."""
        try:
            logger.info(f"Processing chat message: '{message[:50]}...' if len(message) > 50 else message")
            
            try:
                logger.debug("Routing query through supervisor agent")
                selected_agent = await self.supervisor.route_query(message)
                logger.info(f"Query routed to agent type: {type(selected_agent).__name__}")
            except Exception as routing_error:
                logger.error(f"Error routing query: {str(routing_error)}")
                return {
                    "response": "Sorry, I'm having trouble understanding your request right now.",
                    "agent_used": "Error",
                    "error": str(routing_error)
                }
            
            try:
                logger.debug(f"Processing query with selected agent")
                response = await selected_agent.process_query(message)
            except Exception as processing_error:
                logger.error(f"Error processing query: {str(processing_error)}")
                return {
                    "response": "Sorry, I encountered an issue while processing your request.",
                    "agent_used": type(selected_agent).__name__,
                    "error": str(processing_error)
                }
            
            # Determine which agent was used
            agent_used = None
            for name, agent in self.agents.items():
                if agent == selected_agent:
                    agent_used = name
                    break
            
            logger.info(f"Chat processing complete. Agent used: {agent_used}")
            logger.debug(f"Response generated: '{response[:50]}...' if len(response) > 50 else response")
            
            return {
                "response": response,
                "agent_used": agent_used
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in process_chat: {str(e)}")
            return {
                "response": "I apologize, but something went wrong. Please try again later.",
                "agent_used": "Error",
                "error": str(e)
            }
