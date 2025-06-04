import os
import sys

# 簡單的 Hello World 測試
print("Hello from LivePilotAI Test!")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# 寫入測試文件
with open("simple_test_output.txt", "w") as f:
    f.write("LivePilotAI Simple Test Output\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Current directory: {os.getcwd()}\n")
    f.write("Test completed successfully!\n")

print("Test file created: simple_test_output.txt")
