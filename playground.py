from Entity_class import *
from Dm_class import *
from Dmg_class import *
from Token_class import *

DM = DungeonMaster()
DM.enable_print()
Character = entity('Bard Lv5', 0, DM, archive=True)
Character2 = entity('Druid Lv5', 0, DM, archive=True)
Character3 = entity('Wizard Lv5', 0, DM, archive=True)
Enemy = entity('Ogre', 1, DM, archive=True)
Enemy2 = entity('Ogre', 1, DM, archive=True)
Enemy3 = entity('Ogre', 1, DM, archive=True)

fight = [Character, Character2, Character3, Enemy, Enemy2, Enemy3]

Character.AI.do_your_turn(fight)
DM.say('')
Enemy.make_normal_attack_on(Character, fight)