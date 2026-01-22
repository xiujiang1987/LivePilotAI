import cv2

def list_ports():
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    
    print("正在掃描攝像頭設備 (這可能需要幾秒鐘)...")
    
    # 掃描前 5 個索引
    while dev_port < 5:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print(f"Port {dev_port} is not working.")
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print(f"✅ Port {dev_port} is working and reads images ({int(w)}x{int(h)})")
                working_ports.append(dev_port)
            else:
                print(f"⚠️ Port {dev_port} is present but cannot read images ({int(w)}x{int(h)})")
                available_ports.append(dev_port)
            camera.release()
        dev_port += 1
    return working_ports, available_ports, non_working_ports

if __name__ == '__main__':
    working, available, non_working = list_ports()
    print("\n總結:")
    if working:
        print(f"可用且正常的攝像頭索引: {working}")
        print(f"建議在程式中使用 device_id = {working[0]}")
    else:
        print("❌ 沒有找到可用的攝像頭。請檢查連線。")
