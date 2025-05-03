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
    "db_host": "postgres",
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
  "wikipedia": {
    "base_url": "https://en.wikipedia.org/api/rest_v1/page/summary/"
  },
  "research": {
    "semantic_scholar_url": "https://api.semanticscholar.org/graph/v1/paper/search",
    "google_scholar_url": "https://scholar.google.com/scholar",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "results_limit": 5
  },
  "logging": {
    "level": "info",
    "file": "/var/log/promta.log"
  }
}
```

Replace `YOUR_GEMINI_API_KEY` and `YOUR_WEATHER_API_KEY` with the respective API keys.

---

## External API Integrations

The system integrates with several external APIs to enhance the chatbot's knowledge and capabilities:

### 1. Weather API
- **Provider**: WeatherAPI.com
- **Purpose**: Retrieves current weather information for cities around the world
- **Integration**: The City Agent uses this API to answer weather-related questions
- **Endpoints Used**: `/current.json` - Provides current weather data
- **Data Retrieved**: Temperature, weather conditions, humidity, wind speed, and other meteorological data
- **Configuration**: Requires an API key from WeatherAPI.com

### 2. Wikipedia API
- **Provider**: Wikimedia REST API
- **Purpose**: Retrieves factual information about topics, places, people, etc.
- **Integration**: Used to provide general knowledge information to supplement agent responses
- **Endpoints Used**: `/page/summary/` - Provides concise summaries of Wikipedia articles
- **Data Retrieved**: Article summaries, descriptions, and basic facts
- **Configuration**: No API key required, but requests are rate-limited

### 3. Research APIs
- **Provider**: Multiple sources (Semantic Scholar and Google Scholar)
- **Purpose**: Retrieves academic papers and research information
- **Integration**: The Research Agent uses these APIs to answer academic and research-related questions
- **Endpoints Used**:
  - Semantic Scholar: `/paper/search` - Searches for academic papers
  - Google Scholar: Web scraping with appropriate user agent
- **Data Retrieved**: Paper titles, authors, abstracts, publication dates, and citation information
- **Configuration**: 
  - Semantic Scholar doesn't require an API key for basic usage
  - Google Scholar access is configured with an appropriate user agent to avoid blocking

### API Usage Notes
- The system implements rate limiting and caching to avoid overloading external APIs
- Error handling is in place to gracefully handle API unavailability or rate limiting
- Results from external APIs are processed and contextualized before being presented to users
- External API responses are combined with the LLM's knowledge to provide comprehensive answers

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

## Database Setup

The project uses PostgreSQL for data persistence. The database is automatically initialized during the first startup through the `setup_database.py` script.

### Database Tables

1. **products**: Stores product information used by the Product Agent
   - `id`: Serial primary key
   - `name`: Product name (VARCHAR)
   - `description`: Product description (TEXT)
   - `price`: Product price (DECIMAL)
   - `created_at`: Creation timestamp

2. **chat_history**: Stores user conversation history
   - `id`: Serial primary key
   - `user_id`: Identifier for the user (VARCHAR)
   - `session_id`: Identifier for the chat session (VARCHAR)
   - `messages`: JSON array of chat messages (JSONB)
   - `updated_at`: Last update timestamp

### Initialization Process

On first run, the system:
1. Creates necessary tables if they don't exist
2. Creates appropriate indexes on frequently queried columns
3. Populates the products table with sample data (only if the table is empty)

Sample products include:
- Smartphone X
- Laptop Pro
- Wireless Earbuds
- Smart Watch
- Coffee Maker

The database setup process is logged for troubleshooting purposes.

### Database Configuration

Database connection settings are specified in the `config/default.json` file:

```json
"postgres": {
  "db_host": "localhost",
  "db_port": 5432,
  "db_name": "agentdb",
  "db_user": "postgres",
  "db_password": "postgres"
}
```

For production environments, it's recommended to:
- Use environment variables for credentials
- Implement database connection pooling
- Set up regular database backups
- Configure proper user permissions

---

## Postman Collection

A Postman collection is included in the project to help you test the API endpoints easily. The collection provides pre-configured requests for each feature of the API.

### Importing the Collection

1. **Download Postman**:
   - Download and install Postman from [https://www.postman.com/downloads/](https://www.postman.com/downloads/)

2. **Import the Collection**:
   - Open Postman
   - Click on "Import" in the top-left corner
   - Select "File" > "Upload Files" and choose the `postman_collection.json` file from the project directory
   - Click "Import" to add the collection to your Postman workspace

### Using the Collection

1. **Configure Environment Variables**:
   - The collection uses a variable `{{base_url}}` which is set to `http://localhost:7002` by default
   - You can modify this in the "Variables" section of the collection if your API is hosted elsewhere

2. **Available Endpoints**:
   - **Health Check**: Tests if the API is up and running
   - **Chat with Research Agent**: Send research-related queries
   - **Chat with Product Agent**: Send product-related queries
   - **Chat with City Agent**: Send city/weather-related queries

3. **Testing the Endpoints**:
   - Select any request from the collection
   - Review and modify the request body if needed
   - Click the "Send" button to make the request
   - The response will be displayed in the lower section of the Postman interface

4. **Authentication**:
   - All requests include the `X-API-Key` header set to `temp_secret123` by default
   - Update this value if you've changed the API key in your configuration

### Example Usage

To test the weather information functionality:
1. Select the "Chat with City Agent" request
2. In the request body, change the message to something like: "What's the weather like in Tokyo today?"
3. Click "Send"
4. Review the response from the chatbot in the response panel

This collection is particularly useful for:
- Testing API functionality
- Understanding the request/response format
- Debugging integration issues
- Demonstrating the API capabilities to others

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