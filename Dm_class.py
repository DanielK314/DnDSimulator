from datetime import datetime
import numpy as np
import os
import sys


class DungeonMaster:
    def __init__(self):
        self.AI_blank = False #just ignore, but MUST be False, see AI Class
        self.printing_on = False
        self.start_time = datetime.now()

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        self.Battlefield = np.genfromtxt(application_path + '/Battlefield.txt', delimiter= ',')      #load Informations from Battlefield
        self.density = self.Battlefield[0][1]
        #density: 0 - loose, 1 - normal, 2 - dense
        self.rounds_number = 1

        self.text = ''

    def reset(self):
        #This function is called a the start of the fighting and resets the DM
        self.rounds_number = 1
    
    def block_print(self):
        self.printing_on = False

    def enable_print(self):
        self.printing_on = True

    def say(self, text_to_say, this_is_new_line=False):
        if self.printing_on:
            if False:                       #This is a hard coded, disabled developer Function 
                if False:#total diff in ms
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                if True:#diff to last 
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                    self.start_time = datetime.now()
            if this_is_new_line:
                print(self.text)
                self.text = '' #start new line
            self.text = ''.join([self.text, text_to_say])