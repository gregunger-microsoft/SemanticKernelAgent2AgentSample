import asyncio
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory

# Import custom agent support
from custom_agent_client import (
    CustomAgentClient, 
    CustomAgentConfig, 
    CustomAgentConfigLoader
)

# Load environment variables
load_dotenv()

@dataclass
class AgentResponse:
    """Represents a response from an AI agent"""
    cloud_platform: str
    agent_name: str
    favorite_color: str
    message: str

class CustomCloudAgent:
    """Wrapper for custom deployed agents that integrates with the Agent 2 Agent workflow"""
    
    def __init__(self, config: CustomAgentConfig):
        self.config = config
        self.cloud_platform = config.platform
        self.agent_name = config.name
        self.favorite_color = config.favorite_color
    
    async def process_task(self, task: str) -> AgentResponse:
        """Process a task using the custom deployed agent"""
        
        try:
            async with CustomAgentClient(self.config) as client:
                # Create a comprehensive prompt for the custom agent
                enhanced_task = f"""
                You are {self.agent_name}, an AI agent deployed on {self.cloud_platform} cloud platform.
                Your favorite color from the rainbow is {self.favorite_color}.
                
                Task: {task}
                
                Please respond as {self.agent_name} and make sure to mention:
                1. Your cloud platform ({self.cloud_platform})
                2. Your name ({self.agent_name})
                3. Your favorite color ({self.favorite_color})
                4. Complete the given task using your specific expertise
                
                Keep your response concise and in character. Focus on how your {self.cloud_platform} deployment 
                capabilities contribute to solving this task.
                """
                
                custom_response = await client.send_message(enhanced_task)
                
                if custom_response.success:
                    return AgentResponse(
                        cloud_platform=self.cloud_platform,
                        agent_name=self.agent_name,
                        favorite_color=self.favorite_color,
                        message=custom_response.message
                    )
                else:
                    # Fallback message if custom agent fails
                    fallback_message = f"""
                    I am {self.agent_name}, a custom AI agent deployed on {self.cloud_platform}. 
                    My favorite color is {self.favorite_color}. Unfortunately, I'm currently experiencing 
                    connectivity issues, but I would contribute my {self.cloud_platform}-specific expertise 
                    to help with: {task}
                    
                    Error: {custom_response.error_message}
                    """
                    
                    return AgentResponse(
                        cloud_platform=self.cloud_platform,
                        agent_name=self.agent_name,
                        favorite_color=self.favorite_color,
                        message=fallback_message
                    )
        
        except Exception as e:
            # Handle any unexpected errors
            error_message = f"""
            I am {self.agent_name}, a custom AI agent on {self.cloud_platform}. 
            My favorite color is {self.favorite_color}. I encountered an unexpected error 
            while processing the task: {str(e)}
            """
            
            return AgentResponse(
                cloud_platform=self.cloud_platform,
                agent_name=self.agent_name,
                favorite_color=self.favorite_color,
                message=error_message
            )

