# Manim Video Generator

🎬 CLI инструмент для автоматического создания видеороликов с использованием Gemini 2.5 Flash Thinking и Manim.

## 🚀 Быстрый старт

### Установка

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd manim-gpt

# 2. Установите системные зависимости (macOS)
brew install cairo pango pkg-config ffmpeg

# 3. Установите Python зависимости
pip install -r requirements.txt
pip install -e .

# 4. Настройте API ключ
cp env.example .env
# Отредактируйте .env и добавьте ваш GEMINI_API_KEY
```

### Первый запуск

```bash
# Простая анимация
manim-generate "Создай анимацию движущегося круга"

# С просмотром кода
manim-generate "Анимация квадрата" --show-code
```

### Результат

Видео сохраняется в папку `output/` с уникальным именем вида `video_<timestamp>.mp4`.

### Примеры запросов

- "Создай анимацию теоремы Пифагора"
- "Покажи как работает сортировка пузырьком" 
- "Анимация синусоиды"
- "Движение планет вокруг солнца"
- "Демонстрация интеграла"

## Возможности

- 🤖 Использует Gemini 2.5 Flash Thinking для анализа запросов
- 🎥 Автоматически генерирует код Manim
- 🔒 Безопасное выполнение в изолированной среде
- 📱 Простой CLI интерфейс
- 📊 Поддержка различных типов математических анимаций

## Подробная установка

### Предварительные требования

На macOS:
```bash
# Установите системные зависимости
brew install cairo pango pkg-config ffmpeg

# Для математических формул (опционально)
brew install --cask mactex-no-gui
```

На Ubuntu/Debian:
```bash
sudo apt update
sudo apt install libcairo2-dev libpango1.0-dev pkg-config ffmpeg

# Для математических формул (опционально)
sudo apt install texlive-latex-base texlive-latex-extra
```

В Docker/контейнерах (Ubuntu):
```bash
# Добавьте в Dockerfile:
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

