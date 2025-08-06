"""
Multi-AI Provider Management System
Handles cycling through different AI providers when message limits are reached
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

class AIProvider:
    def __init__(self, name: str, api_key: str, base_url: str, model: str, daily_limit: int = 1000):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.daily_limit = daily_limit
        self.messages_used_today = 0
        self.last_reset = datetime.now().date()
        self.is_available = True
        self.last_error = None
    
    def reset_daily_counter(self):
        """Reset message counter if it's a new day"""
        if datetime.now().date() > self.last_reset:
            self.messages_used_today = 0
            self.last_reset = datetime.now().date()
            self.is_available = True
    
    def can_send_message(self) -> bool:
        """Check if this provider can send another message"""
        self.reset_daily_counter()
        return self.is_available and self.messages_used_today < self.daily_limit
    
    def send_message(self, message: str, context: List[Dict] = None) -> Dict:
        """Send message to this AI provider"""
        if not self.can_send_message():
            return {"error": f"Daily limit reached for {self.name}"}
        
        try:
            if self.name.lower() == "openai":
                return self._send_openai_message(message, context)
            elif self.name.lower() == "claude":
                return self._send_claude_message(message, context)
            elif self.name.lower() == "deepseek":
                return self._send_deepseek_message(message, context)
            else:
                return {"error": f"Unknown provider: {self.name}"}
        
        except Exception as e:
            self.last_error = str(e)
            logging.error(f"Error with {self.name}: {e}")
            return {"error": str(e)}
    
    def _send_openai_message(self, message: str, context: List[Dict] = None) -> Dict:
        """Send message to OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            self.messages_used_today += 1
            result = response.json()
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "provider": self.name,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            if "rate_limit" in response.text.lower():
                self.is_available = False
            return {"error": error_msg}
    
    def _send_claude_message(self, message: str, context: List[Dict] = None) -> Dict:
        """Send message to Claude API (Anthropic)"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert OpenAI format to Claude format
        claude_messages = []
        if context:
            for msg in context:
                if msg["role"] == "user":
                    claude_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    claude_messages.append({"role": "assistant", "content": msg["content"]})
        
        claude_messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "max_tokens": 2000,
            "messages": claude_messages
        }
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            self.messages_used_today += 1
            result = response.json()
            return {
                "success": True,
                "response": result["content"][0]["text"],
                "provider": self.name,
                "tokens_used": result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)
            }
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            if "rate_limit" in response.text.lower():
                self.is_available = False
            return {"error": error_msg}
    
    def _send_deepseek_message(self, message: str, context: List[Dict] = None) -> Dict:
        """Send message to DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = context or []
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            self.messages_used_today += 1
            result = response.json()
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "provider": self.name,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            if "rate_limit" in response.text.lower():
                self.is_available = False
            return {"error": error_msg}


class MultiAIManager:
    def __init__(self):
        self.providers: List[AIProvider] = []
        self.conversation_context: List[Dict] = []
        self.current_provider_index = 0
        self.max_context_length = 20  # Keep last 20 messages for context
    
    def add_provider(self, name: str, api_key: str, base_url: str, model: str, daily_limit: int = 1000):
        """Add a new AI provider to the rotation"""
        provider = AIProvider(name, api_key, base_url, model, daily_limit)
        self.providers.append(provider)
        logging.info(f"Added AI provider: {name}")
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of currently available providers"""
        return [p for p in self.providers if p.can_send_message()]
    
    def send_message(self, message: str, preserve_context: bool = True) -> Dict:
        """Send message using the best available AI provider"""
        if not self.providers:
            return {"error": "No AI providers configured"}
        
        available_providers = self.get_available_providers()
        if not available_providers:
            return {"error": "All AI providers have reached their daily limits"}
        
        # Try providers in order, starting from current index
        for i in range(len(available_providers)):
            provider_index = (self.current_provider_index + i) % len(available_providers)
            provider = available_providers[provider_index]
            
            # Send message with context
            context = self.conversation_context if preserve_context else None
            result = provider.send_message(message, context)
            
            if "error" not in result:
                # Success! Update context and current provider
                if preserve_context:
                    self.conversation_context.append({"role": "user", "content": message})
                    self.conversation_context.append({"role": "assistant", "content": result["response"]})
                    
                    # Trim context if too long
                    if len(self.conversation_context) > self.max_context_length:
                        self.conversation_context = self.conversation_context[-self.max_context_length:]
                
                self.current_provider_index = provider_index
                return result
            else:
                logging.warning(f"Provider {provider.name} failed: {result['error']}")
        
        return {"error": "All available providers failed to respond"}
    
    def get_provider_status(self) -> List[Dict]:
        """Get status of all providers"""
        status = []
        for provider in self.providers:
            provider.reset_daily_counter()
            status.append({
                "name": provider.name,
                "available": provider.is_available,
                "messages_used": provider.messages_used_today,
                "daily_limit": provider.daily_limit,
                "last_error": provider.last_error
            })
        return status
    
    def reset_conversation(self):
        """Clear conversation context"""
        self.conversation_context = []
        logging.info("Conversation context reset")
    
    def save_configuration(self, filepath: str):
        """Save provider configuration (without API keys for security)"""
        config = []
        for provider in self.providers:
            config.append({
                "name": provider.name,
                "base_url": provider.base_url,
                "model": provider.model,
                "daily_limit": provider.daily_limit
            })
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_configuration(self, filepath: str, api_keys: Dict[str, str]):
        """Load provider configuration and set API keys"""
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            
            for provider_config in config:
                name = provider_config["name"]
                if name.lower() in api_keys:
                    self.add_provider(
                        name=name,
                        api_key=api_keys[name.lower()],
                        base_url=provider_config["base_url"],
                        model=provider_config["model"],
                        daily_limit=provider_config["daily_limit"]
                    )
                else:
                    logging.warning(f"No API key provided for {name}")
        
        except FileNotFoundError:
            logging.warning(f"Configuration file {filepath} not found")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")


# Global AI manager instance
ai_manager = MultiAIManager()

def initialize_ai_providers():
    """Initialize AI providers with default configuration"""
    # These would be loaded from environment variables or secure config
    # For demo purposes, showing the structure
    
    # Example configuration - API keys should be loaded securely
    api_keys = {
        "openai": "your-openai-api-key",
        "claude": "your-claude-api-key", 
        "deepseek": "your-deepseek-api-key"
    }
    
    # Add providers
    ai_manager.add_provider(
        name="OpenAI",
        api_key=api_keys.get("openai", ""),
        base_url="https://api.openai.com/v1",
        model="gpt-4",
        daily_limit=1000
    )
    
    ai_manager.add_provider(
        name="Claude",
        api_key=api_keys.get("claude", ""),
        base_url="https://api.anthropic.com/v1",
        model="claude-3-sonnet-20240229",
        daily_limit=1000
    )
    
    ai_manager.add_provider(
        name="DeepSeek",
        api_key=api_keys.get("deepseek", ""),
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        daily_limit=1000
    )
    
    logging.info("AI providers initialized")

if __name__ == "__main__":
    # Test the system
    initialize_ai_providers()
    
    # Example usage
    result = ai_manager.send_message("Hello, can you help me automate my home?")
    print(f"Response: {result}")
    
    # Check provider status
    status = ai_manager.get_provider_status()
    print(f"Provider status: {status}")

