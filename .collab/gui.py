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
   WRITETEST=6
   EXIT=7

def open_window():
    layout = [[sg.Text("Write excel formula", key="new"),
               sg.Multiline(size=(10, 5), key='textbox')]]
    window = sg.Window("Second Window", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()


def write_test():
   layout = [[sg.Multiline(size=(30, 5), key='textbox')]]
   return sg.Window('Get filename example', layout, size=(1000, 300))


layout = [[sg.Button(ButtonTypes.PUSH.name), sg.Button(ButtonTypes.COMMIT.name), sg.Button(ButtonTypes.DIFF.name), 
           sg.Button(ButtonTypes.PULL.name), sg.Button(ButtonTypes.INIT.name), 
           sg.Button(ButtonTypes.WRITETEST.name), sg.Button(ButtonTypes.EXIT.name)]] 

window = sg.Window('Get filename example', layout, size=(1000, 100))

map_button_to_function = {ButtonTypes.PUSH.name: push,
   ButtonTypes.PULL.name: pull, ButtonTypes.DIFF.name: diff,ButtonTypes.COMMIT.name: commit, ButtonTypes.INIT.name: init,ButtonTypes.PUSH.name: push, 
   ButtonTypes.WRITETEST.name: open_window, ButtonTypes.EXIT.name: exitProgram}

while True:
   event, values = window.read()

   if event == ButtonTypes.EXIT.name or event == sg.WIN_CLOSED:
      exitProgram()
   
   if event in map_button_to_function:
      function_to_call = map_button_to_function[event]
      if event == ButtonTypes.WRITETEST.name:
         function_to_call()
      else:
         p = Process(target=function_to_call)
         p.start()
         p.join()
