# Semantic Kernel Agent 2 Agent Protocol Demo

This console application demonstrates the implementation of Agent 2 Agent protocol using Microsoft Semantic Kernel with Azure OpenAI. The application supports both built-in AI agents and custom deployed agents across AWS, Azure, and GCP platforms.

## Features

- **Agent 2 Agent Protocol**: Implements Google's Agent 2 Agent communication protocol
- **Custom Agent Integration**: Connect to your own deployed AI agents across cloud platforms
- **Multi-Cloud Agents**: Built-in agents representing AWS, Azure, and GCP platforms
- **Configurable Workflow**: Mix and match custom and built-in agents
- **Sequential Workflow**: Tasks are delegated across agents in sequence
- **Unique Agent Identities**: Each agent has a unique human name and favorite rainbow color
- **Response Aggregation**: Collects and summarizes responses from all agents
- **Error Handling**: Graceful handling of agent failures with fallback responses

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Azure OpenAI**:
   - Update the `.env` file with your Azure OpenAI credentials:
     - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
     - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
     - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your GPT model deployment name
     - `AZURE_OPENAI_API_VERSION`: API version (default: 2024-11-20)

3. **Configure Custom Agents** (Optional):
   ```bash
   python config_manager.py
   ```
   
   Or manually edit `custom_agents.env` to add your deployed agents.

4. **Run the Application**:
   ```bash
   python main.py
   ```

## Custom Agent Configuration

### Adding Custom Agents

You can integrate your own deployed AI agents using the configuration manager:

```bash
python config_manager.py
```

This interactive tool allows you to:
- Add custom agent endpoints
- Enable/disable custom agents
- Test agent connectivity
- View configuration status

### Manual Configuration

Edit `custom_agents.env` to add your agents:

```env
# Enable custom agents
USE_CUSTOM_AGENTS=true
USE_BUILTIN_AGENTS=true

# AWS Custom Agent Example
AWS_AGENT_1_NAME=MyCustomAWS-DataProcessor
AWS_AGENT_1_ENDPOINT=https://my-aws-agent.amazonaws.com/api/chat
AWS_AGENT_1_API_KEY=your-api-key
AWS_AGENT_1_COLOR=Red
```

### Custom Agent API Requirements

Your deployed agents should accept POST requests with this JSON structure:

```json
{
  "message": "task description",
  "context": "additional context",
  "agent_info": {
    "name": "agent name",
    "platform": "cloud platform", 
    "favorite_color": "color"
  },
  "metadata": {
    "timestamp": 1234567890,
    "session_id": "session_id"
  }
}
```

And return responses in one of these formats:

```json
{"message": "response text"}
{"response": "response text"}  
{"content": "response text"}
{"data": {"message": "response text"}}
```

Or OpenAI-compatible format with `choices` array.

## Agents

### Built-in Agents (Semantic Kernel + Azure OpenAI)

1. **Alexandra** (AWS) - Favorite Color: Red
2. **Benjamin** (Azure) - Favorite Color: Orange  
3. **Catherine** (GCP) - Favorite Color: Yellow
4. **David** (AWS) - Favorite Color: Green
5. **Elena** (Azure) - Favorite Color: Blue
6. **Francis** (GCP) - Favorite Color: Indigo
7. **Gabriel** (Multi-Cloud) - Favorite Color: Violet

### Custom Agent Support

- **AWS**: Amazon EC2, ECS, Lambda deployments
- **Azure**: App Service, Container Instances, Functions
- **GCP**: Cloud Run, Compute Engine, Cloud Functions
- **Multi-Cloud**: Cross-platform orchestrators

## Workflow

1. **Agent Discovery**: Load configured custom and built-in agents
2. **Task Delegation**: Main task is delegated to each agent sequentially
3. **Agent Processing**: Each agent processes the task while maintaining their identity
4. **Response Collection**: Responses are collected from both custom and built-in agents
5. **Aggregation**: Final report aggregates all agent responses with platform and type information

## Configuration Options

### Agent Workflow Settings

- `USE_CUSTOM_AGENTS`: Enable/disable custom deployed agents
- `USE_BUILTIN_AGENTS`: Enable/disable built-in Semantic Kernel agents
- `CUSTOM_AGENT_TIMEOUT`: Timeout for custom agent requests (seconds)
- `CUSTOM_AGENT_RETRIES`: Number of retry attempts for failed requests

### Testing and Management

- **Test Setup**: `python test_setup.py`
- **Demo Mode**: `python demo.py` (no API keys required)
- **Config Manager**: `python config_manager.py`
- **Connectivity Test**: Built into config manager

## Output

The application produces:
- Real-time progress updates during workflow execution
- Agent type identification (Custom vs Built-in)
- Individual agent responses with cloud platform and favorite color
- Final aggregated report summarizing all agent contributions
- Cloud platform grouping and summary statistics
- Error handling and fallback responses for failed agents
