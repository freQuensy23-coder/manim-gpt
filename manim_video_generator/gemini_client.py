import os
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv
from typing import Optional, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from .context_manager import ConversationContext

load_dotenv()


class GeminiClient:
    def __init__(self, api_key: str = None, context_manager: Optional['ConversationContext'] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
        self.context_manager = context_manager
        logger.info("Gemini client initialized")

    def generate_manim_code(self, user_request: str) -> str:
        """Generate Manim code based on the user's request"""
        
        # Системный промпт с инструкциями
        system_prompt = """You are a Manim code generator. Your ONLY task is to generate executable Python code using the Manim library.

CRITICAL RULES:
- You MUST respond with ONLY Python code, nothing else
- NO explanations, NO text, NO comments outside the code
- The code MUST be ready to execute immediately
- The response should start with "from manim import *" and contain a complete Scene class

CODE REQUIREMENTS:
1. Always import: from manim import *
2. Create a class that inherits from Scene (default name: VideoScene)
3. Implement the construct(self) method
4. Use self.play() for animations
5. End with self.wait(1) or self.wait(2)
6. Use Text() instead of MathTex() for all text (MathTex requires LaTeX setup)
7. For mathematical formulas, use Text() with Unicode symbols: ², ³, ∫, ∑, π, etc.
8. Use simple geometric shapes: Square(), Circle(), Rectangle(), Line(), etc.
9. Common animations: Write(), Create(), Transform(), FadeIn(), FadeOut(), DrawBorderThenFill()
10. Position objects with .move_to(), .shift(), .to_edge(), .next_to()

EXAMPLE OUTPUT FORMAT (this is exactly how your response should look):
```python
from manim import *

class VideoScene(Scene):
    def construct(self):
        title = Text("Example Title")
        self.play(Write(title))
        self.wait(2)
```

IMPORTANT: 
- Your entire response must be valid Python code
- Do not include any text before or after the code
- If the request is in any language other than English, still generate code with English variable names and comments
- Focus on creating visually appealing animations that demonstrate the requested concept"""

        # Получаем контекст предыдущих сообщений
        messages = []
        if self.context_manager:
            messages = self.context_manager.get_context_for_gemini()
        
        # Добавляем системный промпт и текущий запрос если истории нет
        if not messages:
            messages = [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\nCreate a video for the request: {user_request}"}]}
            ]

        # Debug логирование полного контекста
        logger.debug(f"Sending {len(messages)} messages to Gemini:")
        for i, message in enumerate(messages):
            logger.debug(f"Message {i+1} ({message['role']}): {message['parts'][0]['text'][:200]}{'...' if len(message['parts'][0]['text']) > 200 else ''}")

        logger.info(f"Sending request to Gemini with {len(messages)} context messages")
        response = self.model.generate_content(messages)
        
        # Extract code from the response
        code = response.text.strip()
        
        # Улучшенное извлечение кода
        if code.startswith("```python"):
            # Стандартный случай: код начинается с ```python
            code = code[9:]
            if code.endswith("```"):
                code = code[:-3]
        elif code.startswith("```"):
            # Код начинается с ```
            code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
        else:
            # Ищем первый блок кода внутри текста
            python_match = re.search(r'```python\s*\n(.*?)\n```', code, re.DOTALL)
            if python_match:
                code = python_match.group(1)
            else:
                # Ищем любой блок ```
                code_match = re.search(r'```\s*\n(.*?)\n```', code, re.DOTALL)
                if code_match:
                    code = code_match.group(1)
                # Если нет блоков кода, оставляем как есть (весь ответ)
        
        code = code.strip()
        logger.info("Manim code generated successfully")
        return code

    def fix_manim_code(self, current_code: str, error_trace: str, user_hint: str | None = None) -> str:
        """Fix Manim code using the error trace and optional user hint"""
        
        # Получаем контекст
        messages = []
        if self.context_manager:
            messages = self.context_manager.get_context_for_gemini()
        
        # Если контекста нет, создаем базовое сообщение
        if not messages:
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
            messages = [{"role": "user", "parts": [{"text": prompt}]}]

        # Debug логирование полного контекста
        logger.debug(f"Sending {len(messages)} messages to Gemini for code fix:")
        for i, message in enumerate(messages):
            logger.debug(f"Message {i+1} ({message['role']}): {message['parts'][0]['text'][:200]}{'...' if len(message['parts'][0]['text']) > 200 else ''}")

        logger.info("Sending code fix request to Gemini")
        response = self.model.generate_content(messages)

        fixed = response.text.strip()

        # Улучшенное извлечение кода
        if fixed.startswith("```python"):
            # Стандартный случай: код начинается с ```python
            fixed = fixed[9:]
            if fixed.endswith("```"):
                fixed = fixed[:-3]
        elif fixed.startswith("```"):
            # Код начинается с ```
            fixed = fixed[3:]
            if fixed.endswith("```"):
                fixed = fixed[:-3]
        else:
            # Ищем первый блок кода внутри текста
            python_match = re.search(r'```python\s*\n(.*?)\n```', fixed, re.DOTALL)
            if python_match:
                fixed = python_match.group(1)
            else:
                # Ищем любой блок ```
                code_match = re.search(r'```\s*\n(.*?)\n```', fixed, re.DOTALL)
                if code_match:
                    fixed = code_match.group(1)
                # Если нет блоков кода, оставляем как есть (весь ответ)

        fixed = fixed.strip()
        logger.info("Received fixed code from Gemini")
        return fixed
