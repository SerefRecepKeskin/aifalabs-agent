from typing import Dict, Any
from llama_index.core import Settings
from agents import SupervisorAgent,CityAgent,ResearchAgent,ProductAgent 
from util.client import GeminiClient
from db.setup_database import setup_database
from util import logger
from session import SessionManager
from uuid import uuid4

from .engine import CustomChatEngine 
from .condense_query_engine import ImprovedCondenseQueryEngine

class AgentWorker:
    def __init__(self):
        # chat engine for processing prompts
        self.chat_engine = None
        self.supervisor = None
        self.condense_engine = None

        # create session manager object to manage sessions
        self._session_manager = SessionManager()
        logger.info("AgentWorker instance created")

    @classmethod
    async def create(cls) -> 'AgentWorker':
        """Factory method to create and initialize the AgentWorker."""
        logger.info("Creating AgentWorker using factory method")
        worker = cls()
        try:
            await worker.initialize()
            logger.info("AgentWorker initialization completed")
            return worker
        except Exception as e:
            logger.error(f"Failed to create AgentWorker: {str(e)}")
            raise


    async def initialize(self):
        try:
            # Initialize LLM
            logger.info("Initializing LLM client")
            llm = GeminiClient()
            Settings.llm = llm
            
            # Set up database
            logger.info("Setting up database connection")
            await setup_database()
            self.condense_engine= ImprovedCondenseQueryEngine(llm=Settings.llm)
            
            # Initialize agents
            logger.info("Initializing individual agents")

            city_agent = CityAgent()
            research_agent = ResearchAgent()
            product_agent = ProductAgent()
            
            self.agents = {
                "CityAgent": city_agent,
                "ResearchAgent": research_agent,
                "ProductAgent": product_agent
            }

            
            # Initialize supervisor agent
            logger.info("Initializing supervisor agent")

            self.supervisor = SupervisorAgent(agents=self.agents)
            logger.info("All agents initialized successfully")


            # Initialize chat engine with supervisor agent
            self.chat_engine = CustomChatEngine.from_defaults()                
            logger.info("Chat engine initialized successfully")

        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise



    
    async def process_chat(self, user_id: str, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process a chat message considering chat history and return the response with agent info."""
        try:
            logger.info(f"Processing chat message: '{user_message[:50]}...' if len(user_message) > 50 else user_message")

            # Get or create user session to get memory buffer object
            session = await self._session_manager.get_or_create_session(
                user_id,
                session_id
            )

            # Get chat history from the user session
            chat_history = session.get()

            condensed_query = await self.condense_engine.condense_question(user_message, chat_history)

            logger.debug("Routing query through supervisor agent")
            selected_agent = await self.supervisor.route_query(condensed_query)
            logger.info(f"Query routed to agent type: {type(selected_agent).__name__}")

            agent_response= None
            if selected_agent is not None:
                logger.debug(f"Processing query with selected agent")
                agent_response = await selected_agent.process_query(condensed_query)


            # get response by user message, agent response and chat history
            query_result = await self.chat_engine.achat(
                condensed_query,
                chat_history=chat_history,
                agent_response=agent_response
            )

            assistant_message = query_result.message.blocks[0].text


            # Save messages to session
            message_identifier = str(uuid4())
            await self._session_manager.save_messages(
                session_id=session_id,
                message_identifier=message_identifier,
                user_message=user_message,
                assistant_message=assistant_message
            )

            return {
                "response": assistant_message,
                "message_identifier": message_identifier
            }

        except Exception as e:
            logger.error(f"Unexpected error in process_chat: {str(e)}")
            return {
                "response": "I apologize, but something went wrong. Please try again later.",
                "message_identifier": message_identifier}
        
