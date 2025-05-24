import os
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY не найден в переменных окружения")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
        logger.info("Gemini client инициализирован")

    def generate_manim_code(self, user_request: str) -> str:
        """Генерирует код Manim на основе запроса пользователя"""
        prompt = f"""
Ты - эксперт по библиотеке Manim для создания математических анимаций. 
Пользователь просит: {user_request}

Напиши ТОЛЬКО код Python с использованием Manim, который создаст видео согласно запросу.
Требования:
1. Класс должен наследоваться от Scene
2. Используй self.play() для анимаций
3. Добавь self.wait() в конце
4. Не добавляй никаких комментариев или объяснений
5. Код должен быть готов к выполнению
6. Импортируй все необходимые модули из manim
7. ВАЖНО: Предпочитай Text() вместо MathTex() для текста, так как MathTex требует LaTeX
8. Для математических формул используй обычный Text() с Unicode символами или простые геометрические фигуры

Пример структуры:
```python
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Используй Text() для текста
        title = Text("a² + b² = c²")
        # Используй простые фигуры для визуализации
        square = Square()
        self.play(Write(title))
        self.play(Create(square))
        self.wait()
```

Создай видео для запроса: {user_request}
"""

        logger.info(f"Отправляю запрос в Gemini: {user_request}")
        response = self.model.generate_content(prompt)
        
        # Извлекаем код из ответа
        code = response.text.strip()
        
        # Убираем markdown форматирование если есть
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        logger.info("Код Manim сгенерирован успешно")
        return code 