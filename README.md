# AI Multi-Domain Chatbot Agent

This project is a multi-domain chatbot designed to handle queries across various domains such as city/weather information, research topics, and product details. The chatbot leverages **LlamaIndex** for efficient query processing and response generation, ensuring high-quality and context-aware interactions. The architecture is modular, with specialized agents for each domain and a supervisor agent to route queries intelligently.

---

## ⚠️ Important Notes

1. **API Keys**:
   - Obtain a Weather API key from [WeatherAPI](https://www.weatherapi.com/).
   - Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

2. **Configuration**:
   - The configuration file (`config/default.json`) contains sensitive information such as API keys and database credentials. This setup is **not suitable for production** but is simplified for interview purposes to ensure the project runs easily.

3. **Security**:
   - A basic security measure is implemented by requiring an API key (`X-API-Key`) in the request headers for authentication. This is a minimal safeguard and should be enhanced for production environments.

---

## Project Overview

The chatbot is designed to:
- Handle user queries across multiple domains.
- Use **LlamaIndex** for query processing and response generation.
- Employ a supervisor agent to determine the best domain-specific agent for each query.
- Maintain session-based chat history for personalized responses.

### Key Features of LlamaIndex Integration
- **Query Condensation**: The chatbot uses LlamaIndex's `ImprovedCondenseQueryEngine` to condense user queries and chat history into a concise format for better processing.
- **Custom Chat Engine**: The `CustomChatEngine` built on LlamaIndex ensures efficient and context-aware response generation.
- **Scalability**: LlamaIndex's modular design allows seamless integration with multiple agents and external APIs.

---

## Project Structure

```
├── Dockerfile
├── docker-compose.yml
├── config
│   └── default.json          # Configuration file (API keys, database settings, etc.)
├── agents
│   ├── city_agent.py         # Handles city/weather-related queries
│   ├── product_agent.py      # Handles product-related queries
│   ├── research_agent.py     # Handles research-related queries
│   └── supervisor_agent.py   # Routes queries to the appropriate agent
├── api
│   ├── route
│   │   └── agent.py          # API routes for chatbot interactions
│   ├── schema
│   │   └── agent.py          # Request/response schemas
│   └── service
│       ├── agent.py          # Service layer for processing chat requests
│       └── auth.py           # Authentication service for API key validation
├── chatbot
│   ├── worker.py             # Core chatbot logic and session management
│   ├── engine.py             # Custom chat engine built on LlamaIndex
│   └── condense_query_engine.py # Query condensation logic using LlamaIndex
├── db
│   ├── connector.py          # Database connection utilities
│   ├── settings.py           # Database configuration settings
│   └── setup_database.py     # Database setup and initialization
├── external_api
│   ├── city_api.py           # External API integration for city/weather data
│   └── research_api.py       # External API integration for research data
├── prompt
│   ├── condense.py           # Prompt templates for query condensation
│   └── system.py             # System-level prompts for chatbot initialization
├── session
│   ├── manager.py            # Session management for chat history
│   └── store.py              # Session storage utilities
├── util
│   ├── client.py             # HTTP client utilities for external API calls
│   ├── log.py                # Logging configuration setup
│   ├── logger.py             # Logging utilities for the application
│   └── sting.py              # String manipulation utilities
├── test_api.py               # Script for testing the chatbot API
```

---

## Configuration

The `config/default.json` file contains the following settings:

```json
{
  "app": {
    "host": "0.0.0.0",
    "port": 7002,
    "version": "v1",
    "api_key": "temp_secret123"
  },
  "postgres": {
    "db_host": "localhost",
    "db_port": 5432,
    "db_name": "agentdb",
    "db_user": "postgres",
    "db_password": "postgres"
  },
  "gemini": {
    "api_key": "YOUR_GEMINI_API_KEY",
    "model": "gemini-2.0-flash",
    "max_tokens": 8192
  },
  "weather": {
    "api_key": "YOUR_WEATHER_API_KEY",
    "weatherapi_url": "http://api.weatherapi.com/v1/current.json"
  },
  "logging": {
    "level": "info",
    "file": "/var/log/promta.log"
  }
}
```

Replace `YOUR_GEMINI_API_KEY` and `YOUR_WEATHER_API_KEY` with the respective API keys.

---

## Schema Details

The `api/schema` directory contains the request and response schemas used by the API. These schemas ensure that the data exchanged between the client and server adheres to a predefined structure.

### Key Schemas

1. **MessageRequest**:
   - Represents the structure of the request payload for the `/chat` endpoint.
   - Fields:
     - `user_message` (str): The message sent by the user.
     - `user_identifier` (str): A unique identifier for the user.
     - `session_identifier` (str): A unique identifier for the chat session.

2. **MessageResult**:
   - Represents the structure of the response payload for the `/chat` endpoint.
   - Fields:
     - `bot_message` (str): The response message generated by the chatbot.
     - `message_identifier` (str): A unique identifier for the message.

---

## Health Check

The project includes a health check endpoint to verify that the API is running and operational.

### Endpoint

- **GET** `/health`
  - **Description**: Returns the status of the API.
  - **Response**:
    ```json
    {
      "status": "healthy",
      "message": "Service is running"
    }
    ```
  - **Usage**:
    - Use this endpoint to confirm that the API is up and running before sending other requests.

---

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.
- Python 3.12 installed locally (if running without Docker).

### Steps to Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/aifalabs-agent.git
   cd aifalabs-agent
   ```

2. **Set Up Configuration**:
   - Update `config/default.json` with your API keys and database credentials.

3. **Build and Run with Docker**:
   ```bash
   docker-compose up --build
   ```

4. **Access the API**:
   - The API will be available at `http://localhost:7002/api/v1/chat`.

5. **Test the API**:
   - Use the `test_api.py` script to send test requests:
     ```bash
     python test_api.py --message "Hello, how's the weather in New York?"
     ```

---

## Features

1. **LlamaIndex Integration**:
   - Efficient query condensation and response generation.
   - Custom chat engine for context-aware interactions.

2. **Multi-Domain Support**:
   - Handles queries about cities, weather, research topics, and products.

3. **Session Management**:
   - Maintains chat history for personalized responses.

4. **Modular Design**:
   - Each domain has a dedicated agent for better scalability and maintainability.

5. **Supervisor Agent**:
   - Routes queries to the most appropriate domain-specific agent.

6. **API Authentication**:
   - Requires an `X-API-Key` header for all requests.

---

## Security Considerations

- **API Key Authentication**:
  - All API requests must include a valid `X-API-Key` header.
  - This is a basic security measure and should be replaced with a more robust authentication mechanism in production.

- **Sensitive Data in Config**:
  - The current configuration includes sensitive data (e.g., API keys, database credentials). For production, use environment variables or a secrets management tool.

---

## Future Improvements

1. **Enhanced Security**:
   - Implement OAuth2 or JWT-based authentication.
   - Use encrypted secrets management for sensitive data.

2. **Scalability**:
   - Deploy the application on Kubernetes for better scalability and fault tolerance.

3. **Improved Agent Selection**:
   - Use machine learning models to improve the accuracy of agent selection.

4. **Monitoring and Logging**:
   - Integrate tools like Prometheus and Grafana for monitoring.
   - Use centralized logging with tools like ELK Stack.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---