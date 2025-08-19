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

# Load environment variables
load_dotenv()

@dataclass
class AgentResponse:
    """Represents a response from an AI agent"""
    cloud_platform: str
    agent_name: str
    favorite_color: str
    message: str

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
    
    def _create_agents(self) -> List[CloudAgent]:
        """Create agents for different cloud platforms with unique names and colors"""
        rainbow_colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"]
        
        agents = [
            CloudAgent(self.kernel, "AWS", "Alexandra", rainbow_colors[0]),
            CloudAgent(self.kernel, "Azure", "Benjamin", rainbow_colors[1]), 
            CloudAgent(self.kernel, "GCP", "Catherine", rainbow_colors[2]),
            CloudAgent(self.kernel, "AWS", "David", rainbow_colors[3]),
            CloudAgent(self.kernel, "Azure", "Elena", rainbow_colors[4]),
            CloudAgent(self.kernel, "GCP", "Francis", rainbow_colors[5]),
            CloudAgent(self.kernel, "Multi-Cloud", "Gabriel", rainbow_colors[6])
        ]
        
        return agents
    
    async def execute_workflow(self, main_task: str) -> List[AgentResponse]:
        """Execute the Agent 2 Agent workflow across all cloud platforms"""
        print(f"🚀 Starting Agent 2 Agent Workflow: {main_task}")
        print("=" * 60)
        
        all_responses = []
        
        # Phase 1: Task delegation to each agent sequentially
        for i, agent in enumerate(self.agents, 1):
            print(f"\n📋 Step {i}: Delegating to {agent.agent_name} on {agent.cloud_platform}")
            
            # Create specific sub-task for each agent
            sub_task = f"""
            As part of a multi-cloud workflow, please:
            1. Introduce yourself with your cloud platform and favorite color
            2. Contribute to this main task: {main_task}
            3. Prepare a handoff message for the next agent in the workflow
            """
            
            try:
                response = await agent.process_task(sub_task)
                all_responses.append(response)
                self.workflow_history.append(response)
                
                print(f"✅ {agent.agent_name} ({agent.cloud_platform}) completed their task")
                print(f"   Favorite Color: {agent.favorite_color}")
                print(f"   Response: {response.message[:100]}...")
                
            except Exception as e:
                print(f"❌ Error with {agent.agent_name}: {str(e)}")
                continue
        
        # Phase 2: Workflow aggregation
        print(f"\n🔄 Aggregating responses from {len(all_responses)} agents...")
        
        return all_responses
    
    def generate_final_report(self, responses: List[AgentResponse]) -> str:
        """Generate final aggregated report from all agent responses"""
        report = "\n" + "=" * 60
        report += "\n🌈 FINAL AGENT 2 AGENT WORKFLOW REPORT"
        report += "\n" + "=" * 60
        
        report += f"\n\n📊 Total Agents Participated: {len(responses)}"
        report += "\n\n🌟 Agent Summary:"
        
        for i, response in enumerate(responses, 1):
            report += f"\n\n{i}. Agent: {response.agent_name}"
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
            for agent in agents:
                report += f"\n  - {agent.agent_name} (Color: {agent.favorite_color})"
        
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
