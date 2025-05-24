"""
Test VideoExecutor with simple Manim code
"""

from manim_video_generator.video_executor import VideoExecutor
from pathlib import Path

# Simple Manim test code
test_code = '''
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Create a simple text
        title = Text("Hello, Manim!", font_size=48)

        # Show the text
        self.play(Write(title))
        self.wait(1)

        # Create a square
        square = Square(color=BLUE)

        # Move the text up and show the square
        self.play(
            title.animate.to_edge(UP),
            Create(square)
        )
        self.wait(1)

        # Rotate the square
        self.play(Rotate(square, PI/2))
        self.wait(1)
'''

def main():
    print("🧪 Testing VideoExecutor with simple Manim code")
    
    try:
        # Create executor
        executor = VideoExecutor(output_dir="test_output")

        print("📝 Running test code...")
        video_path = executor.execute_manim_code(test_code)

        print(f"✅ Video created successfully: {video_path}")

        # Check that the file exists
        if video_path.exists():
            size_mb = video_path.stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.1f} MB")
        else:
            print("❌ File not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 