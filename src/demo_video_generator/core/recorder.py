"""Browser-based video recorder using Playwright."""

import time
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page, BrowserContext

from .script import Scene, Action, Project


@dataclass
class RecordingResult:
    """Result of a video recording session."""
    video_path: Path
    timestamps: dict[str, dict]  # scene_id -> {start, duration}
    total_duration: float
    login_duration: float = 0  # Duration to trim from start


class VideoRecorder:
    """Browser-based video recorder."""
    
    def __init__(
        self,
        output_dir: str | Path = "./output",
        resolution: tuple[int, int] = (1440, 900),
        headless: bool = False,
        slow_mo: int = 100,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.resolution = resolution
        self.headless = headless
        self.slow_mo = slow_mo
    
    def record(
        self,
        scenes: list[Scene],
        scene_durations: dict[str, float],
        login_url: Optional[str] = None,
        login_action: Optional[Callable[[Page], None]] = None,
        on_scene_start: Optional[Callable[[str, int], None]] = None,
    ) -> RecordingResult:
        """Record video from scenes.
        
        Args:
            scenes: List of scenes to record
            scene_durations: Duration for each scene (usually from TTS audio)
            login_url: Optional URL to login before recording
            login_action: Optional callback to perform login
            on_scene_start: Optional callback when each scene starts
            
        Returns:
            RecordingResult with video path and timestamps
        """
        timestamps = {}
        login_duration = 0
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
            
            context = browser.new_context(
                viewport={"width": self.resolution[0], "height": self.resolution[1]},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": self.resolution[0], "height": self.resolution[1]},
                locale="zh-CN",
            )
            
            page = context.new_page()
            video_start_time = time.time()
            
            # Perform login if needed
            if login_url and login_action:
                page.goto(login_url, wait_until="networkidle")
                login_action(page)
                login_duration = time.time() - video_start_time
            
            recording_start = time.time()
            
            # Record each scene
            for i, scene in enumerate(scenes):
                scene_id = scene.id
                duration = scene_durations.get(scene_id, 5.0)
                
                scene_start = time.time() - recording_start
                timestamps[scene_id] = {
                    "start": scene_start,
                    "audio_duration": duration,
                }
                
                if on_scene_start:
                    on_scene_start(scene_id, i + 1)
                
                # Navigate to URL if specified
                if scene.url:
                    current_url = page.url.split("#")[0]
                    target_url = scene.url.split("#")[0]
                    if current_url != target_url:
                        page.goto(scene.url, wait_until="networkidle")
                    elif "#" in scene.url:
                        page.goto(scene.url)
                
                # Execute actions
                action_time = 0
                for action in scene.actions:
                    action_time += self._execute_action(page, action)
                
                # Wait remaining time
                remaining = duration - action_time
                if remaining > 0:
                    time.sleep(remaining)
            
            total_duration = time.time() - recording_start
            
            context.close()
            browser.close()
        
        # Find the recorded video file
        video_files = list(self.output_dir.glob("*.webm"))
        if video_files:
            video_path = max(video_files, key=lambda x: x.stat().st_mtime)
        else:
            raise RuntimeError("No video file was recorded")
        
        return RecordingResult(
            video_path=video_path,
            timestamps=timestamps,
            total_duration=total_duration,
            login_duration=login_duration,
        )
    
    def _execute_action(self, page: Page, action: Action) -> float:
        """Execute a single action and return time spent."""
        start = time.time()
        
        if action.type == "scroll":
            y = action.params.get("y", 0)
            smooth = action.params.get("smooth", False)
            behavior = "smooth" if smooth else "instant"
            page.evaluate(f"window.scrollTo({{top: {y}, behavior: '{behavior}'}})")
            time.sleep(0.5)
            
        elif action.type == "scroll_to_text":
            text = action.params.get("text", "")
            offset = action.params.get("offset", 0)
            try:
                element = page.locator(f"text={text}").first
                element.scroll_into_view_if_needed()
                time.sleep(0.3)
                page.evaluate(f"window.scrollBy(0, -{offset})")
            except:
                pass
            time.sleep(0.5)
            
        elif action.type == "click":
            selector = action.params.get("selector", "")
            text = action.params.get("text", "")
            timeout = action.params.get("timeout", 3000)
            try:
                if text:
                    page.click(f"text={text}", timeout=timeout)
                elif selector:
                    page.click(selector, timeout=timeout)
            except:
                pass
            time.sleep(0.5)
            
        elif action.type == "fill":
            selector = action.params.get("selector", "")
            value = action.params.get("value", "")
            page.fill(selector, value)
            time.sleep(0.3)
            
        elif action.type == "wait":
            duration = action.params.get("duration", 1)
            if duration != "auto":
                time.sleep(duration)
                
        elif action.type == "goto":
            url = action.params.get("url", "")
            page.goto(url, wait_until="networkidle")
            time.sleep(0.5)
            
        elif action.type == "scroll_iframe":
            positions = action.params.get("positions", [300, 600, 900])
            interval = action.params.get("interval", 1.5)
            for pos in positions:
                page.evaluate(f"""
                    const iframe = document.querySelector('iframe');
                    if (iframe && iframe.contentWindow) {{
                        iframe.contentWindow.scrollTo({{top: {pos}, behavior: 'smooth'}});
                    }}
                """)
                time.sleep(interval)
        
        return time.time() - start
