"""
Simple tests to check that modules load correctly.
Run: python test_example.py
"""

import os
from pathlib import Path

# Add the current directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules import correctly"""
    print("🧪 Testing imports...")
    
    try:
        from manim_video_generator.gemini_client import GeminiClient
        print("✅ GeminiClient imported")
    except ImportError as e:
        print(f"❌ GeminiClient import error: {e}")
        return False
    
    try:
        from manim_video_generator.video_executor import VideoExecutor
        print("✅ VideoExecutor imported")
    except ImportError as e:
        print(f"❌ VideoExecutor import error: {e}")
        return False
    
    try:
        from manim_video_generator.cli import generate
        print("✅ CLI imported")
    except ImportError as e:
        print(f"❌ CLI import error: {e}")
        return False
    
    return True

def test_video_executor():
    """Test VideoExecutor without actual execution"""
    print("\n🧪 Testing VideoExecutor...")
    
    try:
        from manim_video_generator.video_executor import VideoExecutor
        
        # Create an instance
        executor = VideoExecutor(output_dir="test_output")
        print("✅ VideoExecutor created successfully")
        
        # Check that the folder was created
        if Path("test_output").exists():
            print("✅ Output folder created")
        else:
            print("❌ Output folder not created")
            return False
            
    except Exception as e:
        print(f"❌ VideoExecutor error: {e}")
        return False
    
    return True

def test_gemini_client_init():
    """Test GeminiClient initialization (without API key)"""
    print("\n🧪 Testing GeminiClient (without API)...")
    
    try:
        from manim_video_generator.gemini_client import GeminiClient
        
        # Expect an error without API key
        try:
            client = GeminiClient()
            print("❌ GeminiClient should not initialize without API key")
            return False
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("✅ Correct API key check")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ GeminiClient error: {e}")
        return False
    
    return True

def main():
    print("🚀 Running Manim Video Generator tests\n")
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_video_executor()
    all_passed &= test_gemini_client_init()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        print("\nFor full testing:")
        print("1. Put your Gemini API key in the .env file")
        print("2. Run: manim-generate 'simple animation'")
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 