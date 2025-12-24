"""Script parser for demo video generation."""

from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path
import yaml
import json


@dataclass
class Action:
    """A single action in a scene."""
    type: str  # scroll, click, wait, goto, fill, etc.
    params: dict = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Action":
        action_type = data.pop("type")
        return cls(type=action_type, params=data)


@dataclass
class Scene:
    """A single scene in the video."""
    id: str
    narration: str = ""
    url: Optional[str] = None
    actions: list[Action] = field(default_factory=list)
    duration: Optional[float] = None  # Override duration (otherwise auto from narration)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Scene":
        actions = [Action.from_dict(a) for a in data.pop("actions", [])]
        return cls(actions=actions, **data)


@dataclass
class Project:
    """Project configuration."""
    name: str = "Demo Video"
    resolution: tuple[int, int] = (1440, 900)
    fps: int = 30
    voice: str = "zh-CN-XiaoxiaoNeural"
    voice_rate: str = "+0%"
    bitrate: str = "8000k"
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        if "resolution" in data and isinstance(data["resolution"], list):
            data["resolution"] = tuple(data["resolution"])
        return cls(**data)


@dataclass
class Script:
    """Complete video script."""
    project: Project
    scenes: list[Scene]
    
    @classmethod
    def from_dict(cls, data: dict) -> "Script":
        project = Project.from_dict(data.get("project", {}))
        scenes = [Scene.from_dict(s) for s in data.get("scenes", [])]
        return cls(project=project, scenes=scenes)


class ScriptParser:
    """Parse script files in YAML or JSON format."""
    
    @staticmethod
    def parse(file_path: str | Path) -> Script:
        """Parse a script file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Script file not found: {path}")
        
        content = path.read_text(encoding="utf-8")
        
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(content)
        elif path.suffix == ".json":
            data = json.loads(content)
        else:
            # Try YAML first, then JSON
            try:
                data = yaml.safe_load(content)
            except:
                data = json.loads(content)
        
        return Script.from_dict(data)
    
    @staticmethod
    def parse_string(content: str, format: str = "yaml") -> Script:
        """Parse a script from string."""
        if format == "yaml":
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)
        return Script.from_dict(data)
    
    @staticmethod
    def to_yaml(script: Script) -> str:
        """Convert script to YAML string."""
        data = {
            "project": {
                "name": script.project.name,
                "resolution": list(script.project.resolution),
                "fps": script.project.fps,
                "voice": script.project.voice,
                "voice_rate": script.project.voice_rate,
                "bitrate": script.project.bitrate,
            },
            "scenes": [
                {
                    "id": s.id,
                    "narration": s.narration,
                    "url": s.url,
                    "actions": [{"type": a.type, **a.params} for a in s.actions],
                    "duration": s.duration,
                }
                for s in script.scenes
            ],
        }
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
