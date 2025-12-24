"""CLI entry point for demo video generator."""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.script import ScriptParser
from ..core.tts import TTSEngine
from ..core.recorder import VideoRecorder
from ..core.merger import VideoMerger

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Demo Video Generator - AI-powered product demo video generator."""
    pass


@cli.command()
@click.option("--script", "-s", required=True, help="Path to script file (YAML/JSON)")
@click.option("--output", "-o", default="./output/demo.mp4", help="Output video path")
@click.option("--audio-dir", default=None, help="Audio output directory")
@click.option("--resolution", default="1440x900", help="Video resolution (WxH)")
@click.option("--voice", default="zh-CN-XiaoxiaoNeural", help="TTS voice")
@click.option("--headless", is_flag=True, help="Run browser in headless mode")
def generate(script, output, audio_dir, resolution, voice, headless):
    """Generate demo video from script."""
    console.print(f"[bold blue]🎬 Demo Video Generator[/bold blue]")
    console.print(f"📄 Script: {script}")
    console.print(f"📁 Output: {output}")
    
    # Parse resolution
    width, height = map(int, resolution.split("x"))
    
    # Parse script
    console.print("\n[bold]1. Parsing script...[/bold]")
    script_data = ScriptParser.parse(script)
    console.print(f"   ✅ Loaded {len(script_data.scenes)} scenes")
    
    # Setup paths
    output_path = Path(output)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if audio_dir is None:
        audio_dir = output_dir / "audio"
    else:
        audio_dir = Path(audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate audio
    console.print("\n[bold]2. Generating audio...[/bold]")
    tts = TTSEngine(voice=voice)
    scene_durations = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating...", total=len(script_data.scenes))
        
        for scene in script_data.scenes:
            if scene.narration:
                audio_path = audio_dir / f"{scene.id}.mp3"
                if not audio_path.exists():
                    duration = tts.generate(scene.narration, audio_path)
                else:
                    duration = tts.get_duration(audio_path)
                scene_durations[scene.id] = duration
            else:
                scene_durations[scene.id] = scene.duration or 3.0
            progress.advance(task)
    
    total_audio = sum(scene_durations.values())
    console.print(f"   ✅ Total audio duration: {total_audio:.1f}s")
    
    # Record video
    console.print("\n[bold]3. Recording video...[/bold]")
    recorder = VideoRecorder(
        output_dir=output_dir,
        resolution=(width, height),
        headless=headless,
    )
    
    def on_scene_start(scene_id, index):
        console.print(f"   📍 Scene {index}/{len(script_data.scenes)}: {scene_id}")
    
    result = recorder.record(
        scenes=script_data.scenes,
        scene_durations=scene_durations,
        on_scene_start=on_scene_start,
    )
    console.print(f"   ✅ Recorded {result.total_duration:.1f}s")
    
    # Merge video and audio
    console.print("\n[bold]4. Merging video and audio...[/bold]")
    merger = VideoMerger(
        fps=script_data.project.fps,
        bitrate=script_data.project.bitrate,
    )
    
    merger.merge(
        video_path=result.video_path,
        audio_dir=audio_dir,
        timestamps=result.timestamps,
        output_path=output_path,
        trim_start=result.login_duration,
    )
    console.print(f"   ✅ Video saved: {output_path}")
    
    # Generate subtitles
    console.print("\n[bold]5. Generating subtitles...[/bold]")
    narrations = {s.id: s.narration for s in script_data.scenes if s.narration}
    srt_path = output_path.with_suffix(".srt")
    merger.generate_srt(result.timestamps, narrations, srt_path)
    console.print(f"   ✅ Subtitles saved: {srt_path}")
    
    console.print("\n[bold green]🎉 Done![/bold green]")
    console.print(f"📁 Video: {output_path}")
    console.print(f"📝 Subtitles: {srt_path}")


@cli.command()
@click.option("--script", "-s", required=True, help="Path to script file")
@click.option("--output", "-o", default="./output/audio", help="Audio output directory")
@click.option("--voice", default="zh-CN-XiaoxiaoNeural", help="TTS voice")
def audio(script, output, voice):
    """Generate audio files from script narrations."""
    console.print(f"[bold blue]🎙️ Generating Audio[/bold blue]")
    
    script_data = ScriptParser.parse(script)
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tts = TTSEngine(voice=voice)
    total_duration = 0
    
    for scene in script_data.scenes:
        if scene.narration:
            audio_path = output_dir / f"{scene.id}.mp3"
            console.print(f"   Generating: {scene.id}")
            duration = tts.generate(scene.narration, audio_path)
            total_duration += duration
            console.print(f"   ✅ {audio_path} ({duration:.1f}s)")
    
    console.print(f"\n[bold green]✅ Total: {total_duration:.1f}s[/bold green]")


@cli.command()
@click.option("--script", "-s", required=True, help="Path to script file")
@click.option("--output", "-o", default="./output/video.webm", help="Video output path")
@click.option("--resolution", default="1440x900", help="Video resolution")
@click.option("--headless", is_flag=True, help="Run in headless mode")
def record(script, output, resolution, headless):
    """Record video from script (without audio)."""
    console.print(f"[bold blue]🎬 Recording Video[/bold blue]")
    
    width, height = map(int, resolution.split("x"))
    script_data = ScriptParser.parse(script)
    output_path = Path(output)
    
    # Use default durations
    scene_durations = {s.id: s.duration or 5.0 for s in script_data.scenes}
    
    recorder = VideoRecorder(
        output_dir=output_path.parent,
        resolution=(width, height),
        headless=headless,
    )
    
    result = recorder.record(
        scenes=script_data.scenes,
        scene_durations=scene_durations,
    )
    
    console.print(f"\n[bold green]✅ Video saved: {result.video_path}[/bold green]")


@cli.command()
@click.option("--video", "-v", required=True, help="Source video file")
@click.option("--audio-dir", "-a", required=True, help="Audio directory")
@click.option("--timestamps", "-t", required=True, help="Timestamps JSON file")
@click.option("--output", "-o", required=True, help="Output video path")
@click.option("--trim-start", default=0.0, help="Seconds to trim from start")
def merge(video, audio_dir, timestamps, output, trim_start):
    """Merge video with audio tracks."""
    import json
    
    console.print(f"[bold blue]🔀 Merging Video and Audio[/bold blue]")
    
    with open(timestamps, "r") as f:
        ts_data = json.load(f)
    
    merger = VideoMerger()
    merger.merge(
        video_path=video,
        audio_dir=audio_dir,
        timestamps=ts_data,
        output_path=output,
        trim_start=trim_start,
    )
    
    console.print(f"\n[bold green]✅ Output: {output}[/bold green]")


@cli.command()
@click.option("--language", "-l", default=None, help="Filter by language (e.g., zh-CN)")
def voices(language):
    """List available TTS voices."""
    console.print(f"[bold blue]🎤 Available Voices[/bold blue]")
    
    voice_list = TTSEngine.list_voices_sync(language)
    
    for v in voice_list:
        console.print(f"  {v['ShortName']} - {v['Locale']} ({v['Gender']})")


if __name__ == "__main__":
    cli()
