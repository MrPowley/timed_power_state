import time
import threading
import os

def hibernate_thread(seconds):
    time.sleep(seconds)
    hibernate()

def hibernate():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def put_to_sleep(seconds: int):
    thread = threading.Thread(target=hibernate_thread, args=(seconds,))
    thread.start()