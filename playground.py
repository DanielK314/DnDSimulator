from Entity_class import *

#DM must be initiated for the players once
DM = DungeonMaster()
DM.enable_print()

#Initiate Players
Goblin = entity('Goblin', 1, DM)
Paladin = entity('Paladin Lv3', 0, DM)

Fight = [Goblin, Paladin]

Paladin.AI.do_your_turn(Fight)
Goblin.AI.smart_attack(Fight)