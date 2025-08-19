import os
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

@dataclass
class CustomAgentConfig:
    """Configuration for custom deployed agents"""
    name: str
    platform: str
    endpoint: str
    api_key: Optional[str]
    favorite_color: str
    timeout: int = 30
    retries: int = 3
    agent_type: str = "custom"  # "custom" for HTTP endpoints, "builtin" for SK agents
    
    @property
    def is_authenticated(self) -> bool:
        """Check if this agent requires authentication"""
        return self.api_key is not None and self.api_key != "" and not self.api_key.startswith("NONE")

@dataclass
class CustomAgentResponse:
    """Response from a custom agent"""
    cloud_platform: str
    agent_name: str
    favorite_color: str
    message: str
    success: bool
    error_message: Optional[str] = None

class CustomAgentClient:
    """Client for communicating with custom deployed agents"""
    
    def __init__(self, config: CustomAgentConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_message(self, message: str, task_context: str = "") -> CustomAgentResponse:
        """Send a message to the custom agent and get response"""
        
        if not self.session:
            raise RuntimeError("CustomAgentClient must be used as async context manager")
        
        # Prepare the request payload for JSON-RPC 2.0 format matching your agent's expected schema
        import uuid
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {
                            "text": message,
                            "metadata": {
                                "context": task_context,
                                "agent_info": {
                                    "name": self.config.name,
                                    "platform": self.config.platform,
                                    "favorite_color": self.config.favorite_color
                                },
                                "session_id": f"a2a_{self.config.platform}_{self.config.name}",
                                "timestamp": asyncio.get_event_loop().time()
                            }
                        }
                    ]
                }
            },
            "id": f"req_{asyncio.get_event_loop().time()}"
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SemanticKernel-Agent2Agent/1.0"
        }
        
        # Add authorization header only for authenticated agents
        if self.config.is_authenticated:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        last_error = None
        
        # Retry logic
        for attempt in range(self.config.retries):
            try:
                async with self.session.post(
                    self.config.endpoint,
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Extract response (customize based on your agent's response format)
                        agent_message = self._extract_message_from_response(response_data)
                        
                        return CustomAgentResponse(
                            cloud_platform=self.config.platform,
                            agent_name=self.config.name,
                            favorite_color=self.config.favorite_color,
                            message=agent_message,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        last_error = f"HTTP {response.status}: {error_text}"
                        
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.config.timeout} seconds"
            except aiohttp.ClientError as e:
                last_error = f"Client error: {str(e)}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
            
            if attempt < self.config.retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
        
        # All retries failed
        return CustomAgentResponse(
            cloud_platform=self.config.platform,
            agent_name=self.config.name,
            favorite_color=self.config.favorite_color,
            message=f"Failed to contact custom agent after {self.config.retries} attempts",
            success=False,
            error_message=last_error
        )
    
    def _extract_message_from_response(self, response_data: Dict[Any, Any]) -> str:
        """Extract the message from custom agent response"""
        
        # Try different common response formats
        if isinstance(response_data, dict):
            # JSON-RPC 2.0 format: {"jsonrpc": "2.0", "result": {...}, "id": "..."}
            if "jsonrpc" in response_data and "result" in response_data:
                result = response_data["result"]
                if isinstance(result, dict):
                    # Your agent's specific format: result.parts[0].text
                    if "parts" in result and isinstance(result["parts"], list) and len(result["parts"]) > 0:
                        first_part = result["parts"][0]
                        if isinstance(first_part, dict) and "text" in first_part:
                            return str(first_part["text"])
                    # Try common result formats
                    if "message" in result:
                        return str(result["message"])
                    if "response" in result:
                        return str(result["response"])
                    if "content" in result:
                        return str(result["content"])
                elif isinstance(result, str):
                    return str(result)
            
            # JSON-RPC error format
            if "jsonrpc" in response_data and "error" in response_data:
                return f"Agent error: {response_data['error']}"
            
            # Format 1: {"message": "response text"}
            if "message" in response_data:
                return str(response_data["message"])
            
            # Format 2: {"response": "response text"}
            if "response" in response_data:
                return str(response_data["response"])
            
            # Format 3: {"content": "response text"}
            if "content" in response_data:
                return str(response_data["content"])
            
            # Format 4: {"data": {"message": "response text"}}
            if "data" in response_data and isinstance(response_data["data"], dict):
                if "message" in response_data["data"]:
                    return str(response_data["data"]["message"])
            
            # Format 5: OpenAI-style response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return str(choice["message"]["content"])
        
        # Fallback: convert entire response to string
        return str(response_data)

class CustomAgentConfigLoader:
    """Loads custom agent configurations from environment variables"""
    
    @staticmethod
    def load_custom_agents() -> List[CustomAgentConfig]:
        """Load all agent configurations from environment variables (both custom HTTP and built-in SK agents)"""
        
        # Load custom agents environment file
        load_dotenv("custom_agents.env")
        
        agents = []
        
        # Define the platforms and their prefixes
        platforms = {
            "AWS": "AWS_AGENT_",
            "Azure": "AZURE_AGENT_",
            "GCP": "GCP_AGENT_",
            "Multi-Cloud": "MULTICLOUD_AGENT_",
            "BuiltIn": "BUILTIN_AGENT_"  # Add support for built-in SK agents
        }
        
        # Get timeout and retry settings
        timeout = int(os.getenv("CUSTOM_AGENT_TIMEOUT", "30"))
        retries = int(os.getenv("CUSTOM_AGENT_RETRIES", "3"))
        
        for platform_name, prefix in platforms.items():
            # Look for numbered agents (1, 2, 3, etc.)
            agent_num = 1
            while True:
                name_key = f"{prefix}{agent_num}_NAME"
                endpoint_key = f"{prefix}{agent_num}_ENDPOINT"
                api_key_key = f"{prefix}{agent_num}_API_KEY"
                color_key = f"{prefix}{agent_num}_COLOR"
                type_key = f"{prefix}{agent_num}_TYPE"
                
                name = os.getenv(name_key)
                endpoint = os.getenv(endpoint_key)
                api_key = os.getenv(api_key_key)
                color = os.getenv(color_key)
                agent_type = os.getenv(type_key, "custom").lower()  # Default to "custom", can be "builtin"
                
                # For built-in agents, endpoint is not required
                required_fields = [name, color]
                if agent_type == "custom":
                    required_fields.append(endpoint)
                
                # If any required field is missing, stop looking for more agents of this platform
                if not all(required_fields):
                    break
                
                # Skip if this looks like a placeholder (only for custom agents)
                if agent_type == "custom" and endpoint and endpoint.startswith("https://your-"):
                    agent_num += 1
                    continue
                
                # Handle unauthenticated agents (API key can be NONE, empty, or missing)
                if not api_key or api_key.upper() in ["NONE", "NULL", ""] or api_key.startswith("your-"):
                    api_key = None
                
                # For built-in agents, set endpoint to empty string
                if agent_type == "builtin":
                    endpoint = ""
                
                agents.append(CustomAgentConfig(
                    name=name,
                    platform=platform_name,
                    endpoint=endpoint,
                    api_key=api_key,
                    favorite_color=color,
                    timeout=timeout,
                    retries=retries,
                    agent_type=agent_type
                ))
                
                agent_num += 1
        
        return agents
    
    @staticmethod
    def should_use_custom_agents() -> bool:
        """Check if any agents should be loaded from configuration"""
        load_dotenv("custom_agents.env")
        return os.getenv("USE_CUSTOM_AGENTS", "false").lower() == "true"

# Example usage and testing functions
async def test_custom_agent_connection(config: CustomAgentConfig) -> bool:
    """Test connection to a custom agent"""
    try:
        async with CustomAgentClient(config) as client:
            response = await client.send_message(
                "Hello, this is a connection test from the Agent 2 Agent workflow.",
                "Testing connectivity and basic response capabilities."
            )
            return response.success
    except Exception as e:
        print(f"Test failed for {config.name}: {str(e)}")
        return False

async def test_all_custom_agents() -> Dict[str, bool]:
    """Test all configured custom agents"""
    agents = CustomAgentConfigLoader.load_custom_agents()
    results = {}
    
    for agent in agents:
        print(f"Testing {agent.name} on {agent.platform}...")
        success = await test_custom_agent_connection(agent)
        results[f"{agent.platform}-{agent.name}"] = success
        print(f"  {'✅ Success' if success else '❌ Failed'}")
    
    return results

if __name__ == "__main__":
    # Test the custom agent configuration loading
    agents = CustomAgentConfigLoader.load_custom_agents()
    print(f"Loaded {len(agents)} custom agents:")
    for agent in agents:
        print(f"  - {agent.name} ({agent.platform}) - {agent.favorite_color}")
    
    # Run connection tests
    print("\nTesting connections...")
    results = asyncio.run(test_all_custom_agents())
    print(f"\nTest Results: {results}")
