"""Core modules for demo video generation."""

from .recorder import VideoRecorder
from .tts import TTSEngine
from .merger import VideoMerger
from .script import ScriptParser, Scene, Project

__all__ = [
    "VideoRecorder",
    "TTSEngine", 
    "VideoMerger",
    "ScriptParser",
    "Scene",
    "Project",
]
