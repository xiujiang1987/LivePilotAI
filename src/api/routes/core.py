from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/v1", tags=["Core Control"])

class SystemStatusResponse(BaseModel):
    is_running: bool
    ai_active: bool
    obs_connected: bool
    current_scene: Optional[str] = None

class EmotionResponse(BaseModel):
    dominant_emotion: str
    confidence: float
    raw_scores: Optional[Dict[str, float]] = None
    engine_fps: Optional[float] = None

class SystemCommand(BaseModel):
    command: str

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(request: Request):
    """Get the current running status of LivePilotAI components."""
    app_instance = getattr(request.app.state, "main_app", None)
    
    if not app_instance:
        return SystemStatusResponse(
            is_running=False, ai_active=False, obs_connected=False
        )
        
    is_running = getattr(app_instance, "is_running", False)
    
    # Check OBS 
    obs_connected = False
    current_scene = None
    if getattr(app_instance, "obs_manager", None) and getattr(app_instance.obs_manager, "ws", None):
        obs_connected = True

    # Check AI Camera
    ai_active = False
    if getattr(app_instance, "camera_manager", None) and getattr(app_instance.camera_manager, "is_running", False):
        ai_active = True
        
    return SystemStatusResponse(
        is_running=is_running,
        ai_active=ai_active,
        obs_connected=obs_connected,
        current_scene=current_scene
    )

@router.get("/emotion", response_model=EmotionResponse)
async def get_current_emotion(request: Request):
    """Get the latest detected emotion with raw scores and FPS."""
    app_instance = getattr(request.app.state, "main_app", None)
    
    # Check if app is initialized
    if not app_instance:
        raise HTTPException(status_code=503, detail="Application not ready")
        
    # Check if AI Director exists
    if not hasattr(app_instance, "ai_director") or not app_instance.ai_director:
        # Graceful fallback if engine is off
        return EmotionResponse(dominant_emotion="neutral", confidence=0.0)
        
    director = app_instance.ai_director
    rt_detector = getattr(director, "real_time_detector", None)
    
    current_emotion = "neutral"
    confidence = 0.0
    raw_scores = {}
    fps = 0.0
    
    # Try to fetch from real_time_detector which stores rich data
    if rt_detector:
        latest_results = rt_detector.get_latest_results()
        if latest_results:
            # Assumes 1st face is primary
            primary_face = latest_results[0]
            current_emotion = getattr(primary_face, "emotion", "neutral")
            confidence = getattr(primary_face, "confidence", 0.0)
            raw_scores = getattr(primary_face, "emotions_distribution", {})
            
        # Get FPS
        stats = rt_detector.get_performance_stats()
        fps = stats.get("current_fps", 0.0)

    else:
        # Fallback to direct director attribute
        current_emotion = getattr(director, "current_emotion", "neutral")
        confidence = getattr(director, "current_confidence", 0.0)

    return EmotionResponse(
        dominant_emotion=current_emotion, 
        confidence=confidence,
        raw_scores=raw_scores,
        engine_fps=fps
    )

@router.post("/system")
async def handle_system_action(request: Request, cmd: SystemCommand):
    """Handle core system actions (e.g. stop AI)."""
    app_instance = getattr(request.app.state, "main_app", None)
    
    if not app_instance:
        raise HTTPException(status_code=503, detail="Application not ready")
        
    if cmd.command == "stop_ai":
        try:
            if getattr(app_instance, "camera_manager", None):
                app_instance.camera_manager.stop()
            if getattr(app_instance, "voice_commander", None):
                app_instance.voice_commander.stop()
            return {"message": "AI Engine stopped successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    raise HTTPException(status_code=400, detail="Unknown command")