На Windows:
- Установите [ffmpeg](https://ffmpeg.org/download.html)
- Для cairo/pango можно использовать [MSYS2](https://www.msys2.org/)
- Для LaTeX установите [MikTeX](https://miktex.org/) или [TeX Live](https://www.tug.org/texlive/)

### Установка проекта

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd manim-gpt
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите пакет:
```bash
pip install -e .
```

4. Настройте API ключ Gemini:
```bash
cp env.example .env
# Отредактируйте .env и добавьте ваш GEMINI_API_KEY
```

## Альтернативная установка с Docker

Если у вас проблемы с системными зависимостями, используйте Docker:

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd manim-gpt

# 2. Соберите образ
docker build -t manim-video-generator .

# 3. Запустите контейнер
docker run -e GEMINI_API_KEY=your_api_key_here \
           -v $(pwd)/output:/app/output \
           manim-video-generator "Создай анимацию движущегося круга"
```

Видео будет сохранено в папку `output/` на хосте.

## Использование

### Основная команда

```bash
manim-generate "Ваш запрос на создание видео"
```

### Примеры

```bash
# Математические концепции
manim-generate "Создай анимацию теоремы Пифагора"
manim-generate "Покажи как работает интеграл функции x^2"
manim-generate "Анимация производной синуса"

# Алгоритмы
manim-generate "Анимация сортировки пузырьком"
manim-generate "Покажи как работает бинарный поиск"

# Физика
manim-generate "Анимация гармонических колебаний"
manim-generate "Покажи закон всемирного тяготения"

# Геометрия
manim-generate "Постройка правильного пятиугольника"
manim-generate "Трансформация окружности в квадрат"
```

### Опции

- `--output-dir, -o`: Папка для сохранения видео (по умолчанию: `output`)
- `--api-key`: API ключ Gemini (альтернатива переменной окружения)
- `--scene-name`: Имя класса сцены (по умолчанию: `VideoScene`)
- `--show-code`: Показать сгенерированный код перед выполнением

### Примеры с опциями

```bash
# Сохранить в конкретную папку
manim-generate "Анимация квадратичной функции" -o /path/to/videos

# Показать код перед выполнением
manim-generate "Теорема Ферма" --show-code

# Использовать другой API ключ
manim-generate "Интеграция по частям" --api-key your_api_key_here
```

## Получение API ключа Gemini

1. Перейдите на [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Создайте новый API ключ
3. Добавьте его в файл `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Структура проекта

```
manim-gpt/
├── manim_video_generator/
│   ├── __init__.py          # Основной пакет
│   ├── cli.py               # CLI интерфейс
│   ├── gemini_client.py     # Клиент для Gemini API
│   └── video_executor.py    # Выполнение кода Manim
├── requirements.txt         # Зависимости
├── setup.py                # Установка пакета
├── env.example             # Пример переменных окружения
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose
├── test_example.py         # Тесты без API
├── test_manim_execution.py # Тест рендеринга
└── README.md               # Документация
```

## Тестирование

### Базовые тесты (без API)
```bash
python test_example.py
```

### Тест рендеринга Manim
```bash
python test_manim_execution.py
```

### Полный тест с Gemini API
```bash
# Убедитесь, что у вас есть .env файл с API ключом
manim-generate "простая анимация с кругом"
```

## Troubleshooting

### Нет API ключа
```bash
# Получите ключ на: https://aistudio.google.com/app/apikey
# Добавьте в .env файл:
echo "GEMINI_API_KEY=your_key_here" > .env
```

### Ошибка "GEMINI_API_KEY не найден"
Убедитесь, что создали файл `.env` с вашим API ключом или передали его через опцию `--api-key`.

### Ошибка "manim command not found"
Убедитесь, что Manim установлен корректно:
```bash
pip install manim
manim --version
```

### Ошибка "Invalid value for '-q'"
Эта ошибка уже исправлена в коде. Убедитесь, что вы переустановили пакет после исправлений:
```bash
pip install -e .
```

### Ошибки компиляции pycairo на macOS
```bash
brew install cairo pango pkg-config
pip install --force-reinstall pycairo
```

### Проблемы с numpy
```bash
pip install --force-reinstall scipy numpy
```

### Ошибки рендеринга ffmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Ошибка "No such file or directory: 'latex'"
Эта ошибка возникает, когда сгенерированный код использует MathTex, но LaTeX не установлен:

```bash
# macOS
brew install --cask mactex-no-gui

# Ubuntu/Debian  
sudo apt install texlive-latex-base texlive-latex-extra

# После установки перезапустите терминал
```

Альтернативно, программа автоматически предпочитает Text() вместо MathTex(), но для сложных математических формул LaTeX все же рекомендуется.

### Ошибки установки системных зависимостей

#### "Package 'pangocairo' was not found" (Linux)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install libcairo2-dev libpango1.0-dev pkg-config

# CentOS/RHEL/Fedora
sudo yum install cairo-devel pango-devel pkgconfig
# или для новых версий:
sudo dnf install cairo-devel pango-devel pkgconfig
```

#### Проблемы в CI/Docker
Используйте готовый Dockerfile или добавьте в свой:
```dockerfile
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

#### Быстрое решение с Docker
```bash
docker build -t manim-video-generator .
docker run -e GEMINI_API_KEY=your_key \
           -v $(pwd)/output:/app/output \
           manim-video-generator "ваш запрос"
```

## Качество видео

По умолчанию используется среднее качество (`-q m`). Доступные опции:
- `l` - низкое качество (480p)
- `m` - среднее качество (720p) 
- `h` - высокое качество (1080p)
- `p` - 4K качество
- `k` - 8K качество

Чтобы изменить качество, отредактируйте файл `manim_video_generator/video_executor.py`, строку с `-q m`.

## Лицензия

MIT License