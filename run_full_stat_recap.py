from Entity_class import *
from Encounter_Simulator import *
from Dm_class import DungeonMaster
import json

def run_full_stat_recap():
    #read out Informations for the simulation from json file
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    f = open(application_path + '/simulation_parameters.json')
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

if __name__ == '__main__':
    run_full_stat_recap()