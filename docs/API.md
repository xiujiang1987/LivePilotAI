# LivePilotAI API Documentation

## Camera Management (`src.ai_engine.modules.camera_manager`)

### `CameraManager`
Handles camera initialization, configuration, and frame capture.

#### Helper Classes
- **`CameraConfig`**
    - `device_id` (int): Camera device ID (default 0).
    - `width` (int): Frame width.
    - `height` (int): Frame height.
    - `fps` (int): Target FPS.
    - `buffer_size` (int): Internal buffer size.

- **`PerformanceStats`**
    - `fps` (float): Current FPS.
    - `dropped_frames` (int): Number of dropped frames.

#### Methods

- **`initialize_camera() -> bool`**
  Initializes the camera device. Returns `True` on success.

- **`start_real_time_capture(callback: Callable) -> bool`**
  Starts a threaded capture loop. `callback` is called with each `frame`.

- **`stop_real_time_capture()`**
  Stops the capture thread.

- **`read_frame() -> Tuple[bool, Optional[ndarray]]`**
  Synchronously reads a single frame.

- **`release()`**
  Releases camera resources.

- **`get_available_cameras() -> list`**
  Scans and returns available camera indices.

---

## Face Detection (Coming Soon)
Documentation for `FaceDetector` module.
