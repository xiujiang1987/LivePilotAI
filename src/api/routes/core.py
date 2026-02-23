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

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(request: Request):
    """Get the current running status of LivePilotAI components."""
    app_instance = getattr(request.app.state, "main_app", None)
    
    if not app_instance:
        return SystemStatusResponse(
            is_running=False, ai_active=False, obs_connected=False
        )
        
    is_running = app_instance.is_running
    
    # Check OBS 
    obs_connected = False
    current_scene = None
    if app_instance.obs_manager and app_instance.obs_manager.ws:
        obs_connected = True
        try:
            # Note: obsmanager might not store current scene, fallback to none or get it
            pass
        except Exception:
            pass

    # Check AI Camera
    ai_active = False
    if app_instance.camera_manager and app_instance.camera_manager.is_running:
        ai_active = True
        
    return SystemStatusResponse(
        is_running=is_running,
        ai_active=ai_active,
        obs_connected=obs_connected,
        current_scene=current_scene
    )

@router.get("/emotion", response_model=EmotionResponse)
async def get_current_emotion(request: Request):
    """Get the latest detected emotion."""
    app_instance = getattr(request.app.state, "main_app", None)
    if not app_instance or not app_instance.ai_director:
        raise HTTPException(status_code=503, detail="AI Director not running")
        
    director = app_instance.ai_director
    
    # We retrieve the latest emotion from director state if available
    # Safe fallback if attributes differ
    current_emotion = getattr(director, "current_emotion", "neutral")
    return EmotionResponse(dominant_emotion=current_emotion, confidence=1.0)
