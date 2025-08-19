#!/usr/bin/env python3
"""
Configuration management script for custom agents
"""

import os
import asyncio
from dotenv import load_dotenv, set_key
from custom_agent_client import CustomAgentConfigLoader, test_all_custom_agents

class CustomAgentConfigManager:
    """Manager for custom agent configuration"""
    
    def __init__(self):
        self.config_file = "custom_agents.env"
    
    def enable_custom_agents(self):
        """Enable custom agents in the workflow"""
        set_key(self.config_file, "USE_CUSTOM_AGENTS", "true")
        print("✅ Custom agents enabled")
    
    def disable_custom_agents(self):
        """Disable custom agents in the workflow"""
        set_key(self.config_file, "USE_CUSTOM_AGENTS", "false")
        print("✅ Custom agents disabled")
    
    def add_builtin_agent(self, platform: str, name: str, color: str):
        """Add a new built-in SK agent configuration"""
        
        # Find the next available slot for this platform
        agent_num = 1
        while True:
            prefix = self._get_platform_prefix(platform)
            if not prefix:
                print(f"❌ Invalid platform: {platform}")
                return
            
            name_key = f"{prefix}{agent_num}_NAME"
            if not os.getenv(name_key):
                break
            agent_num += 1
        
        # Add the built-in agent configuration
        type_key = f"{prefix}{agent_num}_TYPE"
        color_key = f"{prefix}{agent_num}_COLOR"
        
        set_key(self.config_file, name_key, name)
        set_key(self.config_file, type_key, "builtin")
        set_key(self.config_file, color_key, color)
        
        print(f"✅ Added built-in SK agent: {name} ({platform}) - {color}")
        print("   This agent will use your Azure OpenAI configuration")
    
    def add_custom_agent(self, platform: str, name: str, endpoint: str, api_key: str, color: str, authenticated: bool = True):
        """Add a new custom agent configuration"""
        
        # Find the next available slot for this platform
        platform_prefix = f"{platform.upper()}_AGENT_"
        agent_num = 1
        
        while True:
            name_key = f"{platform_prefix}{agent_num}_NAME"
            if not os.getenv(name_key):
                break
            agent_num += 1
        
        # Handle unauthenticated agents
        if not authenticated or not api_key or api_key.upper() in ["NONE", "NULL", ""]:
            api_key = "NONE"
        
        # Set the configuration
        set_key(self.config_file, f"{platform_prefix}{agent_num}_NAME", name)
        set_key(self.config_file, f"{platform_prefix}{agent_num}_ENDPOINT", endpoint)
        set_key(self.config_file, f"{platform_prefix}{agent_num}_API_KEY", api_key)
        set_key(self.config_file, f"{platform_prefix}{agent_num}_COLOR", color)
        
        auth_status = "Authenticated" if authenticated and api_key != "NONE" else "Unauthenticated"
        print(f"✅ Added custom agent: {name} ({platform}) - {color} ({auth_status})")
    
    def list_agents(self):
        """List all configured agents"""
        load_dotenv(self.config_file)
        
        use_custom = CustomAgentConfigLoader.should_use_custom_agents()
        
        print("🔧 Agent Configuration Status:")
        print(f"   Configuration Loading Enabled: {'✅ Yes' if use_custom else '❌ No'}")
        
        if use_custom:
            agents = CustomAgentConfigLoader.load_custom_agents()
            print(f"\n📋 Configured Agents ({len(agents)}):")
            
            custom_count = 0
            builtin_count = 0
            
            for i, agent in enumerate(agents, 1):
                if agent.agent_type == "custom":
                    custom_count += 1
                    endpoint_display = agent.endpoint[:50] + "..." if len(agent.endpoint) > 50 else agent.endpoint
                    auth_status = "🔐 Authenticated" if agent.is_authenticated else "🔓 Unauthenticated"
                    api_key_display = "Configured" if agent.is_authenticated else "Not Required"
                    
                    print(f"   {i}. {agent.name} (Custom HTTP Agent)")
                    print(f"      Platform: {agent.platform}")
                    print(f"      Color: {agent.favorite_color}")
                    print(f"      Endpoint: {endpoint_display}")
                    print(f"      Authentication: {auth_status}")
                    print(f"      API Key: {api_key_display}")
                    print()
                elif agent.agent_type == "builtin":
                    builtin_count += 1
                    print(f"   {i}. {agent.name} (Built-in SK Agent)")
                    print(f"      Platform: {agent.platform}")
                    print(f"      Color: {agent.favorite_color}")
                    print("      Uses: Your Azure OpenAI configuration")
                    print()
            
            print(f"📊 Summary: {custom_count} Custom Agents, {builtin_count} Built-in Agents")
        else:
            print("\n⚠️  No agents will be loaded. Set USE_CUSTOM_AGENTS=true to enable agents.")
    
    async def test_agents(self):
        """Test connectivity to all custom agents"""
        print("🧪 Testing Custom Agent Connectivity...")
        print("-" * 40)
        
        agents = CustomAgentConfigLoader.load_custom_agents()
        if not agents:
            print("⚠️  No custom agents configured to test")
            return
        
        results = await test_all_custom_agents()
        
        print("\n📊 Test Results Summary:")
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"   ✅ Successful: {success_count}/{total_count}")
        print(f"   ❌ Failed: {total_count - success_count}/{total_count}")
        
        if success_count < total_count:
            print("\n⚠️  Some agents failed connectivity tests.")
            print("   Please check your endpoints and API keys in custom_agents.env")

