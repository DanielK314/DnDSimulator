from Entity_class import *
from Dm_class import *
from Dmg_class import *
from Token_class import *
import numpy

def reset(fight):
    for x in fight:
        x.long_rest()

def ConcentrationTest1(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[2] = 1
    Character.SpellBook['Haste'].cast([Character])
    if Character.is_concentrating == False: 
        print('Not Concentrated after cast')
        quit()
    else:
        Character.CHP = 200
        Character.changeCHP(dmg(100, 'true'), Enemy, was_ranged = False)
        if Character.is_concentrating == True:
            print('Still concentrated after break Con')
            quit()
        else:
            Character.long_rest()
            print('Concentration Test 1')
            return True

def ConcentrationTestEntangle(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[0] = 1
    Character.spell_dc = 100
    Character.SpellBook['Entangle'].cast([Enemy])
    if Character.is_concentrating == False: 
        print('Not Concentrated after cast')
        quit()
    if Enemy.restrained == False:
        print('not restrained')
        quit()
    Enemy.TM.resolveAll()
    if Character.is_concentrating == True:
        print('Still concentrated after break Con')
        quit()
    if Enemy.restrained:
        print('still restrained from entangle')
        quit()
    print('Concentration Test Entangle')
    return True

def HasteRoundTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[2] = 1
    Character.SpellBook['Haste'].cast([Character])
    if Character.is_concentrating == False: 
        print('Not Concentrated after cast')
        quit()
    else:
        for i in range(0,10):
            Character.end_of_turn()
        if Character.is_concentrating:
            print('Still concentrated')
            quit()
        if Character.is_hasted:
            print('Still Hasted')
            quit()
        Character.start_of_turn()
        if Character.action != 0 or Character.bonus_action != 0 or Character.attack_counter != 0:
            print('Should be exhaused from haste')
            quit()
        else:
            print('Haste Round Test')
            return True

def HasteUnconsciousTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[2] = 1
    Character.SpellBook['Haste'].cast([Character2])
    if Character.is_concentrating == False: 
        print('Not Concentrated after cast')
        quit()
    else:
        Character2.unconscious()
        if Character.is_concentrating:
            print('Still con after target unconscious')
            quit()
        else:
            print('Haste Unconscious Test')
            return True

def HexTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[0] = 1
    Character.SpellBook['Hex'].cast([Enemy])
    if Character.is_concentrating == False: 
        print('Not Concentrated after cast')
        quit()
    else:
        Enemy.unconscious()
        if Character.is_concentrating == False:
            print('Why lost con')
            quit()
        else:
            if Character.can_choose_new_hex == True:
                print('Hex Test')
                return True

def HexConTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[0] = 1
    Character.SpellBook['Hex'].cast([Enemy])
    if Character.is_concentrating == False: 
        print('Not Concentrated after cast')
        quit()
    else:
        Character.CHP = 200
        Character.changeCHP(dmg(100, 'true'), Enemy, was_ranged = False)
        if Character.is_hexing == True:
            print('Still Hexing after break Con')
            quit()
        if Character.can_choose_new_hex == True:
            print('should not choose a new Hex')
            quit()
        if Character.CurrentHexToken != False:
            print('should not still have Hex Token')
            quit()
        if Enemy.is_hexed:
            print('Still Hexed after break Con')
            quit()
        print('Hex Break Concentration Test')

def HexSwitchTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[0] = 1
    Character.SpellBook['Hex'].cast([Enemy])
    Enemy.unconscious()
    Enemy2.CHP = 100
    Character.end_of_turn()
    Character.AI.do_your_turn(fight)
    if Enemy2.is_hexed == False:
        print('Not changed Targets')
        print(Enemy2.is_hexed)
        for x in Enemy2.TM.TokenList:
            print(x.subtype)
        Enemy2.TM.update()
        print(Enemy2.is_hexed)
        quit()
    print('Hex switching Test')

def HuntersMarkTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[0] = 1
    Character.SpellBook['HuntersMark'].cast([Enemy])
    if Enemy.is_hunters_marked == False:
        print('Huntersmark not marked')
        quit()
    Enemy.unconscious()
    Enemy2.CHP = 100
    Character.end_of_turn()
    Character.AI.do_your_turn(fight)
    if Enemy2.is_hunters_marked == False:
        print('Not changed HM')
        print(Enemy2.is_hunters_marked)
        for x in Enemy2.TM.TokenList:
            print(x.subtype)
        Enemy2.TM.update()
        print(Enemy2.is_hunters_marked)
        quit()
    print('Hunters Mark Test')

def conjureAnimalsTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    TestFight = [Character]
    Character.spell_slot_counter[2] = 1
    Character.SpellBook['ConjureAnimals'].cast(TestFight)
    Character.CHP = 200
    Character.changeCHP(dmg(100, 'true'), Enemy, was_ranged = False)
    if Character.is_concentrating:
        print('Still concentrated')
        quit()
    if Character.has_summons:
        print('Has still summons')
        quit()
    for x in TestFight:
        if x.state != -1 and x != Character:
            print('Not all Summons vanish')
            print(len(TestFight))
            print([x.name for x in TestFight])
            print([x.state for x in TestFight])
            quit()
    for x in TestFight:
        if x != Character and x.is_summoned == False:
            print('Not all summons are summons')
            quit()
    Character.end_of_turn()
    Character.spell_slot_counter[2] = 1
    Character.SpellBook['ConjureAnimals'].cast(TestFight)
    for x in TestFight:
        if x != Character: x.death()
    if Character.is_concentrating:
        print('Still concentrated after all summons')
        quit()
    if Character.has_summons:
        print('Has still summons but all dead')
        quit()
    print('Conjure Animals Test')

def guidingBoltTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.spell_slot_counter[0] = 1
    Character.SpellBook['GuidingBolt'].cast(Enemy)
    if len(Character.TM.TokenList) == 0:
        print('Not Guiding Bolting')
        quit()
    if len(Enemy.TM.TokenList) == 0:
        print('Not Guiding Bolted')
        quit()
    Character.action = 1
    Character.attack(Enemy)

    if len(Character.TM.TokenList) != 0:
        print('Still Guiding Bolting')
        quit()
    if len(Enemy.TM.TokenList) != 0:
        print('Still Guiding Bolted')
        quit()
    print('Guiding Bolt Test')

def PrimalCompanionTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.knows_primal_companion = True
    Character.used_primal_companion = False
    Enemy.action = 0
    Enemy.reaction = 0 #should not attack
    fight = [Character, Enemy]
    Character.AI.do_your_turn(fight)
    if Character.used_primal_companion == False:
        print('No prim companion used')
        quit()
    if len(fight) != 3:
        print('Number fight off')
        quit()
    Character.death()
    if fight[2].state != -1:
        print('Companion didnt vanish')
        quit()

    Enemy.long_rest()
    fight = [Character, Enemy]
    Character.AI.do_your_turn(fight)
    Character.action = 1
    if len(fight) != 2:
        print('Player shouldnt be able to summon companion')
        quit()

    fight = [Character, Enemy]
    Character.long_rest()
    Enemy.long_rest()    
    Character.AI.do_your_turn(fight)
    fight[2].death()
    if len(Character.TM.TokenList) != 0:
        print('Not all token resolved')
        quit()
    
    print('Primal Companion')
    return True

def DodgeTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.use_dodge()
    if Character.is_dodged == False:
        print('not dodged')
        quit()
    if Character.action != 0:
        print('no action used')
        quit()
    if Enemy.check_attack_advantage(Character, False, False) != -1:
        print('no Disadv')
        quit()
    if Character.check_advantage(1) != 1:
        print('No dex adv.')
        quit()
    Character.start_of_turn()
    if Character.is_dodged:
        print('still dodged')
        quit()
    print('Dodge Test')

def SmiteTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.knows_smite = True
    for slot in Character.spell_slot_counter:
        slot = 0
    Character.spell_slot_counter[1] = 1
    Character.tohit = 100
    Character.has_range_attack = False
    Character.make_normal_attack_on(Enemy, [Character, Enemy], False)

    if Character.spell_slot_counter[1] != 0:
        print('didnt use smite')
        quit()
    Character.tohit = Character.base_tohit
    print('Smite Test')

def GreatWeaponMasterTest(Character, Character2, Character3, Enemy, Enemy2, Enemy3):
    Character.knows_great_weapon_master = True
    Character.tohit = 100
    Character.dmg = 30
    Character.attack_counter = 1
    Character.has_range_attack = False
    Character.make_normal_attack_on(Enemy, [Character, Enemy])
    if Character.attack_counter != 1:
        print('GWM didnt give extra attack')
        quit()
    print('great weapon master test')

if __name__ == '__main__':
    DM = DungeonMaster()
    DM.enable_print()
    Character = entity('Ape', 0, DM, archive=True)
    Character.orignial_name = 'Hero'
    Character2 = entity('Ape', 0, DM, archive=True)
    Character3 = entity('Ape', 0, DM, archive=True)
    Enemy = entity('Ape', 1, DM, archive=True)
    Enemy.orignial_name = 'Enemy'
    Enemy2 = entity('Ape', 1, DM, archive=True)
    Enemy3 = entity('Ape', 1, DM, archive=True)

    fight = [Character, Character2, Character3, Enemy, Enemy2, Enemy3]

    #Character lerns all spells 
    Character.SpellBook = dict()
    for x in Character.Spell_classes:
        spell_to_lern = x(Character)  #Initiate Spell
        spell_to_lern.is_known = True #Spell is known
        Character.SpellBook[spell_to_lern.spell_name] = spell_to_lern

    tests = [
        ConcentrationTest1,
        ConcentrationTestEntangle,
        HasteRoundTest,
        HasteUnconsciousTest,
        HexTest,
        HexConTest,
        HexSwitchTest,
        HuntersMarkTest,
        conjureAnimalsTest,
        PrimalCompanionTest,
        DodgeTest,
        SmiteTest,
        GreatWeaponMasterTest
    ]

    for test in tests:
        reset(fight)
        test(Character, Character2, Character3, Enemy, Enemy2, Enemy3)