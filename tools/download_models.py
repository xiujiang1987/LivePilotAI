import os
import urllib.request
from pathlib import Path

def download_models():
    project_root = Path(__file__).parent.parent
    models_dir = project_root / 'models'
    models_dir.mkdir(exist_ok=True)
    
    models = {
        'opencv_face_detector.pbtxt': 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/opencv_face_detector.pbtxt',
        # Corrected URL for the uint8.pb model (using specific commit hash or reliable mirror)
        'opencv_face_detector_uint8.pb': 'https://github.com/opencv/opencv_3rdparty/raw/19512576c112aa2c7b6328cb0e8d589a4a90a26d/opencv_face_detector_uint8.pb'
    }
    
    print(f"Checking models in {models_dir}...")
    
    for filename, url in models.items():
        file_path = models_dir / filename
        if file_path.exists():
            print(f"  ✅ {filename} already exists.")
        else:
            print(f"  ⬇️ Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, file_path)
                print(f"  ✅ Downloaded {filename}")
            except Exception as e:
                print(f"  ❌ Failed to download {filename}: {e}")

if __name__ == "__main__":
    download_models()
