import os
from dotenv import load_dotenv
import litellm

class llmCall:
    def __init__(self, model="gemini/gemini-2.5-pro", temperature=0.2, max_tokens=1000):
        """Initialize the chat agent and load API key"""
        # Load variables from .env into the system environment
        load_dotenv()
        
        # Ensure the API key exists
        self.api_key = os.getenv("ASTRO1221_API_KEY")
        if not self.api_key:
            raise ValueError("API Key not found! Did you forget your .env file?")
        
        # State management
        self.model = model
        self.history = [
            {"role": "system", "content": "You are a helpful astronomy research assistant."}
        ]

        # 4. Set the proxy server
        self.api_base = "https://litellmproxy.osu-ai.org"

    def ask_llm(self, user_input):
        """Sends a message to the LLM and updates history."""
        # Add user message to history
        self.history.append({"role": "user", "content": user_input})
        
        # Call LiteLLM (it automatically looks at the environment variables)
        response = litellm.completion(
            model=self.model,
            messages=self.history,
            api_base=self.api_base,
            api_key=self.api_key,
            temperature=0.2,
            max_tokens=1000
        )
        
        # Extract the answer
        answer = response.choices[0].message.content
        
        # Add assistant response to history to maintain context
        self.history.append({"role": "assistant", "content": answer})
        
        return answer