class CloudAgent:
    """Base class for cloud platform agents implementing Agent 2 Agent protocol"""
    
    def __init__(self, kernel: Kernel, cloud_platform: str, agent_name: str, favorite_color: str):
        self.kernel = kernel
        self.cloud_platform = cloud_platform
        self.agent_name = agent_name
        self.favorite_color = favorite_color
        self.chat_history = ChatHistory()
    
    @kernel_function(
        description="Get agent information and favorite color",
        name="get_agent_info"
    )
    async def get_agent_info(self) -> str:
        """Returns agent information including cloud platform, name, and favorite color"""
        return f"I am {self.agent_name}, an AI agent running on {self.cloud_platform}. My favorite color is {self.favorite_color}."
    
    async def process_task(self, task: str) -> AgentResponse:
        """Process a task and return agent response"""
        
        # Add the agent's function to the kernel
        self.kernel.add_function(
            plugin_name=f"{self.cloud_platform.lower()}_agent",
            function=self.get_agent_info
        )
        
        # Create a prompt for the agent
        prompt = f"""
        You are {self.agent_name}, an AI agent running on {self.cloud_platform} cloud platform.
        Your favorite color from the rainbow is {self.favorite_color}.
        
        Task: {task}
        
        Please respond as {self.agent_name} and mention:
        1. Your cloud platform ({self.cloud_platform})
        2. Your name ({self.agent_name})
        3. Your favorite color ({self.favorite_color})
        4. Complete the given task
        
        Keep your response concise and in character.
        """
        
        # Get chat completion service
        chat_completion = self.kernel.get_service(type=AzureChatCompletion)
        
        # Add the prompt to chat history
        self.chat_history.add_user_message(prompt)
        
        # Get response with function calling enabled
        result = await chat_completion.get_chat_message_content(
            chat_history=self.chat_history,
            settings=chat_completion.get_prompt_execution_settings_class()(
                function_choice_behavior=FunctionChoiceBehavior.Auto()
            ),
            kernel=self.kernel
        )
        
        # Add response to chat history
        self.chat_history.add_assistant_message(str(result))
        
        return AgentResponse(
            cloud_platform=self.cloud_platform,
            agent_name=self.agent_name,
            favorite_color=self.favorite_color,
            message=str(result)
        )

