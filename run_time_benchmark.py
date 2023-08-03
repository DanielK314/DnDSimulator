from Entity_class import *
from Encounter_Simulator import *
from Dm_class import *

#run this as Time Benchmark

def run_time_benchmark():
    #initiate the DM and check the printing#
    DM = DungeonMaster()
    DM.block_print()
#    DM.enable_print()

    #load the Entities for the fight
    Entities =  {
        0:{"name": "Bard Lv5", "team": 0},
        1:{"name": "Barbarian Lv5", "team": 0},
        2:{"name": "Cleric Lv8", "team": 0},
        3:{"name": "Druid Lv 5", "team": 0},
        4:{"name": "Paladin Lv5", "team": 0},
        5:{"name": "Rogue Lv5", "team": 0},
        6:{"name": "Sorcerer lv8", "team": 0},
        7:{"name": "Warlock Lv5", "team": 0},
        8:{"name": "Wizard Lv5", "team": 0},
        9:{"name": "Young Dragon", "team": 1},
        10:{"name": "Vamire Spawn", "team": 1},
        11:{"name": "Thoran", "team": 1},
        12:{"name": "Ogre", "team": 1},
        13:{"name": "Guard", "team": 1},
        14:{"name": "Giant Eagle", "team": 1},
        15:{"name": "Goblin", "team": 1},
        16:{"name": "Flameskull", "team": 1},
        17:{"name": "Fire Elemental", "team": 1},
        18:{"name": "Displayer Beast", "team": 1}
    }

    Fighters = [entity(Entities[i]['name'], Entities[i]['team'], DM) for i in range(0,len(Entities))]
    print(full_statistical_recap(200, Fighters))  #Standard 200 rep

if __name__ == '__main__':
    run_time_benchmark()