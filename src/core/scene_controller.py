"""
Basic Scene Controller implementation
"""

class SceneController:
    def __init__(self):
        self.current_scene = "Default"
    
    def switch_scene(self, scene_name):
        self.current_scene = scene_name
        return True
    
    def get_current_scene(self):
        return self.current_scene
