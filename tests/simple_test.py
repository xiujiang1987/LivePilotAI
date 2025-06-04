import sys
print("Python version:", sys.version)

# 測試依賴檢查
packages_to_check = ['cv2', 'numpy', 'tensorflow', 'PIL']
installed = []
missing = []

for pkg in packages_to_check:
    try:
        __import__(pkg)
        installed.append(pkg)
        print(f"✓ {pkg} 已安裝")
    except ImportError:
        missing.append(pkg)
        print(f"✗ {pkg} 未安裝")

print(f"\n已安裝: {installed}")
print(f"缺失: {missing}")

if missing:
    print(f"\n需要安裝的包: {' '.join(missing)}")
else:
    print("\n所有依賴已就緒！")
