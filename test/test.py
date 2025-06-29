# test_device_id.py
import subprocess

def test_device_ids():
    print("🔍 Probando diferentes device IDs...")
    
    for device_id in [0, 1]:
        cmd = f'gst-launch-1.0 videotestsrc num-buffers=10 ! nvh264enc ! nvh264dec cuda-device-id={device_id} ! fakesink'
        print(f"\n🧪 Probando device-id={device_id}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Device ID {device_id}: FUNCIONA")
        else:
            print(f"❌ Device ID {device_id}: FALLO")
            if "error" in result.stderr.lower():
                print(f"Error: {result.stderr.split('ERROR')[1].split('\\n')[0] if 'ERROR' in result.stderr else 'Desconocido'}")

if __name__ == "__main__":
    test_device_ids()