def show_menu():
    """Show the configuration menu"""
    print("\n🔧 Agent Configuration Manager")
    print("=" * 40)
    print("1. List all agents")
    print("2. Enable configuration loading")
    print("3. Disable configuration loading")
    print("4. Add custom HTTP agent (authenticated)")
    print("5. Add custom HTTP agent (unauthenticated)")
    print("6. Add built-in SK agent")
    print("7. Test agent connectivity")
    print("8. Show sample configuration")
    print("9. Show authentication help")
    print("10. Exit")
    print("-" * 40)

def show_sample_config():
    """Show sample configuration for custom agents"""
    print("\n📋 Sample Custom Agent Configuration:")
    print("=" * 50)
    print("""
# Example configuration for authenticated agents:
AWS_AGENT_1_NAME=MyCustomAWS-DataProcessor
AWS_AGENT_1_ENDPOINT=https://my-aws-agent.amazonaws.com/api/chat
AWS_AGENT_1_API_KEY=my-secret-api-key-123
AWS_AGENT_1_COLOR=Red

# Example configuration for unauthenticated agents:
AWS_AGENT_2_NAME=MyPublicAWS-Service
AWS_AGENT_2_ENDPOINT=https://my-public-agent.amazonaws.com/api/chat
AWS_AGENT_2_API_KEY=NONE
AWS_AGENT_2_COLOR=Green

# Alternative ways to specify unauthenticated agents:
# AWS_AGENT_3_API_KEY=          (empty)
# AWS_AGENT_3_API_KEY=NULL      (explicit null)

# Your agent should accept POST requests with JSON payload:
{
  "message": "task description",
  "context": "additional context",
  "agent_info": {
    "name": "agent name",
    "platform": "cloud platform",
    "favorite_color": "color"
  }
}

# Authenticated agents will receive:
# Headers: Authorization: Bearer <api-key>

# Unauthenticated agents will NOT receive authorization headers

# And return JSON response with:
{
  "message": "agent response text"
}
# OR
{
  "response": "agent response text"
}
# OR OpenAI-compatible format with choices array
""")

def show_auth_help():
    """Show help about authentication options"""
    print("\n🔐 Authentication Options:")
    print("=" * 30)
    print("""
AUTHENTICATED AGENTS:
- Require an API key for access
- API key sent in Authorization header as Bearer token
- More secure for production deployments
- Use when your agent requires authentication

UNAUTHENTICATED AGENTS:
- No API key required
- No authorization headers sent
- Good for public demos or internal testing
- Set API_KEY to "NONE", "NULL", or leave empty

SECURITY CONSIDERATIONS:
- Unauthenticated agents should have appropriate rate limiting
- Consider network-level security (VPC, firewall rules)
- Use HTTPS endpoints for all agents
- Monitor usage and implement abuse protection
""")

async def main():
    """Main configuration management function"""
    manager = CustomAgentConfigManager()
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-10): ").strip()
            
            if choice == "1":
                manager.list_agents()
            
            elif choice == "2":
                manager.enable_custom_agents()
            
            elif choice == "3":
                manager.disable_custom_agents()
            
            elif choice == "4":
                print("\nAdd Authenticated Custom HTTP Agent:")
                platform = input("Platform (AWS/Azure/GCP/Multi-Cloud): ").strip()
                name = input("Agent Name: ").strip()
                endpoint = input("API Endpoint URL: ").strip()
                api_key = input("API Key: ").strip()
                color = input("Favorite Color: ").strip()
                
                if all([platform, name, endpoint, api_key, color]):
                    manager.add_custom_agent(platform, name, endpoint, api_key, color, authenticated=True)
                else:
                    print("❌ All fields are required for authenticated agents")
            
            elif choice == "5":
                print("\nAdd Unauthenticated Custom HTTP Agent:")
                platform = input("Platform (AWS/Azure/GCP/Multi-Cloud): ").strip()
                name = input("Agent Name: ").strip()
                endpoint = input("API Endpoint URL: ").strip()
                color = input("Favorite Color: ").strip()
                
                if all([platform, name, endpoint, color]):
                    manager.add_custom_agent(platform, name, endpoint, "NONE", color, authenticated=False)
                else:
                    print("❌ All fields are required")
            
            elif choice == "6":
                print("\nAdd Built-in Semantic Kernel Agent:")
                platform = input("Platform (AWS/Azure/GCP/Multi-Cloud): ").strip()
                name = input("Agent Name: ").strip()
                color = input("Favorite Color: ").strip()
                
                if all([platform, name, color]):
                    manager.add_builtin_agent(platform, name, color)
                else:
                    print("❌ All fields are required")
            
            elif choice == "7":
                await manager.test_agents()
            
            elif choice == "8":
                show_sample_config()
            
            elif choice == "9":
                show_auth_help()
            
            elif choice == "10":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-10.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
