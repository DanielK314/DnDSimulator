from datetime import datetime
import numpy as np


class DungeonMaster:
    def __init__(self):
        self.AI_blank = False #just ignore, but MUST be False, see AI Class
        self.printing_on = False
        self.start_time = datetime.now()
        self.Battlefield = np.genfromtxt('Battlefield.txt', delimiter= ',')      #load Informations from Battlefield
        self.density = self.Battlefield[0][1]
        #density: 0 - loose, 1 - normal, 2 - dense
        self.rounds_number = 1
        self.relations = [] #is a list with inter player relations, see class relation

    def reset(self):
        #This function is called a the start of the fighting and resets the DM
        self.rounds_number = 1
        self.relations = []
    
    def reset_relations(self):
        self.relations = []

    def block_print(self):
        self.printing_on = False

    def enable_print(self):
        self.printing_on = True

    def say(self, text, end=False):
        if self.printing_on:
            if False:                       #This is a hard coded, disabled developer Function 
                if False:#total diff in ms
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                if True:#diff to last 
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                    self.start_time = datetime.now()
            if end == False:
                print(text)
            else:
                print(text, end = end)

    def relate(self, initiator, target, type):
        #create new relation
        self.relations.append(relation(initiator, target, type, self.rounds_number))
    
    def resolve(self, relation):
        #This function resolves an existing relation
        self.relations.remove(relation)


class relation:
    def __init__(self, initiator, target, type, InitRound):
        self.initiator = initiator
        self.target = target
        #Type is what kind of relation this is
        #Haste 
        #Entangle
        #AuraOfProtection
        #Hex
        #ConjuredAnimal
        #GuidingBolt
        self.type = type
        self.InitRound = InitRound #The Round in which this was initialized

