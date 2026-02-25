import sys
print("Python is working")
print("Version:", sys.version)
try:
    import tkinter
    print("GUI: Available")
except:
    print("GUI: Not available")

try:
    from pathlib import Path
    print("Current dir:", Path.cwd())
    print("Files:", list(Path(".").glob("*.py"))[:5])
except Exception as e:
    print("Error:", e)