class Agent2AgentWorkflow:
    """Implements Agent 2 Agent protocol workflow for multi-cloud task delegation"""
    
    def __init__(self):
        self.kernel = self._setup_kernel()
        self.agents = self._create_agents()
        self.workflow_history: List[AgentResponse] = []
    
    def _setup_kernel(self) -> Kernel:
        """Setup Semantic Kernel with Azure OpenAI"""
        kernel = Kernel()
        
        # Add Azure OpenAI chat completion service
        kernel.add_service(
            AzureChatCompletion(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
        )
        
        return kernel
    
    def _create_agents(self) -> List:
        """Create agents from configuration file - no hardcoded agents"""
        agents = []
        
        # Load agent configuration
        use_custom = CustomAgentConfigLoader.should_use_custom_agents()
        
        if use_custom:
            print("🔧 Loading agents from configuration...")
            agent_configs = CustomAgentConfigLoader.load_custom_agents()
            
            for config in agent_configs:
                if config.agent_type == "custom":
                    # Create custom HTTP agent
                    agents.append(CustomCloudAgent(config))
                    auth_status = "🔐 Authenticated" if config.is_authenticated else "🔓 Unauthenticated"
                    print(f"   ✅ Added custom agent: {config.name} ({config.platform}) - {config.favorite_color} - {auth_status}")
                elif config.agent_type == "builtin":
                    # Create built-in SK agent
                    agents.append(CloudAgent(self.kernel, config.platform, config.name, config.favorite_color))
                    print(f"   ✅ Added built-in agent: {config.name} ({config.platform}) - {config.favorite_color}")
        
        if len(agents) == 0:
            print("⚠️  No agents configured. Please check your custom_agents.env file and set USE_CUSTOM_AGENTS=true")
        
        print(f"📊 Total agents in workflow: {len(agents)}")
        return agents
    
    async def execute_workflow(self, main_task: str) -> List[AgentResponse]:
        """Execute the Agent 2 Agent workflow across all cloud platforms"""
        print(f"🚀 Starting Agent 2 Agent Workflow: {main_task}")
        print("=" * 60)
        
        all_responses = []
        
        # Phase 1: Task delegation to each agent sequentially
        for i, agent in enumerate(self.agents, 1):
            if isinstance(agent, CustomCloudAgent):
                auth_status = "🔐 Auth" if agent.config.is_authenticated else "🔓 No Auth"
                agent_type = f"Custom ({auth_status})"
            else:
                agent_type = "Built-in SK"
            
            print(f"\n📋 Step {i}: Delegating to {agent.agent_name} ({agent_type}) on {agent.cloud_platform}")
            
            # Create specific sub-task for each agent
            sub_task = f"""
            As part of a multi-cloud workflow, please:
            1. Introduce yourself with your cloud platform and favorite color
            2. Contribute to this main task: {main_task}
            3. Prepare a handoff message for the next agent in the workflow
            4. Mention your specific deployment capabilities on {agent.cloud_platform}
            """
            
            try:
                response = await agent.process_task(sub_task)
                all_responses.append(response)
                self.workflow_history.append(response)
                
                print(f"✅ {agent.agent_name} ({agent.cloud_platform}) completed their task")
                print(f"   Agent Type: {agent_type}")
                print(f"   Favorite Color: {agent.favorite_color}")
                print(f"   Response: {response.message[:100]}...")
                
            except Exception as e:
                print(f"❌ Error with {agent.agent_name}: {str(e)}")
                
                # Create error response to maintain workflow continuity
                error_response = AgentResponse(
                    cloud_platform=agent.cloud_platform,
                    agent_name=agent.agent_name,
                    favorite_color=agent.favorite_color,
                    message=f"Agent {agent.agent_name} encountered an error: {str(e)}"
                )
                all_responses.append(error_response)
                continue
        
        # Phase 2: Workflow aggregation
        print(f"\n🔄 Aggregating responses from {len(all_responses)} agents...")
        
        return all_responses
    
    def generate_final_report(self, responses: List[AgentResponse]) -> str:
        """Generate final aggregated report from all agent responses"""
        report = "\n" + "=" * 60
        report += "\n🌈 FINAL AGENT 2 AGENT WORKFLOW REPORT"
        report += "\n" + "=" * 60
        
        # Count agent types
        custom_count = sum(1 for agent in self.agents if isinstance(agent, CustomCloudAgent))
        builtin_count = len(self.agents) - custom_count
        
        report += f"\n\n📊 Total Agents Participated: {len(responses)}"
        report += f"\n   🔧 Custom Deployed Agents: {custom_count}"
        report += f"\n   🤖 Built-in SK Agents: {builtin_count}"
        report += "\n\n🌟 Agent Summary:"
        
        for i, response in enumerate(responses, 1):
            # Determine agent type
            agent = next((a for a in self.agents if a.agent_name == response.agent_name), None)
            if isinstance(agent, CustomCloudAgent):
                auth_status = " - 🔐 Authenticated" if agent.config.is_authenticated else " - 🔓 Unauthenticated"
                agent_type = f"Custom{auth_status}"
            else:
                agent_type = "Built-in SK"
            
            report += f"\n\n{i}. Agent: {response.agent_name} ({agent_type})"
            report += f"\n   Cloud Platform: {response.cloud_platform}"
            report += f"\n   Favorite Color: {response.favorite_color}"
            report += f"\n   Message: {response.message}"
        
        # Group by cloud platform
        cloud_summary = {}
        for response in responses:
            if response.cloud_platform not in cloud_summary:
                cloud_summary[response.cloud_platform] = []
            cloud_summary[response.cloud_platform].append(response)
        
        report += "\n\n☁️ Cloud Platform Summary:"
        for cloud, agents in cloud_summary.items():
            report += f"\n\n{cloud}:"
            for agent_response in agents:
                agent = next((a for a in self.agents if a.agent_name == agent_response.agent_name), None)
                agent_type = "Custom" if isinstance(agent, CustomCloudAgent) else "Built-in"
                report += f"\n  - {agent_response.agent_name} ({agent_type}) - Color: {agent_response.favorite_color}"
        
        return report

async def main():
    """Main function to run the Agent 2 Agent workflow"""
    print("🤖 Semantic Kernel Agent 2 Agent Protocol Demo")
    print("=" * 50)
    
    # Initialize the workflow
    workflow = Agent2AgentWorkflow()
    
    # Define the main task
    main_task = "Create a collaborative rainbow-themed presentation where each agent contributes their expertise from their respective cloud platform"
    
    try:
        # Execute the workflow
        responses = await workflow.execute_workflow(main_task)
        
        # Generate and display final report
        final_report = workflow.generate_final_report(responses)
        print(final_report)
        
        print(f"\n✨ Workflow completed successfully with {len(responses)} agent responses!")
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        print("Please check your Azure OpenAI configuration in the .env file")

if __name__ == "__main__":
    asyncio.run(main())
