# Semantic Kernel Agent 2 Agent Protocol Demo

This console application demonstrates the implementation of Agent 2 Agent protocol using Microsoft Semantic Kernel with Azure OpenAI. The application creates multiple AI agents representing different cloud platforms (AWS, Azure, GCP) that collaborate on tasks.

## Features

- **Agent 2 Agent Protocol**: Implements Google's Agent 2 Agent communication protocol
- **Multi-Cloud Agents**: Agents representing AWS, Azure, and GCP platforms
- **Sequential Workflow**: Tasks are delegated across agents in sequence
- **Unique Agent Identities**: Each agent has a unique human name and favorite rainbow color
- **Response Aggregation**: Collects and summarizes responses from all agents

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Azure OpenAI**:
   - Copy the `.env` file and update with your Azure OpenAI credentials:
     - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
     - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
     - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT model deployment name
     - `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)

3. **Run the Application**:
   ```bash
   python main.py
   ```

## Agents

The application creates 7 agents across cloud platforms:

1. **Alexandra** (AWS) - Favorite Color: Red
2. **Benjamin** (Azure) - Favorite Color: Orange  
3. **Catherine** (GCP) - Favorite Color: Yellow
4. **David** (AWS) - Favorite Color: Green
5. **Elena** (Azure) - Favorite Color: Blue
6. **Francis** (GCP) - Favorite Color: Indigo
7. **Gabriel** (Multi-Cloud) - Favorite Color: Violet

## Workflow

1. **Task Delegation**: Main task is delegated to each agent sequentially
2. **Agent Processing**: Each agent processes the task while maintaining their identity
3. **Response Collection**: Responses are collected and stored
4. **Aggregation**: Final report aggregates all agent responses with platform and color information

## Output

The application produces:
- Real-time progress updates during workflow execution
- Individual agent responses with cloud platform and favorite color
- Final aggregated report summarizing all agent contributions
- Cloud platform grouping and summary statistics
