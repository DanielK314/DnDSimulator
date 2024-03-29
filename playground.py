from Entity_class import *
from Dm_class import *
from Dmg_class import *
from Token_class import *
from Spell_class import *
import json
import time
from random import random



DM = DungeonMaster()
DM.enable_print()
Character = entity('Bard Lv5', 0, DM, archive=True)
Character2 = entity('Druid Lv5', 0, DM, archive=True)
Character3 = entity('Druid Lv5', 0, DM, archive=True)
Enemy = entity('Ogre', 1, DM, archive=True)
Enemy2 = entity('Ogre', 1, DM, archive=True)
Enemy2.name = 'Ogre2'
Enemy3 = entity('Ogre', 1, DM, archive=True)
Enemy3.name = 'Ogre3'
Enemy4 = entity('Ogre', 1, DM, archive=True)
Enemy4.name = 'Ogre4'

Kek = entity('Karheg', 0, DM, archive=False)

fight = [Character, Character2, Character3, Enemy2, Enemy, Enemy3, Enemy4, Kek]
#fight = [Character, Character2, Character3, Enemy]

print(Kek.AI.choose_spell(fight))

#Enemy.type = 'plant'
player = Character

# conditions = [player.restrained, player.is_blinded, player.is_stunned, player.is_incapacitated, player.is_paralyzed, player.is_poisoned]
# for x in conditions:
#     print(x)

# #lear all spells
# Character.SpellBook = dict()
# for x in Character.Spell_classes:
#     spell_to_lern = x(Character)  #Initiate Spell
#     spell_to_lern.is_known = True #Spell is known
#     Character.SpellBook[spell_to_lern.spell_name] = spell_to_lern


# Character.knows_stunning_strike = True
# Character.ki_points = 5
# Character.tohit = 10
# Character.dmg = 10
# Character.has_range_attack = False
# Character.attack_counter = 1
# Character.action = 1

# Character.spell_slot_counter[2] = 1

# Character.SpellBook['CallLightning'].cast([Enemy, Enemy2])
# #Character.end_of_turn()
# #Character.TM.resolveAll()
# #Character.start_of_turn()
# #Character.AI.do_your_turn(fight)
# Character.end_of_turn()
# Character.start_of_turn()
# Character.AI.do_your_turn(fight)

# DM.say(' ', True)

# from scipy.optimize import curve_fit
# import matplotlib.pyplot as plt

# #Fit
# from random import random
# data_x = [i for i in range(1,11)]
# data_y = [8, 6, 4, 3, 2, 1.5, 1, 0.75, 0.5, 0.25]
# model = lambda x, a, b, c: a/(x+b) + c
# popt, pcov = curve_fit(model, data_x, data_y)
# print(popt)

# fitx = data_x
# fity = [model(x, 38.4, 2.47, -2.95) for x in fitx]
# plt.plot(data_x, data_y, 'rx')
# plt.plot(fitx, fity, color= 'red')
# #plt.show()

# for x in range(1,11):
#     print(str(x) + ': ' + str(model(x, popt[0], popt[1], popt[2])))

# n = 100000
# start_time = time.time()
# for i in range(n):
#     string = ''
#     for j in range(10):
#         string += str(random())
#     print(string)
# run1 = (time.time()-start_time)
# start_time = time.time()
# for i in range(n):
#     string = ''
#     for j in range(10):
#         string.join(str(random()))
#     print(string)
# print(str(run1))
# print(str(time.time() - start_time))

# Character.AI.do_your_turn(fight)
# DM.say('')
# Enemy.make_normal_attack_on(Character, fight)

# n = 100000

# for i in range(50):
#     Token(Character.TM) #Add Tokens

# start_time = time.time()
# for i in range(n):
#     Character.TM.endOfTurn() #Loop through Tokens
#     print(i)
# run1 = (time.time()-start_time)

# start_time = time.time()
# count = 0
# for i in range(n):
#     if Character.has_armor_of_agathys:
#         print('Hello World')
#     if Character.knows_assassinate:
#         print('Hello World')
#     if Character.knows_action_surge:
#         print('Hello World')
#     if Character.knows_archery:
#         print('Hello World')
#     if Character.knows_agonizing_blast:
#         print('Hello World')
#     if Character.has_armor_of_agathys:
#         print('Hello World')
#     if Character.knows_assassinate:
#         print('Hello World')
#     if Character.knows_action_surge:
#         print('Hello World')
#     if Character.knows_archery:
#         print('Hello World')
#     if Character.knows_agonizing_blast:
#         print('Hello World')
#     count += 1
#     print(count)
# print(run1)
# print((time.time()-start_time))


# Enemy.type = 'undead'
# Character.SpellBook['Blight'].twin_cast([Enemy, Enemy2], 6)
# for x in Character.Spell_classes:
#     test_spell = x(Character)
#     print(x.score)
# Character.action = 1
# Character.attack(Enemy, is_ranged=True, other_dmg=200, tohit=100)
# Character.end_of_turn()
# Character.AI.choose_new_hex(fight)

# Character.SpellBook['ChillTouch'].twin_cast([Enemy,Enemy2])
# Enemy.changeCHP(dmg(-3, 'heal'), Character, was_ranged=False)