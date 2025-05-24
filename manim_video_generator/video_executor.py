import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from loguru import logger


class VideoExecutor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"VideoExecutor initialized, output directory: {self.output_dir}")

    def execute_manim_code(self, code: str, scene_name: str = "VideoScene") -> Path:
        """Execute Manim code in an isolated environment and return the video path"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a temporary file with the code
            code_file = temp_path / "scene.py"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            logger.info(f"Code written to temporary file: {code_file}")
            
            # Run Manim
            output_file = self._run_manim(code_file, scene_name, temp_path)
            
            # Copy the result to the output folder
            final_output = self._copy_to_output(output_file)
            
            return final_output

    def _run_manim(self, code_file: Path, scene_name: str, temp_dir: Path) -> Path:
        """Run Manim to render the video"""
        
        cmd = [
            "manim", "render",
            str(code_file),
            scene_name,
            "--format", "mp4",
            "-q", "m",  # medium quality: 'l'=low, 'm'=medium, 'h'=high, 'p'=4k, 'k'=8k
            "--output_file", "video.mp4"
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute the command in the temporary directory
        result = subprocess.run(
            cmd,
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode != 0:
            logger.error(f"Manim execution error: {result.stderr}")
            raise RuntimeError(f"Manim exited with error: {result.stderr}")
        
        logger.info("Manim executed successfully")
        
        # Look for the created video
        media_dir = temp_dir / "media"
        if not media_dir.exists():
            raise FileNotFoundError("Media folder not found after running Manim")
        
        # Search for mp4 file recursively
        video_files = list(media_dir.rglob("*.mp4"))
        if not video_files:
            raise FileNotFoundError("Video file not found after rendering")
        
        # Take the most recent file
        video_file = max(video_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Video file found: {video_file}")
        
        return video_file

    def _copy_to_output(self, video_file: Path) -> Path:
        """Copy video to the output folder with a unique name"""
        
        import time
        timestamp = int(time.time())
        output_file = self.output_dir / f"video_{timestamp}.mp4"
        
        shutil.copy2(video_file, output_file)
        logger.info(f"Video copied to: {output_file}")
        
        return output_file 