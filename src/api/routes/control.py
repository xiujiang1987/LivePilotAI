from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["Control Actions"])

class LayoutRequest(BaseModel):
    scene_name: str

class SystemCommand(BaseModel):
    command: str

@router.post("/layout")
async def change_layout(request: Request, body: LayoutRequest):
    """Manually change the OBS scene layout."""
    app_instance = getattr(request.app.state, "main_app", None)
    if not app_instance or not app_instance.scene_controller:
        raise HTTPException(status_code=503, detail="Scene controller not ready")
        
    try:
        success = app_instance.scene_controller.change_to_scene(body.scene_name)
        if success:
            return {"status": "success", "message": f"Switched to {body.scene_name}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to switch scene")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system")
async def system_action(request: Request, body: SystemCommand):
    """Control the LivePilotAI system state (start, stop)."""
    app_instance = getattr(request.app.state, "main_app", None)
    if not app_instance:
        raise HTTPException(status_code=503, detail="Main app not ready")
        
    cmd = body.command.lower()
    
    # Send commands up to the app instance or panels
    if cmd == "stop_ai":
        if app_instance.camera_manager:
            app_instance.camera_manager.stop()
        return {"status": "success", "message": "AI Engine stopped"}
    elif cmd == "start_ai":
        # In actual implementation, requires main_panel to trigger start sequence
        raise HTTPException(status_code=501, detail="Start AI via API not fully implemented")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown command {cmd}")
