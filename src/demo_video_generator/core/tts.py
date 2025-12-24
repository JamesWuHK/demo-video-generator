"""Text-to-Speech engine using Edge TTS."""

import asyncio
from pathlib import Path
from typing import Optional
import edge_tts
from mutagen.mp3 import MP3


class TTSEngine:
    """Text-to-Speech engine for generating narration audio."""
    
    def __init__(
        self,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        volume: str = "+0%",
    ):
        self.voice = voice
        self.rate = rate
        self.volume = volume
    
    async def generate_async(self, text: str, output_path: str | Path) -> float:
        """Generate audio file from text asynchronously.
        
        Returns the duration of the generated audio in seconds.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            volume=self.volume,
        )
        await communicate.save(str(output_path))
        
        return self.get_duration(output_path)
    
    def generate(self, text: str, output_path: str | Path) -> float:
        """Generate audio file from text synchronously.
        
        Returns the duration of the generated audio in seconds.
        """
        return asyncio.run(self.generate_async(text, output_path))
    
    @staticmethod
    def get_duration(audio_path: str | Path) -> float:
        """Get the duration of an audio file in seconds."""
        audio = MP3(str(audio_path))
        return audio.info.length
    
    @staticmethod
    async def list_voices(language: Optional[str] = None) -> list[dict]:
        """List available voices, optionally filtered by language."""
        voices = await edge_tts.list_voices()
        
        if language:
            voices = [v for v in voices if v["Locale"].startswith(language)]
        
        return voices
    
    @classmethod
    def list_voices_sync(cls, language: Optional[str] = None) -> list[dict]:
        """List available voices synchronously."""
        return asyncio.run(cls.list_voices(language))


# Common voice presets
VOICE_PRESETS = {
    "zh-CN-female": "zh-CN-XiaoxiaoNeural",
    "zh-CN-male": "zh-CN-YunxiNeural",
    "zh-TW-female": "zh-TW-HsiaoChenNeural",
    "zh-TW-male": "zh-TW-YunJheNeural",
    "en-US-female": "en-US-JennyNeural",
    "en-US-male": "en-US-GuyNeural",
    "ja-JP-female": "ja-JP-NanamiNeural",
    "ja-JP-male": "ja-JP-KeitaNeural",
}
