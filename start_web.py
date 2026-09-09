#!/usr/bin/env python3
"""
=============================================================================
    Start Web Demo
    ==============
    สคริปต์สำหรับเปิด web demo อย่างง่าย

    วิธีใช้:
        python start_web.py

    จากนั้นเปิด browser ไปที่:
        http://localhost:5000
=============================================================================
"""

import webbrowser
import time
import threading

def open_browser():
    """เปิด browser หลังจาก server พร้อม"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("=" * 50)
    print("  Starting Optimization Algorithms Web Demo...")
    print("  Browser will open automatically")
    print("=" * 50)
    print()

    # เปิด browser อัตโนมัติ
    threading.Thread(target=open_browser, daemon=True).start()

    # รัน Flask app
    from app import app
    app.run(debug=False, port=5000)
