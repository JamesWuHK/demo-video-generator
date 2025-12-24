"""Video and audio merger."""

from pathlib import Path
from typing import Optional
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip


class VideoMerger:
    """Merge video and audio tracks with precise synchronization."""
    
    def __init__(
        self,
        fps: int = 30,
        bitrate: str = "8000k",
        preset: str = "slow",
    ):
        self.fps = fps
        self.bitrate = bitrate
        self.preset = preset
    
    def merge(
        self,
        video_path: str | Path,
        audio_dir: str | Path,
        timestamps: dict[str, dict],
        output_path: str | Path,
        trim_start: float = 0,
    ) -> Path:
        """Merge video with audio tracks based on timestamps.
        
        Args:
            video_path: Path to the source video file
            audio_dir: Directory containing audio files (named {scene_id}.mp3)
            timestamps: Dict mapping scene_id to {start, audio_duration}
            output_path: Path for the output video
            trim_start: Seconds to trim from the start of the video
            
        Returns:
            Path to the output video file
        """
        video_path = Path(video_path)
        audio_dir = Path(audio_dir)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load video
        video = VideoFileClip(str(video_path))
        
        # Trim start if needed
        if trim_start > 0:
            video = video.subclipped(trim_start, video.duration)
        
        # Build audio tracks
        audio_clips = []
        for scene_id, ts in timestamps.items():
            audio_path = audio_dir / f"{scene_id}.mp3"
            if audio_path.exists():
                start_time = ts["start"]
                audio = AudioFileClip(str(audio_path))
                audio = audio.with_start(start_time)
                audio_clips.append(audio)
        
        # Composite audio
        if audio_clips:
            final_audio = CompositeAudioClip(audio_clips)
            final_video = video.with_audio(final_audio)
        else:
            final_video = video
        
        # Write output
        final_video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=self.fps,
            preset=self.preset,
            bitrate=self.bitrate,
        )
        
        # Cleanup
        video.close()
        for clip in audio_clips:
            clip.close()
        
        return output_path
    
    @staticmethod
    def generate_srt(
        timestamps: dict[str, dict],
        narrations: dict[str, str],
        output_path: str | Path,
    ) -> Path:
        """Generate SRT subtitle file.
        
        Args:
            timestamps: Dict mapping scene_id to {start, audio_duration}
            narrations: Dict mapping scene_id to narration text
            output_path: Path for the output SRT file
            
        Returns:
            Path to the SRT file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def format_time(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
        with open(output_path, "w", encoding="utf-8") as f:
            for i, (scene_id, ts) in enumerate(timestamps.items(), 1):
                if scene_id in narrations:
                    start = ts["start"]
                    duration = ts["audio_duration"]
                    end = start + duration
                    
                    f.write(f"{i}\n")
                    f.write(f"{format_time(start)} --> {format_time(end)}\n")
                    f.write(f"{narrations[scene_id]}\n\n")
        
        return output_path
