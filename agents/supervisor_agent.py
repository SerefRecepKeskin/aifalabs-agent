from typing import Dict, List, Any
from .base_agent import BaseAgent
from util import logger

SUPERVISOR_PROMPT = """You are a supervisor for a multi-domain chatbot. Your job is to determine which specialized agent
should handle a user query. The available agents are:

1. City and Weather Agent: Handles questions about cities and weather conditions
2. Research Agent: Handles questions about research topics and academic information
3. Product Agent: Handles questions about products in our database

For the given user query, determine which agent is most appropriate to handle it.
Respond only with the agent name: "CityAgent", "ResearchAgent", or "ProductAgent".
"""

class SupervisorAgent(BaseAgent):
    """Agent responsible for routing queries to the appropriate domain-specific agent"""
    
    def __init__(self, agents: Dict[str, BaseAgent]):
        super().__init__(system_prompt=SUPERVISOR_PROMPT)
        self.agents = agents
        logger.info("SupervisorAgent initialized with %d agents", len(agents))
        
    async def route_query(self, query: str) -> BaseAgent:
        """Determine which agent should handle the query"""
        logger.info("Routing query: '%s'", query)
        # First approach: Ask each agent for its confidence score
        confidence_scores = {}
        for name, agent in self.agents.items():
            confidence_scores[name] = await agent.can_handle(query)
            logger.debug("Agent '%s' confidence: %.2f", name, confidence_scores[name])
            
        # Get the agent with the highest confidence
        selected_agent = max(confidence_scores, key=confidence_scores.get)
        if confidence_scores[selected_agent] <= 0:
            logger.warning("No agent found with sufficient confidence for query: '%s'", query)
            return None
        logger.info("Selected agent '%s' with confidence %.2f", selected_agent, confidence_scores[selected_agent])
        return self.agents[selected_agent]
        
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a query by routing to the appropriate agent"""
        logger.info("Processing query: '%s'", query)
        agent = await self.route_query(query)
        logger.debug("Delegating query to %s", agent.__class__.__name__)
        response = await agent.process_query(query, context)
        logger.debug("Got response from %s", agent.__class__.__name__)
        return response
        
    async def can_handle(self, query: str) -> float:
        """Supervisor can handle all queries"""
        logger.debug("SupervisorAgent can_handle called (always returns 1.0)")
        return 1.0