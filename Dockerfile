FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY env.example .
COPY manim_video_generator/ ./manim_video_generator/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Создаем папку для вывода
RUN mkdir -p /app/output

# Устанавливаем точку входа
ENTRYPOINT ["manim-generate"]

# Пример использования:
# docker build -t manim-video-generator .
# docker run -e GEMINI_API_KEY=your_key -v $(pwd)/output:/app/output manim-video-generator "Создай анимацию круга" 