# helpper program to easily view current cursor postion
# quickes to run from command prompt
import os
from time import sleep
import pyautogui
try:
    while True:
        sleep(.3)
        os.system('cls')
        x,y = pyautogui.position()
        print(f'{x},{y}')
except KeyboardInterrupt:
    quit() 