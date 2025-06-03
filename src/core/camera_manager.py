"""Basic Camera Manager"""
class CameraManager:
    def __init__(self):
        self.active = False
    
    def start(self):
        self.active = True
    
    def stop(self):
        self.active = False
