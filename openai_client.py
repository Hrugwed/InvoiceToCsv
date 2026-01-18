"""
OpenAI API client wrapper for consistent API interactions.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from openai import OpenAI
from config import OPENAI_API_KEY, MAX_RETRIES, REQUEST_TIMEOUT


class OpenAIClient:
    """Wrapper for OpenAI API calls with error handling and retries."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        response_format: Optional[Dict[str, str]] = None,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Make a chat completion request with retries.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use
            response_format: Optional response format (e.g., {"type": "json_object"})
            temperature: Sampling temperature
            
        Returns:
            Response dictionary from OpenAI API
        """
        for attempt in range(MAX_RETRIES):
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "timeout": REQUEST_TIMEOUT,
                }
                
                if response_format:
                    kwargs["response_format"] = response_format
                
                response = self.client.chat.completions.create(**kwargs)
                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                }
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise RuntimeError(f"OpenAI API call failed after {MAX_RETRIES} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def vision_completion(
        self,
        image_path: Union[str, Path],
        prompt: str,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Make a vision API call for image analysis.
        
        Args:
            image_path: Path to image file or base64 encoded image
            prompt: Text prompt for the vision model
            model: Model name to use
            max_tokens: Maximum tokens in response
            
        Returns:
            Response dictionary from OpenAI API
        """
        import base64
        
        # Read and encode image
        if isinstance(image_path, Path):
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        else:
            base64_image = image_path
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ]
        
        return self.chat_completion(
            messages=messages,
            model=model,
            response_format={"type": "json_object"},
            temperature=0.0,
        )
    
    def parse_json_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse JSON response from OpenAI API.
        
        Args:
            response: Response dictionary from chat_completion
            
        Returns:
            Parsed JSON dictionary
        """
        content = response.get("content", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nContent: {content}")
