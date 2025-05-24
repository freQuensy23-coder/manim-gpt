"""
Тестирование VideoExecutor с простым кодом Manim
"""

from manim_video_generator.video_executor import VideoExecutor
from pathlib import Path

# Простой тестовый код Manim
test_code = '''
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Создаем простой текст
        title = Text("Hello, Manim!", font_size=48)
        
        # Показываем текст
        self.play(Write(title))
        self.wait(1)
        
        # Создаем квадрат
        square = Square(color=BLUE)
        
        # Перемещаем текст вверх и показываем квадрат
        self.play(
            title.animate.to_edge(UP),
            Create(square)
        )
        self.wait(1)
        
        # Поворачиваем квадрат
        self.play(Rotate(square, PI/2))
        self.wait(1)
'''

def main():
    print("🧪 Тестирование VideoExecutor с простым кодом Manim")
    
    try:
        # Создаем executor
        executor = VideoExecutor(output_dir="test_output")
        
        print("📝 Выполняем тестовый код...")
        video_path = executor.execute_manim_code(test_code)
        
        print(f"✅ Видео создано успешно: {video_path}")
        
        # Проверяем, что файл существует
        if video_path.exists():
            size_mb = video_path.stat().st_size / (1024 * 1024)
            print(f"📊 Размер файла: {size_mb:.1f} MB")
        else:
            print("❌ Файл не найден")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 