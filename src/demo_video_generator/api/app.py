"""FastAPI application for demo video generator."""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import uuid
import json

app = FastAPI(
    title="Demo Video Generator API",
    description="AI-powered product demo video generator",
    version="0.1.0",
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task storage (use Redis in production)
tasks: dict[str, dict] = {}


class ProjectConfig(BaseModel):
    name: str = "Demo Video"
    resolution: list[int] = [1440, 900]
    fps: int = 30
    voice: str = "zh-CN-XiaoxiaoNeural"
    bitrate: str = "8000k"


class ActionConfig(BaseModel):
    type: str
    params: dict = {}


class SceneConfig(BaseModel):
    id: str
    narration: str = ""
    url: Optional[str] = None
    actions: list[dict] = []
    duration: Optional[float] = None


class ScriptConfig(BaseModel):
    project: ProjectConfig = ProjectConfig()
    scenes: list[SceneConfig]


class GenerateRequest(BaseModel):
    script: ScriptConfig
    options: dict = {}


class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float = 0.0
    message: str = ""
    output_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Demo Video Generator API", "version": "0.1.0"}


@app.post("/api/v1/generate", response_model=TaskStatus)
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start a video generation task."""
    task_id = str(uuid.uuid4())
    
    tasks[task_id] = {
        "status": "pending",
        "progress": 0.0,
        "message": "Task queued",
        "output_path": None,
        "error": None,
    }
    
    # Add to background tasks
    background_tasks.add_task(process_video_task, task_id, request.script.model_dump())
    
    return TaskStatus(task_id=task_id, **tasks[task_id])


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a generation task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatus(task_id=task_id, **tasks[task_id])


@app.get("/api/v1/tasks/{task_id}/download")
async def download_video(task_id: str):
    """Download the generated video."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video not ready")
    
    output_path = task["output_path"]
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=Path(output_path).name,
    )


async def process_video_task(task_id: str, script_data: dict):
    """Process video generation task."""
    from ..core.script import Script
    from ..core.tts import TTSEngine
    from ..core.recorder import VideoRecorder
    from ..core.merger import VideoMerger

    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["message"] = "Parsing script..."

        # Parse script
        script = Script.from_dict(script_data)

        # Setup paths
        output_dir = Path(f"./output/{task_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)

        # Generate audio
        tasks[task_id]["message"] = "Generating audio..."
        tasks[task_id]["progress"] = 0.1

        tts = TTSEngine(voice=script.project.voice)
        scene_durations = {}

        for i, scene in enumerate(script.scenes):
            if scene.narration:
                audio_path = audio_dir / f"{scene.id}.mp3"
                duration = tts.generate(scene.narration, audio_path)
                scene_durations[scene.id] = duration
            else:
                scene_durations[scene.id] = scene.duration or 3.0

            tasks[task_id]["progress"] = 0.1 + (0.3 * (i + 1) / len(script.scenes))

        # Record video
        tasks[task_id]["message"] = "Recording video..."
        tasks[task_id]["progress"] = 0.4

        recorder = VideoRecorder(
            output_dir=output_dir,
            resolution=tuple(script.project.resolution),
            headless=True,
        )

        result = recorder.record(
            scenes=script.scenes,
            scene_durations=scene_durations,
        )

        tasks[task_id]["progress"] = 0.7

        # Merge video and audio
        tasks[task_id]["message"] = "Merging video and audio..."

        output_path = output_dir / "output.mp4"
        merger = VideoMerger(
            fps=script.project.fps,
            bitrate=script.project.bitrate,
        )

        merger.merge(
            video_path=result.video_path,
            audio_dir=audio_dir,
            timestamps=result.timestamps,
            output_path=output_path,
            trim_start=result.login_duration,
        )

        tasks[task_id]["progress"] = 0.9

        # Generate subtitles
        tasks[task_id]["message"] = "Generating subtitles..."
        narrations = {s.id: s.narration for s in script.scenes if s.narration}
        srt_path = output_path.with_suffix(".srt")
        merger.generate_srt(result.timestamps, narrations, srt_path)

        # Done
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 1.0
        tasks[task_id]["message"] = "Video generation completed"
        tasks[task_id]["output_path"] = str(output_path)

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["message"] = f"Error: {str(e)}"


# New AI Script Generation Endpoints

class AIGenerateRequest(BaseModel):
    """Request for AI script generation."""
    url: str
    video_length: int = 60
    style: str = "professional"  # professional, casual, energetic
    language: str = "zh-CN"
    focus_areas: list[str] = []


class AIGenerateResponse(BaseModel):
    """Response from AI script generation."""
    script: dict
    analysis: dict


@app.post("/api/v1/ai/generate-script", response_model=AIGenerateResponse)
async def ai_generate_script(request: AIGenerateRequest):
    """Generate demo video script using AI.

    Analyzes the website and automatically creates a complete script.
    """
    from ..core.ai_generator import generate_demo_script

    try:
        # Generate script using AI
        script = await generate_demo_script(
            url=request.url,
            video_length=request.video_length,
            style=request.style,
            language=request.language,
            focus_areas=request.focus_areas
        )

        return AIGenerateResponse(
            script=script,
            analysis={"url": request.url}  # Could include more analysis details
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")


@app.post("/api/v1/ai/generate-video")
async def ai_generate_video(request: AIGenerateRequest, background_tasks: BackgroundTasks):
    """AI-powered one-click video generation.

    Analyzes website, generates script, and creates video in one step.
    """
    from ..core.ai_generator import generate_demo_script

    try:
        # Generate script
        script_data = await generate_demo_script(
            url=request.url,
            video_length=request.video_length,
            style=request.style,
            language=request.language,
            focus_areas=request.focus_areas
        )

        # Create video generation task
        task_id = str(uuid.uuid4())

        tasks[task_id] = {
            "status": "pending",
            "progress": 0.0,
            "message": "AI script generated, starting video creation...",
            "output_path": None,
            "error": None,
            "script": script_data,  # Include generated script in response
        }

        # Add to background tasks
        background_tasks.add_task(process_video_task, task_id, script_data)

        return TaskStatus(task_id=task_id, **tasks[task_id])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")


def create_app():
    """Create FastAPI application."""
    return app

