from Entity_class import *
from Encounter_Simulator import *
import json

if __name__ == '__main__':
    #read out Informations for the simulation from json file
    f = open('simulation_parameters.json')
    data = json.load(f)
    parameters = data['simulation_parameters']
    Loaded_Entities = data['Entities']
    f.close

    #initiate the DM and check the printing#
    DM = DungeonMaster()
    if parameters['printing_on'] == 0:
        DM.block_print()
    else:
        DM.enable_print()

    #load the Entities for the fight
    Fighters = [entity(player['name'], player['team'], DM) for player in Loaded_Entities]
    full_statistical_recap(parameters['repetitions'], Fighters)