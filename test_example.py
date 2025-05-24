"""
Простой тест для проверки работы модулей
Запустите: python test_example.py
"""

import os
from pathlib import Path

# Добавляем текущую директорию в путь
import sys
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тестируем, что все модули импортируются корректно"""
    print("🧪 Тестирование импортов...")
    
    try:
        from manim_video_generator.gemini_client import GeminiClient
        print("✅ GeminiClient импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта GeminiClient: {e}")
        return False
    
    try:
        from manim_video_generator.video_executor import VideoExecutor
        print("✅ VideoExecutor импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта VideoExecutor: {e}")
        return False
    
    try:
        from manim_video_generator.cli import generate
        print("✅ CLI импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта CLI: {e}")
        return False
    
    return True

def test_video_executor():
    """Тестируем VideoExecutor без реального выполнения"""
    print("\n🧪 Тестирование VideoExecutor...")
    
    try:
        from manim_video_generator.video_executor import VideoExecutor
        
        # Создаем экземпляр
        executor = VideoExecutor(output_dir="test_output")
        print("✅ VideoExecutor создан успешно")
        
        # Проверяем, что папка создалась
        if Path("test_output").exists():
            print("✅ Папка вывода создана")
        else:
            print("❌ Папка вывода не создана")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в VideoExecutor: {e}")
        return False
    
    return True

def test_gemini_client_init():
    """Тестируем инициализацию GeminiClient (без API ключа)"""
    print("\n🧪 Тестирование GeminiClient (без API)...")
    
    try:
        from manim_video_generator.gemini_client import GeminiClient
        
        # Тестируем ошибку без API ключа
        try:
            client = GeminiClient()
            print("❌ GeminiClient не должен инициализироваться без API ключа")
            return False
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("✅ Корректная проверка API ключа")
            else:
                print(f"❌ Неожиданная ошибка: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка в GeminiClient: {e}")
        return False
    
    return True

def main():
    print("🚀 Запуск тестов Manim Video Generator\n")
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_video_executor()
    all_passed &= test_gemini_client_init()
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 Все тесты прошли успешно!")
        print("\nДля полного тестирования:")
        print("1. Установите API ключ Gemini в .env файл")
        print("2. Запустите: manim-generate 'простая анимация'")
    else:
        print("❌ Некоторые тесты не прошли")
        sys.exit(1)

if __name__ == "__main__":
    main() 