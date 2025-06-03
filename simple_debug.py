import os
import sys

print("Simple test starting...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Check if main files exist
files_to_check = ["main_day5.py", "launcher_fixed.py", "basic_test.py"]
for file in files_to_check:
    if os.path.exists(file):
        print(f"Found: {file}")
    else:
        print(f"Missing: {file}")

print("Simple test completed.")
