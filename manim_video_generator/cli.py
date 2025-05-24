import click
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from .gemini_client import GeminiClient
from .video_executor import VideoExecutor

load_dotenv('.env')  # Load .env from the current directory

# Logging setup
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


@click.command()
@click.argument('request', required=True)
@click.option('--output-dir', '-o', default='output', help='Directory to save the video')
@click.option('--api-key', help='Gemini API key (or use the GEMINI_API_KEY environment variable)')
@click.option('--scene-name', default='VideoScene', help='Scene class name in the generated code')
@click.option('--show-code', is_flag=True, help='Show generated code before execution')
def generate(request: str, output_dir: str, api_key: str, scene_name: str, show_code: bool):
    """
    Generate a video from a text prompt using Gemini and Manim.

    REQUEST is a description of the video to create.

    Examples:

        manim-generate "Create an animation of the Pythagorean theorem"

        manim-generate "Show how the integral of x^2 works"

        manim-generate "Bubble sort animation"
    """
    
    logger.info("🎬 Starting Manim Video Generator")
    logger.info(f"📝 Request: {request}")
    
    try:
        # Initialize Gemini client
        logger.info("🤖 Initializing Gemini...")
        gemini = GeminiClient(api_key=api_key)
        
        # Generate code
        logger.info("⚡ Generating Manim code...")
        code = gemini.generate_manim_code(request)
        
        if show_code:
            click.echo("📄 Generated code:")
            click.echo("=" * 50)
            click.echo(code)
            click.echo("=" * 50)
            
            if not click.confirm("Proceed with execution?"):
                logger.info("Cancelled by user")
                return
        
        # Execute code with optional error fixing
        executor = VideoExecutor(output_dir=output_dir)

        while True:
            logger.info("🎥 Rendering video...")
            try:
                video_path = executor.execute_manim_code(code, scene_name=scene_name)
                break
            except Exception as exec_err:
                import traceback
                trace = traceback.format_exc()
                click.echo("\n❌ Rendering error:\n" + trace, err=True)

                choice = click.prompt(
                    "What to do? [s]top / [r]etry LLM / [h]int",
                    type=click.Choice(["s", "r", "h"], case_sensitive=False),
                    default="s"
                )

                if choice.lower() == "s":
                    sys.exit(1)

                hint = None
                if choice.lower() == "h":
                    hint = click.prompt("Enter a hint for the LLM")

                logger.info("🔧 Requesting code fix from Gemini")
                code = gemini.fix_manim_code(code, trace, hint)

                if show_code:
                    click.echo("\n📄 Corrected code:")
                    click.echo("=" * 50)
                    click.echo(code)
                    click.echo("=" * 50)

                        if not click.confirm("Continue execution with the new code?"):
                            logger.info("Cancelled by user")
                            sys.exit(1)

        
        # Success!
        logger.info(f"✅ Video successfully created: {video_path}")
        click.echo(f"\n🎉 Done! Video saved to: {video_path}")
        
        # Show file size
        size_mb = video_path.stat().st_size / (1024 * 1024)
        click.echo(f"📊 File size: {size_mb:.1f} MB")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Manim Video Generator - create videos using AI"""
    pass


cli.add_command(generate)


if __name__ == '__main__':
    cli() 