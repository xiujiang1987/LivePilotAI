try:
    import mediapipe.python.solutions as solutions
    print("Imported mediapipe.python.solutions")
except ImportError as e:
    print(f"Failed to import mediapipe.python.solutions: {e}")

import mediapipe as mp
print(f"mp location: {mp.__file__}")
