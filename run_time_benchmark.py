from Entity_class import *
from Encounter_Simulator import *
from Dm_class import *

def run_time_benchmark():
    #initiate the DM and check the printing#
    DM = DungeonMaster()
    DM.block_print()
#    DM.enable_print()

    #load the Entities for the fight
    Entities =  {0:{'name': 'Dylara', 'team': 0},
                        1:{'name': 'Lazerus', 'team': 0},
                        2:{'name': 'Mel', 'team': 0},
                        3:{'name': 'Zenera', 'team': 0},
                        4:{'name': 'Brida', 'team': 0},
                        5:{'name': 'Lilo', 'team': 0},
                        6:{'name': 'Glogga', 'team': 0},
                        7:{'name': 'Fighter3', 'team': 0},
                        8:{'name': 'Schläger 1', 'team': 1},
                        9:{'name': 'Schläger 2', 'team': 1},
                        10:{'name': 'Schläger 3', 'team': 1},
                        11:{'name': 'Schläger 4', 'team': 1},
                        12:{'name': 'Young Dragon', 'team': 1},
                        13:{'name': 'Night Hag', 'team': 1},
                        14:{'name': 'Thoran', 'team': 1}
    }        
    Fighters = [entity(Entities[i]['name'], Entities[i]['team'], DM) for i in range(0,len(Entities))]
    print(full_statistical_recap(1000, Fighters))

if __name__ == '__main__':
    run_time_benchmark()