import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from loguru import logger
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips


class VideoExecutor:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.music_file = Path("data/music.mp3")
        logger.info(f"VideoExecutor initialized, output directory: {self.output_dir}")
        
        if not self.music_file.exists():
            logger.warning(f"Background music file not found: {self.music_file}")

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
            
            # Add background music
            output_file = self._add_background_music(output_file, temp_path)
            
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

    def _add_background_music(self, video_file: Path, temp_dir: Path) -> Path:
        """Add background music to the video"""
        logger.info("Adding background music to video")
        
        video_with_music = temp_dir / "video_with_music.mp4"
        
        # Load video and music
        video = VideoFileClip(str(video_file))
        music = AudioFileClip(str(self.music_file))
        
        # Adjust music duration to match video
        video_duration = video.duration
        if music.duration > video_duration:
            # Trim music if longer than video
            music = music.subclip(0, video_duration)
        else:
            # Loop music if shorter than video
            loops_needed = int(video_duration // music.duration) + 1
            music = concatenate_audioclips([music] * loops_needed).subclip(0, video_duration)
        
        # Set music volume lower to not overpower original audio (if any)
        music = music.volumex(0.3)  # 30% volume
        
        # Combine original audio with music
        if video.audio is not None:
            final_audio = CompositeAudioClip([video.audio, music])
        else:
            final_audio = music
        
        # Create final video with music
        final_video = video.set_audio(final_audio)
        final_video.write_videofile(str(video_with_music), codec='libx264', audio_codec='aac')
        
        # Clean up
        video.close()
        music.close()
        final_video.close()
        
        logger.info(f"Background music added: {video_with_music}")
        return video_with_music

    def _copy_to_output(self, video_file: Path) -> Path:
        """Copy video to the output folder with a unique name"""
        
        import time
        timestamp = int(time.time())
        output_file = self.output_dir / f"video_{timestamp}.mp4"
        
        shutil.copy2(video_file, output_file)
        logger.info(f"Video copied to: {output_file}")
        
        return output_file  