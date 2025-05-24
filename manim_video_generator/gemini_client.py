import os
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
        logger.info("Gemini client initialized")

    def generate_manim_code(self, user_request: str) -> str:
        """Generate Manim code based on the user's request"""
        prompt = f"""
You are an expert on the Manim library for creating mathematical animations.
The user requests: {user_request}

Write ONLY Python code using Manim that will create the requested video.
Requirements:
1. The class must inherit from Scene
2. Use self.play() for animations
3. Add self.wait() at the end
4. Do not add any comments or explanations
5. The code must be ready to run
6. Import all required modules from manim
7. IMPORTANT: Prefer Text() instead of MathTex() since MathTex requires LaTeX
8. For math formulas use plain Text() with Unicode characters or simple shapes

Example structure:
```python
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Use Text() for text
        title = Text("a² + b² = c²")
        # Use simple shapes for visualization
        square = Square()
        self.play(Write(title))
        self.play(Create(square))
        self.wait()
```

Create a video for the request: {user_request}
"""

        logger.info(f"Sending request to Gemini: {user_request}")
        response = self.model.generate_content(prompt)
        
        # Extract code from the response
        code = response.text.strip()
        
        # Remove markdown formatting if present
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        logger.info("Manim code generated successfully")
        return code

    def fix_manim_code(self, current_code: str, error_trace: str, user_hint: str | None = None) -> str:
        """Fix Manim code using the error trace and optional user hint"""
        hint_block = f"\nUser hint: {user_hint}" if user_hint else ""
        prompt = f"""
You are an assistant that helps fix errors in Manim code.

Current code:
```python
{current_code}
```

Execution error:
{error_trace}
{hint_block}

Provide the corrected code. Return ONLY the Python code without explanations.
"""

        logger.info("Sending code fix request to Gemini")
        response = self.model.generate_content(prompt)

        fixed = response.text.strip()

        if fixed.startswith("```python"):
            fixed = fixed[9:]
        if fixed.startswith("```"):
            fixed = fixed[3:]
        if fixed.endswith("```"):
            fixed = fixed[:-3]

        fixed = fixed.strip()
        logger.info("Received fixed code from Gemini")
        return fixed
