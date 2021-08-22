import PySimpleGUI as sg
from cli import *
from enum import Enum
from multiprocessing import Process

# sg.theme('Dark Blue 3')  # please make your creations colorful
class ButtonTypes(Enum):
   PUSH=1
   PULL=2
   DIFF=3
   INIT=4
   COMMIT=5
   EXIT=6


layout = [[sg.Button(ButtonTypes.PUSH.name), sg.Button(ButtonTypes.COMMIT.name), sg.Button(ButtonTypes.DIFF.name), 
           sg.Button(ButtonTypes.PULL.name), sg.Button(ButtonTypes.INIT.name), sg.Button(ButtonTypes.EXIT.name)]] 

window = sg.Window('Get filename example', layout)

map_button_to_function = {ButtonTypes.PUSH.name: push,
   ButtonTypes.PULL.name: pull, ButtonTypes.DIFF.name: diff,ButtonTypes.COMMIT.name: commit, ButtonTypes.INIT.name: init,ButtonTypes.PUSH.name: push, ButtonTypes.EXIT.name: exitProgram}

while True:
   event, values = window.read()

   if event == ButtonTypes.EXIT.name:
      exitProgram()

   if event in map_button_to_function:
      function_to_call = map_button_to_function[event]
      p = Process(target=function_to_call)
      p.start()
      p.join()
