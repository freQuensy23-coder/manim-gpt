import click
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from .gemini_client import GeminiClient
from .video_executor import VideoExecutor

load_dotenv('.env')  # Ищем .env в текущей директории

# Настройка логирования
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


@click.command()
@click.argument('request', required=True)
@click.option('--output-dir', '-o', default='output', help='Папка для сохранения видео')
@click.option('--api-key', help='API ключ Gemini (или используйте переменную окружения GEMINI_API_KEY)')
@click.option('--scene-name', default='VideoScene', help='Имя класса сцены в сгенерированном коде')
@click.option('--show-code', is_flag=True, help='Показать сгенерированный код перед выполнением')
def generate(request: str, output_dir: str, api_key: str, scene_name: str, show_code: bool):
    """
    Генерирует видео на основе текстового запроса используя Gemini и Manim.
    
    REQUEST - описание того, какое видео нужно создать
    
    Примеры:
    
        manim-generate "Создай анимацию теоремы Пифагора"
        
        manim-generate "Покажи как работает интеграл функции x^2"
        
        manim-generate "Анимация сортировки пузырьком"
    """
    
    logger.info("🎬 Запуск Manim Video Generator")
    logger.info(f"📝 Запрос: {request}")
    
    try:
        # Инициализация клиента Gemini
        logger.info("🤖 Инициализация Gemini...")
        gemini = GeminiClient(api_key=api_key)
        
        # Генерация кода
        logger.info("⚡ Генерация кода Manim...")
        code = gemini.generate_manim_code(request)
        
        if show_code:
            click.echo("📄 Сгенерированный код:")
            click.echo("=" * 50)
            click.echo(code)
            click.echo("=" * 50)
            
            if not click.confirm("Продолжить выполнение?"):
                logger.info("Отменено пользователем")
                return
        
        # Выполнение кода
        logger.info("🎥 Рендеринг видео...")
        executor = VideoExecutor(output_dir=output_dir)
        video_path = executor.execute_manim_code(code, scene_name=scene_name)
        
        # Успех!
        logger.info(f"✅ Видео успешно создано: {video_path}")
        click.echo(f"\n🎉 Готово! Видео сохранено в: {video_path}")
        
        # Проверяем размер файла
        size_mb = video_path.stat().st_size / (1024 * 1024)
        click.echo(f"📊 Размер файла: {size_mb:.1f} MB")
        
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        click.echo(f"❌ Ошибка конфигурации: {e}", err=True)
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Manim Video Generator - создание видео с помощью ИИ"""
    pass


cli.add_command(generate)


if __name__ == '__main__':
    cli() 