from Entity_class import *
from Dm_class import *
from Dmg_class import *
from Token_class import *
from Spell_class import *

DM = DungeonMaster()
DM.enable_print()
Character = entity('Bard Lv5', 0, DM, archive=False)
Character2 = entity('Druid Lv5', 0, DM, archive=True)
Character3 = entity('Druid Lv5', 0, DM, archive=True)
Enemy = entity('Ogre', 1, DM, archive=True)
Enemy2 = entity('Ogre', 1, DM, archive=True)
Enemy3 = entity('Ogre', 1, DM, archive=True)

fight = [Character, Character2, Character3, Enemy, Enemy2, Enemy3]

# Character.AI.do_your_turn(fight)
# DM.say('')
# Enemy.make_normal_attack_on(Character, fight)


if 'ChillTouch' in Character.SpellBook:
    print('Yes')

#Character3.make_normal_attack_on(Enemy2, fight)
#Character2.make_normal_attack_on(Enemy, fight)
Character.CHP = 1

Enemy.type = 'undead'
Character.SpellBook['Blight'].twin_cast([Enemy, Enemy2], 6)
# Character.action = 1
# Character.attack(Enemy, is_ranged=True, other_dmg=200, tohit=100)
# Character.end_of_turn()
# Character.AI.choose_new_hex(fight)

# Character.SpellBook['ChillTouch'].twin_cast([Enemy,Enemy2])
# Enemy.changeCHP(dmg(-3, 'heal'), Character, was_ranged=False)