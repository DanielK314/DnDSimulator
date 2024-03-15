from Ifstatement_class import ifstatements
from Dmg_class import dmg
from AI_class import AI
from Token_class import *
from Spell_class import *

from random import random, shuffle
import numpy as np
import json
import os
import sys

class entity:                                          #A Character
    def __init__(self, name, team, DM, archive = False, external_json = False):                  #Atk - Attack [+x to Hit, mean dmg]

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        if archive == False:
            path = application_path + '/Entities/' + str(name) + '.json'
        else:
            path = application_path + '/Archive/' + str(name) + '.json'

        if external_json == False:
            file = open(path)
            data = json.load(file)
            file.close()
        else:
            data = external_json


        self.data = data
        self.DM = DM
        self.TM = TokenManager(self)  #Token Manager

    #Base Properties
        self.name = str(name)
        self.orignial_name = str(name)        #restore name after zB WildShape
        self.team = team                                      #which Team they fight for
        self.type = str(data['Type'])
        self.base_type = self.type

        self.AC = int(data['AC'])         #Current AC that will be called, and reset at start of turn
        self.shape_AC =int(data['AC'])     #AC of the current form, changed by wild shape
        self.base_AC = int(data['AC'])      #AC of initial form, will be set to this after reshape
        self.HP = int(data['HP'])
        self.proficiency = int(data['Proficiency'])
        self.tohit = int(data['To_Hit'])
        self.base_tohit = int(data['To_Hit'])

        self.base_attacks = int(data['Attacks'])    #attacks of original form   #number auf Attacks
        self.attacks = self.base_attacks  #at end_of_turn attack_counter reset to self.attack
        self.dmg = float(data['DMG'])           #dmg per attack
        self.base_dmg = float(data['DMG'])
        self.offhand_dmg = float(data['OffHand']) #If 0, no Offhand dmg

        self.level = float(data['Level'])           #It is not fully implementet yet, but level is used in some functions already, Level is used as CR for wildshape and co
        try: self.strategy_level = int(data['StrategyLevel']) #Value 1-10, how strategig a player is, 10 means min. randomness
        except: self.strategy_level = 5 #Medium startegy
        if self.strategy_level < 1: self.strategy_level = 1
        if self.strategy_level > 10: self.strategy_level = 10

        #Calculate Random Weight, for target_attack_score function
        #random factor between 1 and the RandomWeight
        #Random Weight of 0 is no random, should not be 
        #Random Weight around 2 is average 
        self.random_weight = 38.4/(self.strategy_level+2.47)-2.95

    #Position management
        self.speed = int(data['Speed'])
        #positions: 0 - front line, 1 - mid, 2 - back line
        self.position_txt = data['Position'] #front is default
        self.base_position = 0
        if 'middle' in self.position_txt:
            self.base_position = 1
        elif 'back' in self.position_txt:
            self.base_position = 2
        self.position = self.base_position  #This position will be called
        # airborn = 3 for player who can fly
        #Can the Character use range attacks
        self.range_attack = int(data['Range_Attack'])
        if self.range_attack == 1:
            self.has_range_attack = True
        else:
            self.has_range_attack = False

    #Abilities and Stats    
        self.Str = int(data['Str'])
        self.Dex = int(data['Dex'])
        self.Con = int(data['Con'])
        self.Int = int(data['Int'])
        self.Wis = int(data['Wis'])
        self.Cha = int(data['Cha'])
        self.stats_list = [self.Str, self.Dex, self.Con, self.Int, self.Wis, self.Cha]       #used for temp changes and request
        self.base_stats_list = self.stats_list
        self.modifier = [round((self.stats_list[i] -10)/2 -0.1, 0) for i in range(0,6)]  #calculate the mod
        self.base_modifier = self.modifier

        #actually only the modifier are currently ever used
        self.saves_prof = data['Saves_Proficiency']        #Already in Entity, not implementet in fight functions tho
        #list for saves of all kind. if = 0, no advantage 
        #if > 0 has advantage
        #if < 0 has disadvantage
        self.HeroVillain = int(data['Hero_or_Villain'])

    #Damage Types
        self.damage_type = data['Damage_Type']
        self.base_damage_type = self.damage_type
        self.damage_resistances = data['Damage_Resistance']
        self.base_damage_resistamces = self.damage_resistances
        self.damage_immunity = data['Damage_Immunity']
        self.base_damage_immunity = self.damage_immunity
        self.damage_vulnerability = data['Damage_Vulnerabilities']
        self.base_damage_vulnerability = self.damage_vulnerability

        self.additional_resistances = ''     #for rage and stuff

        self.last_used_DMG_Type = data['Damage_Type']

    #Spellcasting
        self.spell_mod = int(data['Spell_Mod'])                    #spell modifier
        self.spell_dc = int(data['Spell_DC'])                                #spell save DC

        self.spell_slots = [int(data['Spell_Slot_' + str(i)]) for i in range(1,10)]  #fixed spell slots available ( 0 - Level1, 1 - Level2, ...)
        self.spell_slot_counter = [int(data['Spell_Slot_' + str(i)]) for i in range(1,10)] #current counter for used spell slots 

        #Spells known
        self.spell_list = data['Spell_List']

        #If this updates, the All_Spells in the GUI will load this
        #Keep this in Order of the Spell Level, so that it also fits for the GUI
        self.SpellNames = ['FireBolt', 'ChillTouch', 'EldritchBlast',
                           'BurningHands', 'MagicMissile', 'GuidingBolt', 'Entangle', 'CureWounds', 'HealingWord', 'Hex', 'ArmorOfAgathys', 'FalseLife', 'Shield', 'InflictWounds', 'HuntersMark',
                           'AganazzarsSorcher', 'ScorchingRay', 'Shatter', 'SpiritualWeapon',
                           'Fireball', 'LightningBolt', 'Haste', 'ConjureAnimals', 'CallLightning',
                           'Blight', 'SickeningRadiance', 'WallOfFire', 'Polymorph',
                           'Cloudkill']
        #Add here all Spell classes that are impemented
        self.Spell_classes = [firebolt, chill_touch, eldritch_blast,
                         burning_hands, magic_missile, guiding_bolt, entangle, cure_wounds, healing_word, hex, armor_of_agathys, false_life, shield, inflict_wounds, hunters_mark,
                         aganazzars_sorcher, scorching_ray, shatter, spiritual_weapon,
                         fireball, lightningBolt, haste, conjure_animals, call_lightning,
                         blight, sickeningRadiance, wallOfFire, polymorph,
                         cloudkill]
        #A Spell Class will only be added to the spellbook, if the Spell name is in self.spell_list
        self.SpellBook = dict()
        for x in self.Spell_classes:
            spell_to_lern = x(self)  #Initiate Spell
            if spell_to_lern.is_known: #If Spell is known, append to SpellBook
                self.SpellBook[spell_to_lern.spell_name] = spell_to_lern

        #Haste
        self.is_hasted = False
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        #Hex 
        self.is_hexed = False
        self.is_hexing = False
        self.can_choose_new_hex = False 
        self.CurrentHexToken = False #This is the Hex Concentration Token
        #Hunters Mark
        self.is_hunters_marked = False
        self.is_hunters_marking = False
        self.can_choose_new_hunters_mark = False 
        self.CurrentHuntersMarkToken = False #This is the Hunters Mark Concentration Token
        #Armor of Agathys
        self.has_armor_of_agathys = False
        self.agathys_dmg = 0
        #Spiritual Weapon
        self.has_spiritual_weapon = False
        self.SpiritualWeaponDmg = 0
        self.SpiritualWeaponCounter = 0
        #Conjure Animals
        self.is_summoned = False       #if True it will be removed from fight after dead
        self.summoner = False      #general for all summoned entities
        self.has_summons = False
        #Guiding Bolt
        self.is_guiding_bolted = False
        #Chill Touch
        self.chill_touched = False
        #Cloudkill
        self.is_cloud_killing = False
        #sickening radiance
        self.is_using_sickening_radiance = False



    #Special Abilities
        self.other_abilities = data['Other_Abilities']
        #Action Surge
        if 'ActionSurge' in self.other_abilities:
            self.knows_action_surge = True
        else: self.knows_action_surge = False
        self.action_surges = int(data['ActionSurges'])       #The base how many action surge the player has
        self.action_surge_counter = self.action_surges
        self.action_surge_used = False
        #Improved Critical
        if 'ImprovedCritical' in self.other_abilities:
            self.knows_improved_critical = True
        else:self.knows_improved_critical = False
        #Second Wind
        if 'SecondWind' in self.other_abilities:
            self.knows_second_wind = True
        else:
            self.knows_second_wind = False
        self.has_used_second_wind = False

        #Archery
        if 'Archery' in self.other_abilities:
            self.knows_archery = True
        else: self.knows_archery = False
        #Great Weapon Fighting
        if 'GreatWeaponFighting' in self.other_abilities:
            self.knows_great_weapon_fighting = True
        else: self.knows_great_weapon_fighting = False
        #Interception
        if 'Interception' in self.other_abilities:
            self.knows_interception = True
        else: self.knows_interception = False
        self.interception_amount = 0 #is true if a interceptor is close, see end_of_turn

        #UncannyDodge
        if 'UncannyDodge' in self.other_abilities:
            self.knows_uncanny_dodge = True
        else:
            self.knows_uncanny_dodge = False
        #Cunning Action
        self.knows_cunning_action = False
        if 'CunningAction' in self.other_abilities:
            self.knows_cunning_action = True
        #Wails from the Grave
        self.wailsfromthegrave = 0
        self.wailsfromthegrave_counter = self.proficiency
        if 'WailsFromTheGrave' in self.other_abilities:
            self.wailsfromthegrave = 1    #is checked in Attack Function, wails from the grave adds just ot sneak attack at the moment, improvement maybe?
        #Sneak Attack
        self.sneak_attack_dmg = float(data['Sneak_Attack_Dmg'])        #If Sneak_Attack is larger then 0, the Entity has sneak Attack
        self.sneak_attack_counter = 1                  #set 0 after sneak attack     
        #Assassinate
        self.knows_assassinate = False
        if 'Assassinate' in self.other_abilities:
            self.knows_assassinate = True

        #RecklessAttack
        self.knows_reckless_attack = False
        if 'RecklessAttack' in self.other_abilities:
            self.knows_reckless_attack = True
        self.reckless = 0    #while reckless, u have ad but attacks against u have too, must be called in Player AI
        #Rage
        self.knows_rage = False
        self.rage_dmg = 0
        if 'Rage' in self.other_abilities:
            self.knows_rage = True
            self.rage_dmg = float(data['RageDmg'])
        self.raged = 0     # 1 if currently raging
        self.rage_round_counter = 0
        #Frenzy
        self.knows_frenzy = False
        if 'Frenzy' in self.other_abilities:
            self.knows_frenzy = True
        self.is_in_frenzy = False
        if 'BearTotem' in self.other_abilities:
            self.knows_bear_totem = True
        else:
            self.knows_bear_totem = False
        if 'EagleTotem' in self.other_abilities:
            self.knows_eagle_totem = True
        else:
            self.knows_eagle_totem = False
        if 'WolfTotem' in self.other_abilities:
            self.knows_wolf_totem = True
        else:
            self.knows_wolf_totem = False
        self.has_wolf_mark = False #Is true if you were attacked last by a Totel of the Wolf barbarian
        
        #Lay On Hands
        self.lay_on_hands = int(data['Lay_on_Hands_Pool'])            #pool of lay on hands pool
        self.lay_on_hands_counter = self.lay_on_hands    #lay on hands pool left
        #Smite
        self.knows_smite = False
        if 'Smite' in self.other_abilities:
            self.knows_smite = True
        #Aura of Protection
        self.knows_aura_of_protection = False
        if 'AuraOfProtection' in self.other_abilities:
            self.knows_aura_of_protection = True
            #Is implemented in the do_your_turn function via area of effect chooser

        #Inspiration
        if 'Inspiration' in self.other_abilities:
            self.knows_inspiration = True
            self.inspiration_die = int(data['Inspiration'])
            if self.inspiration_die not in [0,2,3,4,5,6]:
                self.inspiration_die = 0
        else:
            self.knows_inspiration = False
            self.inspiration_die = 0
        self.inspired = 0   #here the amount a target is inspired
        if self.modifier[5] > 0: self.base_inspirations = self.modifier[5]
        else: self.base_inspirations = 1
        self.inspiration_counter = self.base_inspirations     #for baric inspiration char mod
        #Combat Inspiration
        if 'CombatInspiration' in self.other_abilities:
            self.knows_combat_inspiration = True
        else: self.knows_combat_inspiration = False
        self.is_combat_inspired = False 
        if 'CuttingWords' in self.other_abilities:
            self.knows_cutting_words = True
        else: self.knows_cutting_words = False

        #ChannelDevinity
        self.channel_divinity_counter = int(data['ChannelDivinity'])
        if self.channel_divinity_counter > 0:
            self.knows_channel_divinity = True
        else:
            self.knows_channel_divinity = False
        #Turn Undead
        if 'TurnUndead' in self.other_abilities:
            self.knows_turn_undead = True
        else:
            self.knows_turn_undead = False
        self.is_a_turned_undead = False
        self.turned_undead_round_counter = 0
        #DestroyUndead
        self.destroy_undead_CR = float(data['DestroyUndeadCR'])

        #Agonizing Blast
        self.knows_agonizing_blast = False
        if 'AgonizingBlast' in self.other_abilities:
            self.knows_agonizing_blast = True

        #Primal Companion
        try: self.favored_foe_dmg = float(data['FavoredFoeDmg'])
        except: self.favored_foe_dmg = 0
        self.knows_favored_foe = False
        self.favored_foe_counter = self.proficiency
        self.has_favored_foe = False
        if self.favored_foe_dmg > 0: self.knows_favored_foe = True
        self.knows_primal_companion = False
        self.used_primal_companion = False  #only use once per fight
        if 'PrimalCompanion' in self.other_abilities:
            self.knows_primal_companion = True
        self.primal_companion = False 
        self.knows_beastial_fury = False
        if 'BestialFury' in self.other_abilities:
            self.knows_beastial_fury = True

    #Feats
        #Great Weapon Master
        self.knows_great_weapon_master = False
        if 'GreatWeaponMaster' in self.other_abilities:
            self.knows_great_weapon_master = True
        self.has_additional_great_weapon_attack = False
        self.knows_polearm_master = False
        if 'PolearmMaster' in self.other_abilities:
            self.knows_polearm_master = True
            poleArmDMG = 2.5 + max(self.base_modifier[0], self.base_modifier[1]) #Dex or Str
            if self.offhand_dmg < poleArmDMG:
                self.offhand_dmg = poleArmDMG #1d4 + attack mod

    #Meta Magic
        self.sorcery_points_base = int(data['Sorcery_Points'])
        self.sorcery_points = self.sorcery_points_base
        self.knows_quickened_spell = False
        if 'QuickenedSpell' in self.other_abilities:
            self.knows_quickened_spell = True
        self.quickened_spell = 0  #if 1 a Action Spell will be casted as BA, can be called as via quickened Spell function from spell class
        self.knows_empowered_spell = False
        if 'EmpoweredSpell' in self.other_abilities:
            self.knows_empowered_spell = True
        self.empowered_spell = False #if True, the next Spell will ne empowered (20% mehr dmg)
        self.knows_twinned_spell = False
        if 'TwinnedSpell' in self.other_abilities:
            self.knows_twinned_spell = True

    # Ki Points
        try: self.ki_points_base = int(data['Ki_Points'])
        except: self.ki_points_base = 0
        self.ki_points = self.ki_points_base
        self.ki_save_dc = 8 + self.proficiency + self.modifier[4]
        self.knows_deflect_missiles = False
        if 'DeflectMissiles' in self.other_abilities:
            self.knows_deflect_missiles = True
        self.knows_flurry_of_blows = False
        if 'FlurryOfBlows' in self.other_abilities:
            self.knows_flurry_of_blows = True
        self.knows_patient_defense = False
        if 'PatientDefense' in self.other_abilities:
            self.knows_patient_defense = True
        self.knows_step_of_the_wind = False
        if 'StepOfTheWind' in self.other_abilities:
            self.knows_step_of_the_wind = True
        self.knows_stunning_strike = False
        if 'StunningStrike' in self.other_abilities:
            self.knows_stunning_strike = True
        self.knows_open_hand_technique = False
        if 'OpenHandTechnique' in self.other_abilities:
            self.knows_open_hand_technique = True

    #Monster Abilites
        self.knows_dragons_breath = False
        if 'DragonsBreath' in self.other_abilities:
            self.knows_dragons_breath = True
        self.knows_spider_web = False
        if 'SpiderWeb' in self.other_abilities:
            self.knows_spider_web = True
        self.knows_poison_bite = False
        self.poison_bites = 1         #Only once per turn
        self.poison_bite_dmg = 0      #dmg of poison bite
        self.poison_bite_dc = 0
        if 'PoisonBite' in self.other_abilities:
            self.knows_poison_bite = True
            #Dmg roughly scales with Level
            self.poison_bite_dmg = 8 + self.level*3
            self.poison_bite_dc = int(11.1 + self.level/3)
        
        self.knows_recharge_aoe = False
        if 'RechargeAOE' in self.other_abilities:
            self.knows_recharge_aoe = True

        try: self.aoe_recharge_dmg = data['AOERechargeDmg']
        except: self.aoe_recharge_dmg = 0
        try: self.aoe_recharge_dc = int(data['AOERechargeDC'])
        except: self.aoe_recharge_dc = 0
        try: self.aoe_save_type = int(data['AOESaveType']) #0 - Str, 1 - Dex, ...
        except: self.aoe_save_type = 0
        try: self.aoe_recharge_area = int(data['AOERechargeArea'])
        except: self.aoe_recharge_area = 0
        try:
            self.aoe_recharge_propability = float(data['AOERechargePropability'])
            if self.aoe_recharge_propability > 1: self.aoe_recharge_propability = 1
            if self.aoe_recharge_propability < 0: self.aoe_recharge_propability = 0
        except: self.aoe_recharge_propability = 0
        try: self.aoe_recharge_type = data['AOERechargeType']
        except: self.aoe_recharge_type = 'fire'

        try: self.start_of_turn_heal = int(data['StartOfTurnHeal'])
        except: self.start_of_turn_heal = 0  #heals this amount at start of turn

        try: self.legendary_resistances = int(data['LegendaryResistances'])
        except: self.legendary_resistances = 0
        self.legendary_resistances_counter = self.legendary_resistances

    #Wild Shape / New Shapes
        self.shape_name = ''
        self.shape_remark = ''
        self.is_shape_changed = False
        self.is_in_wild_shape = False

        self.BeastForms = {
            0:{'Name': 'Wolf', 'Level': 0.25},
            1:{'Name': 'Brown Bear', 'Level': 1},
            2:{'Name': 'Crocodile', 'Level': 0.5},
            3:{'Name': 'Ape', 'Level': 0.5},
            4:{'Name': 'Giant Eagle', 'Level': 1},
            5:{'Name': 'Giant Boar', 'Level': 2},
            6:{'Name': 'Polar Bear', 'Level': 2},
            7:{'Name': 'Boar', 'Level': 0.25}
        }
        self.DruidCR = 0
        self.knows_wild_shape = False
        if 'WildShape' in self.other_abilities:
            self.knows_wild_shape = True
            self.DruidCR = float(data['DruidCR']) #This is the max CR in which the druid can wild shape
            if self.DruidCR < 0.25: self.DruidCR = 0.25 #min CR

        self.knows_combat_wild_shape = False
        if 'CombatWildShape' in self.other_abilities:
            self.knows_combat_wild_shape = True
        self.shape_HP = 0                       #temp HP of the current (different) shape
        self.wild_shape_uses = 2

    #Fight Counter
        self.state = 1                       # 1 - alive, 0 - uncouncious, -1 dead
        self.death_counter = 0
        self.heal_counter = 0
        self.CHP = self.HP                                 #CHP - current HP
        self.THP = 0         #Temporary HitPoints (dont stack)
        self.initiative = 0
        self.attack_counter = self.attacks           #will be reset to attack at start of turn
        self.is_attacking = False #Is set true if player has used acktion to attack
        self.unconscious_counter = 0       #This counts how often the player was unconscious in the fight for the statistics

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.has_cast_left = True #if a spell is cast, hast_cast_left = False
        self.is_concentrating = False

        #Conditions
        self.restrained = False            #will be ckeckt wenn attack/ed, !!!!!!!!! only handle via Tokens
        self.prone = 0
        self.is_blinded = False    #tokensubtype bl
        self.is_dodged = False    #is handled by the DodgedToken
        self.is_stunned = False   #tokensubtype st
        self.is_incapacitated = False  #tokensubtype ic
        self.is_paralyzed = False  #tokensubtype pl
        self.is_poisoned = False   #tokensubtype ps
        self.is_invisible = False   #tokensubtype iv

        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0

        self.dash_target = False
        self.has_dashed_this_round = False
        self.no_attack_of_opportunity_yet = True

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False
        self.recharge_aoe_is_charged = False

    #AI
        self.AI = AI(self)

    def rollD20(self, advantage_disadvantage=0): #-1 is disadvantage +1 is advantage
        d20_1 = int(random()*20 + 1)
        d20_2 = int(random()*20 + 1)
        if advantage_disadvantage > 0:
            d20 = max([d20_1, d20_2])
        elif advantage_disadvantage < 0:
            d20 = min([d20_1, d20_2])
        else:
            d20 = d20_1
        
        #Inspiration hits here, at the top most layer of this simulation, creazy isnt it 
        if self.inspired != 0:
            #Only use it if roll is low, but not that low
            if d20 < 13 and d20 > 6:
                d20 += self.inspired
                self.inspired = 0
                self.is_combat_inspired = False
                self.DM.say('(with inspiration), ')
        return d20

#---------------------Character State Handling----------------
    def unconscious(self):
        self.DM.say(self.name + ' is unconscious ', True)
        self.CHP = 0
        self.state = 0   # now unconscious
        self.unconscious_counter += 1 #for statistics

        #if u get uncounscious:
        self.end_rage()
        self.break_concentration()
        self.TM.unconscious()

        if self.team == 1: #this is for Monsters
            self.state = -1
    
    def get_conscious(self):
        self.DM.say(self.name + ' regains consciousness', True)
        self.state = 1
        self.heal_counter = 0
        self.death_counter = 0

    def death(self):
        self.CHP = 0
        self.state = -1
        #if u die:
        self.end_rage()
        self.break_concentration()
        self.TM.death()

    def check_uncanny_dodge(self, dmg):
        #-----------Uncanny Dodge
        if self.knows_uncanny_dodge:
            if dmg.abs_amount() > 0 and self.reaction == 1 and self.state == 1: #uncanny dodge condition
                dmg.multiply(1/2) #Uncanny Dodge halfs all dmg
                self.reaction = 0
                self.DM.say(' Uncanny Dodge')

    def check_new_state(self, was_ranged):
        #State Handling after Changing CHP

        #----------State Handling Unconscious
        if self.state == 0:         #if the player is dying
            if self.CHP > 0:           #was healed over 0
                self.get_conscious()
            if self.CHP <0:
                if self.CHP < -1*self.HP:
                    self.death()
                    self.DM.say(str(self.name) + ' died due to the damage ', True)
                else:
                    self.CHP = 0
                    if was_ranged:
                        self.death_counter += 1
                    else: #melee is auto crit
                        self.death_counter += 2
                    if self.death_counter >= 3:
                        self.death()
                        self.DM.say(str(self.name) + ' was attacked and died', True)
                    else:
                        self.DM.say(str(self.name) + ' death saves at ' + self.StringDeathCounter(), True)

        #----------State handling alive
        if self.state == 1:                    #the following is if the player was alive before
            if self.CHP < 0-self.HP:              #if more then -HP dmg, character dies
                self.death()
                self.DM.say(str(self.name) + ' died due to the damage ', True)
            if self.CHP <= 0 and self.state != -1:   #if below 0 and not dead, state dying 
                self.unconscious()

    def changeCHP(self, Dmg, attacker, was_ranged):
        self.check_uncanny_dodge(Dmg)

        damage = Dmg.calculate_for(self) #call dmg class, does the Resistances 
        #This calculates the total dmg with respect to resistances

        #-----------Statistics
        if damage > 0:
            attacker.dmg_dealed += damage
            if attacker.is_summoned:   #Append the dmg of summons to summoner
                attacker.summoner.dmg_dealed += damage
            attacker.last_used_DMG_Type = Dmg.damage_type()
        elif damage < 0:
            attacker.heal_given -= damage

        #---------Damage Deal
        AgathysDmg = dmg() #0 dmg
        if damage > 0:                 #if damage, it will be checkt if wild shape HP are still there
            if self.is_a_turned_undead:
                self.end_turned_undead()
            self.make_concentration_check(damage) #Make Concentration Check for the dmg
            #Concentration Checks are done in and outside of wild shape/other shapes
            if self.is_shape_changed:
                self.change_shape_HP(damage, attacker, was_ranged)
                #Not checking resistances anymore, already done 
            else:
                if self.THP > 0:     #Temporary Hitpoints
                    AgathysDmg = self.check_for_armor_of_agathys() #returns the agathys dmg
                    if damage < self.THP: #Still THP
                        self.THP -= damage
                        self.DM.say(self.name + ' takes DMG: ' + Dmg.text() + 'now: ' + str(round(self.CHP,2)) + ' + ' + str(round(self.THP,2)) + ' temporary HP', True)
                        damage = 0
                    else: #THP gone
                        damage = damage - self.THP #substract THP
                        self.THP = 0
                        self.DM.say('temporaray HP empty, ')

                #Change CHP
                if damage > 0: #If still damage left
                    self.CHP -= damage
                    self.DM.say(self.name + ' takes DMG: ' + Dmg.text() + 'now at: ' + str(round(self.CHP,2)), True)

        #---------Armor of Agathys 
        if AgathysDmg.abs_amount() > 0 and was_ranged == False:
            self.DM.say(attacker.name + ' is harmed by the Armor of Agathys', True)
            attacker.changeCHP(AgathysDmg, self, was_ranged=False)

        #---------Heal
        if damage < 0:               #neg. damage is heal Currently Heal is always applied to CHP never to shape HP
            if self.state == -1:
                print('This is stupid, dead cant be healed', True)
                quit()
            if self.chill_touched: 
                self.DM.say(self.name + ' is chill touched and cant be healed.')
            elif abs(self.HP - self.CHP) >= abs(damage):
                self.CHP -= damage    
                self.DM.say(str(self.name) + ' is healed for: ' + str(-damage) + ' now at: ' + str(round(self.CHP,2)), True)
            else:                     #if more heal then HP, only fill HP up
                damage = -1*(self.HP - self.CHP)
                self.CHP -= damage
                self.DM.say(str(self.name) + ' is healed for: ' + str(-damage) + ' now at: ' + str(round(self.CHP,2)), True)

        self.check_new_state(was_ranged)

    def change_shape_HP(self, damage, attacker, was_ranged):
        if damage < self.shape_HP:     #damage hits the wild shape
            self.shape_HP -= damage
            self.DM.say(str(self.name) + ' takes damage in ' + self.shape_remark + ' shape: ' + str(round(damage,2)) + ' now: ' + str(round(self.shape_HP,2)), True)
        else:                  #wild shape breakes, overhang goes to changeCHP
            overhang_damage = abs(self.shape_HP - damage)
            #reshape after critical damage
            self.DM.say(str(self.name) + ' ' + self.shape_remark + ' shape breaks ', True)
            self.drop_shape()  #function that resets the players stats
            #Remember, this function is called in ChangeCHP, so resistances and stuff has already been handled
            #For this reason a 'true' dmg type is passed here
            Dmg = dmg(overhang_damage, 'true')
            self.changeCHP(Dmg, attacker, was_ranged)

    def addTHP(self, newTHP):
        if self.THP == 0: #currently no THP
            self.THP = newTHP
        elif self.has_armor_of_agathys:
            self.THP = newTHP
            self.break_armor_of_agathys()
            #New THP will break the Armor
        else:
            self.THP = newTHP
        self.DM.say(self.name + ' gains ' + str(newTHP) + ' temporary HP', True)

    def stand_up(self):
        rules = [self.prone == 1, self.restrained == 0]
        errors = [self.name + ' tried to stand up but is not prone', 
                self.name + ' tried to stand up, but is restrained']
        ifstatements(rules, errors, self.DM).check()
        self.prone = 0
        self.DM.say(self.name + ' stood up to end prone', True)

    def dps(self):
        #DPS is a reference used to determine the performance of the player so far in the fight
        #It is used by some AI functions to determine the value of the target in a fight
        #This Function returns a value for the dps
        #Heal is values 2 times dmg
        return (self.dmg_dealed + self.heal_given*2)/self.DM.rounds_number

    def value(self):
        #This function is designed to help decision making in AI
        #It returns a current, roughly dmg equal score of the entity to compare how important it is for the team
        #Score that should be roughly a dmg per round equal value
        Score = self.dps() #see .dps() func, is dmg and heal*2 per turn
        if self.is_invisible:
            Score = Score*1.2
        if self.is_hasted:
            Score = Score*1.1

        if self.prone == 1:
            Score = Score*0.95
        if self.restrained == 1:
            Score = Score*0.9
        if self.is_blinded:
            Score = Score*0.9
        if self.is_poisoned:
            Score = Score*0.95
        if self.is_incapacitated:
            Score = Score*0.2
        if self.is_stunned:
            Score = Score*0.15
        if self.is_paralyzed:
            Score = Score*0.1
        return Score

    def update_additional_resistances(self):
        #If this function is called it checks all possible things that could add a resisantace
        self.additional_resistances = ''
        if self.raged == 1:
            self.additional_resistances += 'piercing, bludgeoning, slashing, '
            if self.knows_bear_totem:
                self.additional_resistances += 'acid, cold, fire, force, lightning, thunder, necrotic, poison, radiant'

#---------------------Checks and Saves
    def make_check(self, which_check):  #0-Str, 1-Dex, ...
        d20_roll = self.rollD20()
        result = d20_roll + self.modifier[which_check]  #calc modifier
        return result

    def check_advantage(self, which_save, extraAdvantage = 0, notSilent = True):
        saves_adv_dis = [0,0,0,0,0,0] #calculate all factors to saves:
        text = '' #collect text to say
        if self.restrained == 1:  #disadvantage in dex if restrained
            saves_adv_dis[1] -= 1
            text += 'restrained, '
        if self.is_dodged:
            saves_adv_dis[1] += 1  #dodge adv on dex save
            text += 'dodged, '

        if self.raged == 1:   #str ad if raged
            saves_adv_dis[0] += 1
            text += 'raging, '
        if self.is_hasted:
            saves_adv_dis[1] += 1
            text += 'hasted, '
        if self.is_hexed:
            HexType = int(random()*2 + 1) #random hex disad at Str, Dex or Con
            HexText = ['Str ', 'Dex ', 'Con ']
            text += 'hexed ' + HexText[HexType] + ', '
            saves_adv_dis[HexType] -= 1 #one rand disad 
        if extraAdvantage != 0: #an extra, external source of advantage
            if extraAdvantage > 0:
                text += 'adv, '
            else:
                text += 'disad, '
    
        if notSilent: self.DM.say(text) #only if not silent
        return saves_adv_dis[which_save] + extraAdvantage

    def make_save(self, which_save, extraAdvantage = 0, DC = False):          #0-Str, 1-Dex, 2-Con, 3-Int, 4-Wis, 5-Cha
    #how to disadvantage and advantage here !!!
        save_text = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        self.DM.say(str(self.name) + ' is ', True)
        Advantage = self.check_advantage(which_save, extraAdvantage = extraAdvantage)
        AuraBonus = self.protection_aura()
        if AuraBonus > 0:
            self.DM.say('in protection aura, ')
        if Advantage < 0:
            d20_roll = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('in disadvantage doing a ' + save_text[which_save] + ' save: ')
        elif Advantage > 0:
            d20_roll = self.rollD20(advantage_disadvantage=1)
            self.DM.say('in advantage doing a ' + save_text[which_save] + ' save: ')
        else:
            d20_roll = self.rollD20(advantage_disadvantage=0)
            self.DM.say('doing a ' + save_text[which_save] + ' save: ')

        modifier = self.modifier[which_save]
        if save_text[which_save] in self.saves_prof: #Save Proficiency
            modifier += self.proficiency
        result = d20_roll + modifier + AuraBonus #calc modifier

        #Legendary Resistances
        if result < DC and self.legendary_resistances_counter > 0:
            self.legendary_resistances_counter -= 1
            self.DM.say(self.name + ' uses a legendary resistance: ' + str(self.legendary_resistances_counter) + '/' + str(self.legendary_resistances))
            return 10000  #make sure to pass save
        else:
            #Just display text 
            roll_text = str(int(d20_roll)) + ' + ' + str(int(modifier))
            if AuraBonus != 0: roll_text += ' + ' + str(int(AuraBonus))
            if DC != False: roll_text += ' / ' + str(DC) + ' '
            self.DM.say(roll_text)
            return result

    def make_death_save(self):
        d20_roll = int(random()*20 + 1)
        AuraBonus = self.protection_aura()
        if AuraBonus > 0:
            d20_roll += AuraBonus
            self.DM.say(''.join(['Aura of protection +',str(int(AuraBonus)),' : ']), True)
        self.DM.say(self.StringDeathCheck(d20_roll), True)
        if self.death_counter >= 3:
            self.death()
            self.DM.say(str(self.name) + ' failed death save and died', True)
        if self.heal_counter >= 3:
            self.CHP = 1
            self.get_conscious()

    def StringDeathCheck(self, d20_roll):
        if d20_roll < 11:
            self.death_counter += 1
            TextResult = str(self.name) + ' did not made the death save '
        elif d20_roll > 10 and d20_roll != 20:
            self.heal_counter += 1
            TextResult = str(self.name) + ' made the death save'
        if d20_roll == 20:
            self.heal_counter += 2
            TextResult = str(self.name) + ' made the death save critical'
        TextResult += self.StringDeathCounter()
        return TextResult

    def StringDeathCounter(self):
        text = '(' + str(self.death_counter) + '-/' + str(self.heal_counter) + '+)'
        return text 

#---------------Concentration and Conjuration Spells-----------
    def make_concentration_check(self, damage):
        if self.is_concentrating:
            saveDC = 10
            if damage/2 > 10: saveDC = int(damage/2)
            save_res = self.make_save(2, DC=saveDC)
            if save_res >= saveDC:   #concentration is con save
                return 
            else:
                self.break_concentration()
                return 
        else:
            return

    def break_concentration(self):
        self.TM.break_concentration()
        #Will test for concentration tokens
        #If Concentration breaks, it will say so

    def break_armor_of_agathys(self):
        if self.has_armor_of_agathys and self.THP > 0:
            self.has_armor_of_agathys = False
            self.THP = 0
            self.agathys_dmg = 0
            self.DM.say(self.name + ' Armor of Agathys breaks, ')
        else:
            print(self.name + ' Armor of Agathys broke without having one')
            quit()

    def break_spiritual_weapon(self):
        if self.has_spiritual_weapon:
            self.has_spiritual_weapon = False
            self.SpiritualWeaponCounter = 0 #reset counter
            self.SpiritualWeaponDmg = 0
            self.DM.say('Spiritual Weapon of ' + self.name + ' vanishes, ')
    
    def end_turned_undead(self):
        self.is_a_turned_undead == False #no longer turned
        self.turned_undead_round_counter = 0
        self.DM.say(self.name + ' is no longer turned', True)

#--------------------Position Management----------------------
    def need_dash(self, target, fight, AttackIsRanged = False):
        #0 - need no dash
        #1 - need dash
        #2 - not reachable

        #ABack-25ft-AMid-25ft-AFront-BFront-25ft-BMid-25ft-BBack
        #no Dash for ranged attacks
        if AttackIsRanged: return 0 
        if self.has_range_attack: return 0
        if target.position == 3: return 0 #Airborn is in range

        #The Distance between lines scales with how dense the Battlefield is
        # 0 Wide Space
        # 1 normal
        # 2 crowded
        distance = 25
        if self.DM.density == 0:
            distance = 50
        elif self.DM.density == 2:
            distance = 12.5


        EnemiesLeft = [x for x in fight if x.team != self.team and x.state == 1]
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]

        if self.position < 3: #0,1,2 Front, Mid, Back
            if len(EnemiesInFront) == 0 and len(EnemiesInMid) == 0: OpenLines=2 #open Front and Mid
            elif len(EnemiesInFront) == 0: OpenLines = 1 #open front
            else: OpenLines = 0 #no open line
        if self.position == 3: #airborn
            if target.position < 3: OpenLines=3 #basically 3 open lines
            else: return 0

        #Test if Dash is ness        
        #example: Mid Attacks Mid, no open front: 1 + 1 = 2*25ft = 50ft 
        if self.speed >= (target.position + self.position - OpenLines)*distance: return 0
        elif self.dash_target == target: return 0 #The player has used dash last round to get to this target
        #Only works if you can still dash with action or cunning action or eagle totem
        elif self.action == 1 or (self.knows_cunning_action and self.bonus_action ==1) or (self.knows_eagle_totem and self.bonus_action ==1):
            if 2*self.speed >= (target.position + self.position - OpenLines)*distance: return 1
            else: return 2 
        else: return 2

    def will_provoke_Attack(self, target, fight, AttackIsRanged = False):
        #this function tells if an attack of opportunity will be provoked
        if AttackIsRanged: return False
        if self.has_range_attack: return False
        if self.dash_target == target: return False

        EnemiesLeft = [x for x in fight if x.team != self.team and x.state == 1]
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]
        
        #Open Lines
        if self.position < 3: #0,1,2 Front, Mid, Back
            if len(EnemiesInFront) == 0 and len(EnemiesInMid) == 0: return False #open Front and Mid
            elif len(EnemiesInFront) == 0: OpenLines = 1 #open front
            else: OpenLines = 0 #no open line
        if self.position == 3: return False #no opp. attacks from the air

        #Compare Lines
        #if you cross more then 2 lines (like, front - back or mid - mid) you provoke opp. attack
        if self.position == 2:
            OpenLines += 1 #back Player can attack Front with no Opp Attack 
        if self.position + target.position - OpenLines >= 2:
            return True 
        else: return False

    def use_disengage(self):
        if self.bonus_action == 1 and self.knows_cunning_action:
            self.DM.say(self.name + ' used cunning action to disengage', True)
            self.bonus_action = 0
        elif self.action == 1:
            self.DM.say(self.name + ' used an action to disengage', True)
            self.action = 0
        else:
            print(self.name + ' tried to disengage, but has no action left', True)
            quit()

    def enemies_reachable_sort(self,fight, AttackIsRanged = False):
        #This function is used to determine which Enemies are theoretically in reach to attack for a Player
        #This also includes Players, that are only reachable by dashing or by provoking attacks of Opportunity

        #The following Rules Apply
        #----------0---------
        #Front can always melee attack the other front
        #Front can attack the other mid, if the player speed suffice
        #Front can attack the other back, if player speed suffice and by provoking an opportunity attack
        #If there is no Player in the other Front, the Front can melee attack mid and back
        #If there is no front, the distance to mid and back reduces
        #----------1---------
        #mid can meelee attack front
        #mid can attack mid, if speed suffices, and by provoking an opportunity attack
        #If there is no Player in the other Front, the mid can melee attack mid and back
        #If there is no Player in the other Front and Mid, mid can attack all
        #----------2---------
        #back can attack Front
        #----------3---------
        #airborn can melee attack all, but must land for that
        #if airborn lands, it is then in front
        #Airborn can not be attacked by melee at this point
        #----------R---------
        #If player has reanged attacks, player can attack all regardless

        #Idea: Line Airborn, only hittable by ranged 
        #At the start of turn, a creature desides to go airborn or land

        #This includes Character Players that are unconscious        
        EnemiesNotDead = [x for x in fight if x.team != self.team and (x.state == 1 or (x.team != 1 and x.state == 0))]
        
        if AttackIsRanged: return EnemiesNotDead #Everyone in Range
        if self.has_range_attack: return EnemiesNotDead #Everyone in Range
        if self.position == 3: return EnemiesNotDead #Everyone in Range
        
        EnemiesInFront = [Enemy for Enemy in EnemiesNotDead if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesNotDead if Enemy.position == 1]
        

        EnemiesInReach = []

        for i in range(0,len(EnemiesNotDead)):
        #This is to manually tell the function that the Attack is ranged, even if the player might not have ranged attacks, for Spells for example
            Enemy = EnemiesNotDead[i]
            if Enemy == self.dash_target: #last dash target is always in reach
                EnemiesInReach.append(Enemy) #Is in range 
                continue

        #All other lines front(0), mid(1), back(2)
            if self.position == 1:
                if Enemy.position == 2 and len(EnemiesInFront) != 0:
                    continue
            if self.position == 2:
                if Enemy.position == 1 and len(EnemiesInFront) != 0:
                    continue
                if Enemy.position == 2 and len(EnemiesInFront) != 0:
                    continue
                if Enemy.position == 2 and len(EnemiesInMid) != 0:
                    continue
            if Enemy.position == 3 and self.position !=3:
                continue
            DashValue = self.need_dash(Enemy, fight, AttackIsRanged= False)
            if DashValue == 2: #target is too far away
                continue
            
            #No False case, so in range
            EnemiesInReach.append(Enemy)
        return EnemiesInReach

    def use_dash(self, target):
        if self.knows_cunning_action and self.bonus_action == 1:
            self.DM.say(self.name + ' uses cunning action to dash to ' + target.name, True)
            is_BADash = True 
        elif self.knows_eagle_totem and self.bonus_action == 1:
            self.DM.say(self.name + ' uses eagle totem to dash to ' + target.name, True)
            is_BADash = True
        else:
            is_BADash = False
        if is_BADash:
            self.bonus_action = 0
            self.dash_target = target
            self.has_dashed_this_round = True
        elif self.action == 1:
            self.action = 0
            self.attack_counter = 0
            self.dash_target = target
            self.has_dashed_this_round = True
            self.DM.say(self.name + ' uses dash to get to ' + target.name, True)
        else:
            print(self.name + ' tried to dash, but has no action left', True)
            quit()

    def move_position(self):
        #This function will be called, if the player hat no target in reach last turn
        if self.position == 1: #if you are usually in mid go front 
            self.DM.say(self.name + ' moves to the front line', True)
            self.position = 0
            self.action = 0 #took the action

    def use_dodge(self):
        if self.action == 0:
            print(self.name + ' tried to dodge without action')
            quit()
        self.DM.say(self.name + ' uses its turn to dodge', True)
        self.action = 0 #uses an action to do
        DodgeToken(self.TM) #give self a dodge token
        #The dodge token sets and resolves self.is_dodge = True

#-------------------Attack Handling----------------------
    def make_attack_check(self, target, fight, is_off_hand):
        if self.action == 0 and self.is_attacking == False and is_off_hand == False:
            print(self.name + ' tried to attack, but has no action left')
            quit()
        elif self.bonus_action == 0 and is_off_hand:
            print(self.name + ' tried to offhand attack, but has no bonus attacks left')
            quit()
        elif is_off_hand and self.is_attacking == False:
            print(self.name + ' tried to offhand attack, but has not attacked with action')
            quit()
        elif self.attack_counter < 1 and is_off_hand == False:
            print(self.name + ' tried to attack, but has no attacks left')
            quit()
        elif self.state != 1:
            print(self.name +' treid to attack but is not conscious')
            quit()
        #check if target is in range
        elif target not in self.enemies_reachable_sort(fight):
            print(self.name + ' tried to attack, but ' + target.name + ' is out of reach')
            quit()            

    def check_dash_and_op_attack(self, target, fight, NeedDash):
        if NeedDash == 1:
            self.use_dash(target)
        if self.will_provoke_Attack(target, fight):
            if self.no_attack_of_opportunity_yet:#only one per turn
                #now choose whos doing the attack of opportunity
                EnemiesLeft = [x for x in fight if x.team != self.team and x.state == 1]
                EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
                if len(EnemiesInFront) > 0:
                    OpportunityAttacker = EnemiesInFront[int(random()*len(EnemiesInFront))]
                else:
                    OpportunityAttacker = EnemiesLeft[int(random()*len(EnemiesLeft))]
                if self.provoke_opportunit_attack(OpportunityAttacker) == False:
                    #false means that the attack killed the player
                    return #return and end the turn

    def make_normal_attack_on(self, target, fight, is_off_hand=False):
    #This is the function of a player trying to move to a target und making an attack
    #It also checks for Dash and does opportunity attacks if necessary

    #First Check for attck_counter
        self.make_attack_check(target, fight, is_off_hand)
        #target is within reach
        NeedDash = self.need_dash(target, fight)
        if NeedDash == 2:
            print(self.name + ' tried to attack, but ' + target.name + ' is out of reach, this is weird here, check enemies_rechable_sort')
            quit()
        #----attack of opportunity and dash
        self.check_dash_and_op_attack(target, fight, NeedDash)

        #The Player is now in range for attack
        is_ranged = False
        if self.has_range_attack: is_ranged = True

        if self.attack_counter == 0 and is_off_hand == False:
            #If you used the action to dash, return and end your turn here, if cunning action, then proceed
            return
        if is_off_hand:
            #Make Offhand Attack
            self.bonus_action = 0
            self.attack(target, is_ranged, other_dmg=self.offhand_dmg, is_offhand=True, is_spell=False)
        else:
            self.check_polearm_master(target, is_ranged) #Check if target is a polearm master
            self.action = 0 #if at least one attack, action = 0
            self.is_attacking = True #uses action to attack
            self.attack_counter -= 1 #Lower the attack counter 
            self.attack(target, is_ranged)

    def provoke_opportunit_attack(self, target):
        if self.no_attack_of_opportunity_yet: #only one per turn 
            self.DM.say(self.name + ' has provoked an attack of opportunity:', True)
            self.no_attack_of_opportunity_yet = False
            target.AI.do_opportunity_attack(self)
            if self.state != 1: return False
            else: return True
        else: return True

    def check_attack_advantage(self, target, is_ranged, is_opportunity_attack):
        #This function returns if an attack is advantage or disadvantage
        #No stats or tokens should be changed here, it is just a check
        #calculate all effects that might influence Disad or Advantage
        advantage_disadvantage = 0
        if target.state == 0:
            advantage_disadvantage += 1 #advantage against unconscious
            self.DM.say(target.name + ' unconscious, ')

        if target.reckless == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' reckless, ')
        if self.reckless == 1:
            advantage_disadvantage += 1    
            self.DM.say(self.name + ' reckless, ')
        if target.knows_eagle_totem and is_opportunity_attack:
            advantage_disadvantage -= 1
            #disadvantage for opp. att against eagle totem
            self.DM.say('eagle totem, ')
        if self.knows_assassinate:
            if self.DM.rounds_number == 1 and self.initiative > target.initiative:
                #Assassins have advantage against player that have not had a turn
                advantage_disadvantage += 1
                self.DM.say(self.name + ' assassinte, ')
        if target.has_wolf_mark and is_ranged == False:
            self.DM.say(target.name + ' has wolf totem, ')
            advantage_disadvantage += 1

        #Conditions
        if target.restrained == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' restrained, ')
        if self.restrained == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' restrained, ')
        if target.is_dodged:
            advantage_disadvantage -= 1
            self.DM.say(target.name + ' dodged, ',)
        if target.is_blinded:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' blinded, ')
        if self.is_blinded:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' blinded, ')
        if target.is_stunned:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' stunned, ')
        if self.is_invisible:
            advantage_disadvantage += 1
            self.DM.say(self.name + ' invisible')
        if target.is_invisible:
            advantage_disadvantage -= 1
            self.DM.say(target.name + ' invisible')
        if target.is_paralyzed:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' paralyzed')
        if self.is_poisoned:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' poisoned')

        if target.prone == 1:
            if is_ranged:
                advantage_disadvantage -=1 #disad for ranged against prone
            else:
                advantage_disadvantage += 1
            self.DM.say(target.name + ' prone, ')
        if self.prone == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' prone, ')
        if target.is_guiding_bolted:
            #This is set by the guidingBolted Token triggered bevore
            self.DM.say('guiding bolt, ')
            advantage_disadvantage += 1
            #Being guiding boltet is reset at the make_attack_roll function
            #It should not happen here, as I want to use this function also for AI stuff
            #It should therefor not change any status
        return advantage_disadvantage

    def make_attack_roll(self, target, is_ranged, is_opportunity_attack):
        #calculate all effects that might influence Disad or Advantage
        advantage_disadvantage = self.check_attack_advantage(target, is_ranged, is_opportunity_attack)
        if target.is_guiding_bolted:
            target.is_guiding_bolted = False #reset being boltet
            
        #Roll the Die to hit
        if advantage_disadvantage > 0:
            d20 = self.rollD20(advantage_disadvantage=1)
            self.DM.say('Advantage: ')
        elif advantage_disadvantage < 0:
            d20 = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('Disadvantage: ')
        else:
            d20 = self.rollD20(advantage_disadvantage=0)
        #The roll and advantage is returned, advantage is still important for sneak attack
        return d20 , advantage_disadvantage

    def check_polearm_master(self, target, is_ranged):
        #This function is called in the make normal attack function
        #At this point it is already clear it is no offhand attack and no opp. attack
        if target.knows_polearm_master:
            rules = [is_ranged == False,  #No range attacks
                     target.last_attacker != self, #if attacked before, you didnt just enter their range
                     target.reaction == 1]  #has reaction left
            if all(rules):
                self.DM.say(self.name + ' has entered the polearm range of ' + target.name, True)
                target.AI.do_opportunity_attack(self)

    def check_smite(self, target, Dmg, is_ranged, is_spell):
        if is_ranged == False and self.knows_smite and is_spell == False:  #smite only on melee
            slot = self.AI.want_to_use_smite(target) #returns slot or false
            if slot != False and self.spell_slot_counter[slot-1] > 0:
                #DMG calc
                if slot > 4: smitedmg = 4.5*5 #5d8 max
                else: smitedmg = 4.5*(slot + 1) #lv1 -> 2d8
                if target.type in ['undead', 'fiend']: smitedmg += 4.5 #extra d8 

                Dmg.add(smitedmg, 'radiant')
                self.spell_slot_counter[slot - 1] -= 1
                self.DM.say(''.join([self.name,' uses ',str(slot),'. lv Smite: +',str(smitedmg)]), True)

    def check_sneak_attack(self, Dmg, advantage_disadvantage, is_spell):
        if self.sneak_attack_dmg > 0:    #Sneak Attack 
            rules = [self.sneak_attack_counter == 1, 
                     advantage_disadvantage >= 0, #not in disadv.
                     is_spell == False
                     ]
            if all(rules):
                Dmg.add(self.sneak_attack_dmg, self.damage_type)
                self.DM.say(''.join([self.name,' Sneak Attack: +', str(self.sneak_attack_dmg)]), True)
                if self.wailsfromthegrave == 1 and self.wailsfromthegrave_counter > 0:  #if sneak attack hits and wails from the grave is active
                    Dmg.add(self.sneak_attack_dmg/2, 'necrotic')
                    self.wailsfromthegrave_counter -= 1
                    self.DM.say(' and ' + str(self.sneak_attack_dmg/2) + ' wails from the grave')
                self.sneak_attack_counter = 0

    def check_combat_inspiration(self, Dmg, is_spell):
        if self.is_combat_inspired and self.inspired > 0 and is_spell == False:
            #Works only for weapon dmg, so other_dmg == False
            Dmg.add(self.inspired, self.damage_type)
            self.DM.say(self.name + ' uses combat inspiration: +' + str(self.inspired), True)
            self.inspired = 0
            self.is_combat_inspired = False

    def check_great_weapon_fighting(self, Dmg, is_ranged, other_dmg, is_spell):
        rules = [self.knows_great_weapon_fighting,
                self.offhand_dmg == 0,  #no offhand
                is_ranged == False,     #no range
                is_spell == False]   #no spells or stuff
        if all(rules):
            self.DM.say(self.name + ' uses great weapon fighting', True)
            Dmg.multiply(1.15) #no 1,2 in dmg roll, better dmg on attack

    def pre_hit_modifier(self, target, Dmg, d20, advantage_disadvantage, is_crit, is_spell, is_ranged, is_offhand):
        #Does the target AI wants to use Reaction to cast shield? 
        if target.state == 1: #is still alive?
            if target.reaction == 1 and 'Shield' in target.SpellBook:
                target.AI.want_to_cast_shield(self, Dmg)  #call the target AI for shield

        Modifier = 0 # Will go add to the attack to hit
        ACBonus = 0
        AdditionalDmg = 0 #This is damage that will not be multiplied

        if self.knows_great_weapon_master:
            rules = [is_spell == False, #No spells or other stuff
                        is_ranged == False, is_offhand == False]
            if all(rules): #No spells or range attacks
                #Do you want to use great_weapon_master
                if self.AI.want_to_use_great_weapon_master(target, advantage_disadvantage):
                    Modifier -=5  #-5 to attack but +10 to dmg
                    AdditionalDmg += 10
                    self.DM.say('great weapon master, ')
                
                if is_crit and self.bonus_action == 1: 
                    #Just made a crit meele attack, take BA for another attack
                    self.DM.say('extra attack through crit, ')
                    self.bonus_action = 0
                    self.attack_counter += 1
                
                #Inititate Token
                #This Token resolves at end of turn
                #If target gets unconcious in this turn, the Token triggers and gives another attack to player
                GreatWeaponToken(self.TM, GreatWeaponAttackToken(target.TM, subtype='gwa'))

        if target.is_combat_inspired and target.inspired > 0:
            if d20 + self.tohit > target.AC:
                self.DM.say('combat inspired AC (' + str(target.inspired) + '), ')
                ACBonus += target.inspired
                target.inspired = 0
                target.is_combat_inspired = False

        #Gives Bard Chance to protect himself with cutting Words
        if target.knows_cutting_words and target.inspiration_counter > 0:
            if d20 + self.tohit > target.AC:
                self.DM.say(target.name + ' uses cutting word, ')
                Modifier += -target.inspiration_die
                target.inspiration_counter -= 1 #One Use
                target.reaction = 0 #uses reaction
        
        if self.knows_archery and is_ranged and is_spell == False:
            self.DM.say(self.name + ' uses Archery, ')
            Modifier += 2 #Archery

        return Modifier, ACBonus, AdditionalDmg

    def attack(self, target, is_ranged, other_dmg = False, damage_type = False, tohit = False, is_opportunity_attack = False, is_offhand = False, is_spell = False):
    #this is the attack funktion of a player attacking a target with a normak attack
    #if another type of dmg is passed, it will be used, otherwise the player.damage_type is used
    #if no dmg is passed, the normal entitiy dmg is used
    #is_ranged tells the function if it is a meely or ranged attack
        #this ensures that for a normal attack the dmg type of the entity is used
        if damage_type == False: damage_type = self.damage_type
        #if no other dmg is passed, use that of the player
        if other_dmg == False: Dmg = dmg(self.dmg, damage_type)
        else: Dmg = dmg(other_dmg, damage_type)

        #check if other to hit is passsed, like for a spell
        if tohit == False: tohit = self.tohit
        target.TM.isAttacked(self, is_ranged, is_spell)     #Triggers All Tokens, that trigger if target is attacked
        if self.state != 1: return 0   #maybe already dead because of attack of opp or token

        self.DM.say(self.name + " -> " + target.name + ', ', True)

        if is_ranged: self.DM.say('ranged, ')
        else: self.DM.say('melee, ')
        if is_offhand: self.DM.say('off hand, ')

        #Advantage still important for sneak attack
        d20, advantage_disadvantage = self.make_attack_roll(target, is_ranged, is_opportunity_attack)
                
        if d20 == 20 or (self.knows_improved_critical and d20 == 19):
            is_crit = True
        else:
            is_crit = False

        Modifier, ACBonus, AdditionalDmg  = self.pre_hit_modifier(target, Dmg, d20, advantage_disadvantage, is_crit, is_spell, is_ranged, is_offhand)

    #-----------------Hit---------------
        if d20 + tohit + Modifier >= target.AC + ACBonus or is_crit:       #Does it hit
            if is_crit:
                self.DM.say('Critical Hit!, ')
            text = ''.join(['hit: ',str(d20),'+',str(tohit),'+',str(Modifier),'/',str(target.AC),'+',str(ACBonus)])
            self.DM.say(text)

        #Smite
            self.check_smite(target, Dmg, is_ranged, is_spell)
        #Snackattack
            self.check_sneak_attack(Dmg, advantage_disadvantage, is_spell)
        #Combat Inspiration 
            self.check_combat_inspiration(Dmg, is_spell)
        #GreatWeaponFighting
            self.check_great_weapon_fighting(Dmg, is_ranged, other_dmg, is_spell)
        #Favored Foe
            if self.knows_favored_foe:
                if self.AI.want_to_use_favored_foe(target) and self.favored_foe_counter > 0 and self.is_concentrating == False:
                    self.use_favored_foe(target)
        #Stunning Strike
            if self.knows_stunning_strike and is_ranged == False:
                if self.ki_points > 0:
                    if target.is_stunned == False: #don't double stunn
                        self.use_stunning_strike(target)
        #Tokens
            target.TM.washitWithAttack(self, Dmg, is_ranged, is_spell) #trigger was hit Tokens
            self.TM.hasHitWithAttack(target, Dmg, is_ranged, is_spell) #trigger was hit Tokens

        #poison Bite
            if self.knows_poison_bite and self.poison_bites == 1 and is_spell == False and is_offhand == False:
                self.poison_bites = 0 #only once per turn
                poisonDMG = self.poison_bite_dmg
                poisonDC = self.poison_bite_dc
                self.DM.say(self.name + ' uses poison bite, ', True)
                if target.make_save(2, DC = poisonDC) >= poisonDC: #Con save
                    poisonDMG = poisonDMG/2
                Dmg.add(poisonDMG, 'poison')
        #Critical
            if is_crit: Dmg.multiply(1.8)
        #Additional damage
            if AdditionalDmg != 0: Dmg.add(AdditionalDmg, self.damage_type)
        #add rage dmg
            if self.raged == True and is_ranged == False: #Rage dmg only on melee
                Dmg.add(self.rage_dmg, self.damage_type)
        #Interception
            if target.interception_amount > 0:
                self.DM.say(' Attack was intercepted: -' + str(target.interception_amount))
                Dmg.substract(target.interception_amount)
                target.interception_amount = 0 #only once
        #Deflect Missile
            if target.knows_deflect_missiles and is_ranged:
                if target.reaction == 1:
                    #ask AI if player wants to reduce dmg with reaction
                    #and if so, if it also wants to return attack if possible
                    wants_to_reduce_dmg, wants_to_return_attack = target.AI.want_to_use_deflect_missiles(self, Dmg)
                    if wants_to_reduce_dmg:
                        target.use_deflect_missiles(self, Dmg, wants_to_return_attack)

        else:
            Dmg = dmg(amount=0)   #0 dmg
            self.DM.say(''.join(['miss: ',str(d20),'+',str(tohit),'+',str(Modifier),'/',str(target.AC),'+',str(ACBonus)]))
        target.changeCHP(Dmg, self, is_ranged)  #actually change HP
        target.last_attacker = self
        if self.knows_wolf_totem:
            target.has_wolf_mark = True #marked with wolf totem
        return Dmg.abs_amount()

#-------------------Shape Changing, Wild Shape--------------
    def assume_new_shape(self, ShapeName, ShapeDict, Remark = ''):
        #Takes a dict as input for the shape properties
        #Shape Properties
        self.is_shape_changed = True
        self.name = self.orignial_name + '(' + ShapeName + ')'
        self.shape_name = ShapeName
        self.shape_remark = Remark
        self.AC = ShapeDict['AC']
        self.shape_AC = ShapeDict['AC']
        self.shape_HP = ShapeDict['HP']
        self.tohit = ShapeDict['To_Hit']
        self.type = ShapeDict['Type']

        #number auf Attacks
        self.attacks = ShapeDict['Attacks']
        self.attack_counter = self.attacks
        self.dmg = ShapeDict['DMG']

        #new Stats/Modifier
        ShapeStatList = [
            ShapeDict['Str'],
            ShapeDict['Dex'],
            ShapeDict['Con'],
            ShapeDict['Int'],
            ShapeDict['Wis'],
            ShapeDict['Cha']
        ]
        ShapeModList = [round((self.stats_list[i] -10)/2 -0.1, 0) for i in range(0,6)]  #calculate the shape mod
        self.stats_list = ShapeStatList
        self.modifier = ShapeModList

        #new dmg types
        self.damage_type = ShapeDict['Damage_Type']
        self.damage_resistances = ShapeDict['Damage_Resistance']
        self.damage_immunity = ShapeDict['Damage_Immunity']
        self.damage_vulnerability = ShapeDict['Damage_Vulnerabilities']

    def drop_shape(self):
        #If Shape Changed, reset all the changed attributes back to base
        if self.is_shape_changed:
            self.name = self.orignial_name
            self.shape_remark = ''
            self.shape_AC = self.base_AC  #set the shape AC of Entity back to base AC (for more see __init__)
            self.AC = self.shape_AC #set current AC back
            self.shape_HP = 0
            self.tohit = self.base_tohit
            self.attacks = self.base_attacks
            self.attack_counter = 0 #is set to zero, so no attacks can occure in new form, until start of new turn, where they will be reset
            self.dmg = self.base_dmg
            self.type = self.base_type
            
            self.modifier = self.base_modifier
            self.stats_list = self.base_stats_list

            self.damage_immunity = self.base_damage_immunity
            self.damage_resistances = self.base_damage_resistamces
            self.damage_vulnerability = self.base_damage_vulnerability
            self.damage_type = self.base_damage_type

            self.is_shape_changed = False  #no longer shape changed
            self.is_in_wild_shape = False  #definately no longer in wild shape
            self.shape_name = ''            
            self.TM.hasDroppedShape() #some Tokens trigger here, like polymorph

    def wild_shape(self, ShapeIndex):
        #ShapeIndex is Index in BeastFroms from entity __init__
        #Wild shape needs an action or a bonus action if you know combat_wild_shape
        rules = [
            self.knows_wild_shape,
            self.wild_shape_uses > 0,
            self.is_shape_changed == False,
            self.DruidCR >= self.BeastForms[ShapeIndex]['Level']
        ]
        errors = [
                self.name + ' tried to go into wild shape without knowing how',
                self.name + ' cant go into wild shape anymore',
                self.name + ' cant go into wild shape while chape changed',
                self.name + ' tried to go into a too high CR shape: ' + str(self.BeastForms[ShapeIndex]['Level'])
        ]
        ifstatements(rules, errors, self.DM)

        if self.bonus_action == 1 and self.knows_combat_wild_shape:
            self.bonus_action = 0
        elif self.action == 1:
            self.action = 0
        else:
            print('no action left for wildshape')
            quit()

        #A Shape form is choosen and then initiated as entity to use their stats
        ShapeName = self.BeastForms[ShapeIndex]['Name']
        NewShape = entity(ShapeName, self.team, self.DM, archive=True)
        #Use Stats to create dict for shape change function
        ShapeDict = {
            'AC' : NewShape.AC, 
            'HP' : NewShape.HP,
            'To_Hit' : NewShape.tohit,
            'Type' : NewShape.type,
            'Attacks' : NewShape.attacks,
            'DMG' : NewShape.dmg,
            'Str' : NewShape.Str,
            'Dex' : NewShape.Dex,
            'Con' : NewShape.Con,
            'Int' : NewShape.Int,
            'Wis' : NewShape.Wis,
            'Cha' : NewShape.Cha,
            'Damage_Type' : NewShape.damage_type,
            'Damage_Resistance' : NewShape.damage_resistances, 
            'Damage_Immunity' : NewShape.damage_immunity,
            'Damage_Vulnerabilities' : NewShape.damage_vulnerability
        }
        self.assume_new_shape(ShapeName, ShapeDict, Remark= 'wild')

        self.is_in_wild_shape = True
        self.DM.say(self.name + ' goes into wild shape ' + ShapeName, True)
        self.wild_shape_uses -= 1

    def wild_reshape(self):
        if self.bonus_action == 1 and self.is_in_wild_shape:
            self.bonus_action = 0
            self.drop_shape() #resets all shape prop. to base
            self.DM.say(self.name + ' drops wild shape', True)
        else:
            if self.is_in_wild_shape == False:
                print(self.name + ' tried to drop wild shape, but is not in wild shape')
                quit()
            else:
                print(self.name + ' tried to drop wild shape, but has no bonus action left')
                quit()

    def use_combat_wild_shape_heal(self, spell_level=1):
        rules = [self.knows_combat_wild_shape,
                self.is_in_wild_shape,
                self.spell_slot_counter[spell_level -1] > 0,
                self.bonus_action == 1]
        errors = [self.name + ' tried to heal by combat wild shape but does not know how',
                self.name + ' tried to heal by combat wild shape but is not in wild shape',
                self.name + ' tried to heal by combat wild shape but has no bonus action left',
                self.name + ' tried to heal by combat wild shape with a ' + str(spell_level) + 'lv spell slot but has non left']
        ifstatements(rules, errors, self.DM).check()

        heal = spell_level*4.5
        self.changeCHP(dmg(-heal, 'heal'), self, was_ranged=False)
        #HEal is currently always applied to CHP not Shape HP 
        self.spell_slot_counter[spell_level -1] -= 1
        self.bonus_action -= 1

#------------------Special Abilities-----------------
    def rackless_attack(self):
        if self.knows_reckless_attack:
            self.reckless = 1
            self.DM.say(self.name + ' uses reckless Attack', True)
        else:
            print(self.name + ' tried to reckless Attack without knowing it')
            quit()

    def rage(self):
        #rage dmg is added in attack function
        if self.bonus_action == 1 and self.knows_rage:
            self.bonus_action = 0
            self.raged = 1
            self.update_additional_resistances()
            rage_text = self.name + ' falls into a'
            if self.knows_bear_totem:
                rage_text += ' bear totem'
            if self.knows_eagle_totem:
                rage_text += ' eagle totem'
            if self.knows_frenzy:
                self.is_in_frenzy = True
                rage_text += ' franzy'
            self.DM.say(rage_text + ' rage', True)
        else:
            if self.bonus_action == 0:
                print(self.name + ' tried to rage, but has no bonus action')
                quit()
            elif self.knows_rage == False:
                print(self.name + ' tried to rage but cant')
                quit()

    def use_frenzy_attack(self):
        if self.is_in_frenzy and self.bonus_action == 1:
            self.DM.say(self.name + ' uses the bonus action for a frenzy attack', True)
            self.attack_counter += 1  #additional attack
            self.bonus_action = 0
        elif self.bonus_action == 0:
            print(self.name + ' tried to use frenzy attack without a bonus action')
            quit()
        elif self.is_in_frenzy == False:
            print(self.name + ' tried to use franzy attack but is not in a frenzy rage')
            quit()

    def end_rage(self):
        if self.raged == 1:
            self.raged = 0
            self.update_additional_resistances()
            self.is_in_frenzy = False
            self.DM.say(self.name + ' falls out of rage, ')

    def inspire(self, target):
        if self.bonus_action == 0:  #needs a bonus action
            print(self.name + ' tried to use bardic inspiration but has no bonus action left')
            quit()
        else:
            if self.inspiration_counter > 0:
                self.bonus_action = 0
                target.inspired = self.inspiration_die
                #Combat Inspiration
                CombatInspirationText = ''
                if self.knows_combat_inspiration:
                    target.is_combat_inspired = True 
                    CombatInspirationText = ' combat'

                self.inspiration_counter -= 1
                self.DM.say(''.join([self.name,CombatInspirationText,' inspired ',str(target.name),' with awesomeness']), True)
            else:
                print(self.name + ' tried to use bardic inspiration but has none left')
                quit()

    def use_lay_on_hands(self, target, heal):
        if self.action == 0:
            print(self.name + ' tried to lay on hands, but has no action left')
            quit()
        elif heal <= 0:
            print('Lay on Hands was called with a negative heal')
            quit()
        elif self.lay_on_hands_counter <= 0:
            print(self.name + ' tried to lay on hands, but has no points left')
            quit()
        else:
            if self.lay_on_hands_counter > heal:
                self.lay_on_hands_counter -= heal
            elif self.lay_on_hands_counter > 0:
                heal = self.lay_on_hands_counter
                self.lay_on_hands_counter = 0
            self.action = 0
            self.DM.say(self.name + ' uses lay on hands', True)
            target.changeCHP(dmg(-1*heal, 'heal'), self, False)

    def use_empowered_spell(self):
        rules = [self.knows_empowered_spell, self.sorcery_points > 0, self.empowered_spell==False]
        errors= [
            self.name + ' tried to use Empowered Spell without knowing it',
            self.name + ' tried to use empowered Spell, but has no Sorcery Points left',
            self.name + ' tried to use empowered spell, but has already used it']
        ifstatements(rules, errors, self.DM).check()

        self.sorcery_points -= 1
        self.empowered_spell = True
        self.DM.say(self.name + ' used Empowered Spell', True)

    def use_action_surge(self):
        rules = [self.knows_action_surge,
            self.action_surge_counter > 0,
            self.action_surge_used == False]
        errors = [
            self.name + ' tried to use action surge, but does not know how',
            self.name + ' tried to use action surge, but has no charges left',
            self.name + ' tried to use action surge, but already used it']
        ifstatements(rules, errors, self.DM).check()

        self.action_surge_counter -= 1
        self.action_surge_used = True
        self.action_surge()      #This resets the action, cast and attacks
        self.DM.say(self.name + ' used action surge', True)

    def use_aura_of_protection(self, allies):
        #passiv ability, restes at start of Turn or if unconscious
        if self.knows_aura_of_protection:
            if len(allies) > 5: #at least 5 allies
                targetnumber = int(random() + 2.2) #2-3 plus self
            elif len(allies) > 2:  #at least 2 allies and self
                targetnumber = int(random() + 0.8)  #0-1
            else:
                targetnumber = 0 #only self
            if self.level >= 18: targetnumber += 1 #30ft at lv 18

            #Now choose random targtes plus self
            targets = []
            targets.append(self)
            AllyChoice = [ally for ally in allies if ally != self]
            shuffle(AllyChoice)
            for i in range(0,targetnumber):
                if i >= len(AllyChoice): break #no allies left
                targets.append(AllyChoice[i])
            targets.append(self) #always in aura

            #Now apply Bonus
            links = []
            auraBonus = self.modifier[5] #wis mod 
            for ally in targets:
                links.append(ProtectionAuraToken(ally.TM, auraBonus)) #a link for every Ally
            EmittingProtectionAuraToken(self.TM, links)
        else: return

    def protection_aura(self):
        #Returns the current Bonus of all Auras of Protection 
        AuraBonus = 0
        if self.TM.checkFor('aop') == True: #Check if you have a aura of protection Token
            for x in self.TM.TokenList:
                if x.subtype == 'aop':
                    if x.auraBonus > AuraBonus: # mag. effects dont stack, take stronger effect
                        AuraBonus += x.auraBonus #take the Aura Bonus from Token
        return AuraBonus

    def use_second_wind(self):
        rules = [self.bonus_action==1, self.knows_second_wind, self.has_used_second_wind == False]
        errors = [self.name + ' tried to use second wind without a BA',
            self.name + ' tried to use second wind without knowing it',
            self.name + ' tried to use second wind, but has used it already']
        ifstatements(rules, errors, self.DM).check()

        heal = 5.5 + self.level
        self.DM.say(self.name + ' used second wind', True)
        self.changeCHP(dmg(-heal,'heal'), self, was_ranged=False)
        self.bonus_action = 0
        self.has_used_second_wind = True #until end of fight

    def use_turn_undead(self, targets):
        rules = [self.knows_turn_undead,
                self.action > 0,
                self.channel_divinity_counter > 0]
        errors = [self.name + ' tried to use turn undead, but ' + 'does not know how',
                self.name + ' tried to use turn undead, but ' + 'has no action left',
                self.name + ' tried to use turn undead, but ' + 'has no channel divinity left']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.name + ' uses turn undead:', True)
        for target in targets:
            if target.type == 'undead':
                if target.make_save(4, DC = self.spell_dc) < self.spell_dc:
                    #Destroy undead
                    if target.level <= self.destroy_undead_CR:
                        self.DM.say(target.name + ' is destroyed', True)
                        target.death()
                    else:
                        target.is_a_turned_undead = True
                        self.DM.say(target.name + ' is turned', True)
            else:
                continue
        self.action = 0
        self.channel_divinity_counter -= 1 #used a channel divinity

    def use_start_of_turn_heal(self):
        if self.start_of_turn_heal <= 0:
            print(self.name + ' tried to use start of turn heal without having it')
            quit()
        elif self.state != 1:
            return  #not consious
        else:
            self.DM.say(self.name + ' uses regeneration', True)
            heal = dmg(-self.start_of_turn_heal, type='heal')
            self.changeCHP(heal, self, was_ranged=False)

    def summon_primal_companion(self, fight):
        rules = [
            self.knows_primal_companion, #has the Ability
            self.used_primal_companion == False #has not used this fight
        ]
        errors = [
            self.name + ' tried to summon primal companion but has none',
            self.name + ' tried to summon primal companion but used it before'
        ]
        ifstatements(rules, errors, self.DM).check()
        companion = self.summon_entity('Primal Companion', archive=True)
        companion.name = ''.join([self.name, 's Companion'])
        companion.team = self.team  #your team
        #AC
        companion.AC = 13 + self.proficiency
        companion.shape_AC = companion.AC
        companion.base_AC = companion.AC
        #Stats
        companion.HP = 5 + 5*self.level
        companion.CHP = companion.HP
        companion.proficiency = self.proficiency
        #Attack
        companion.tohit = self.spell_mod + self.proficiency
        companion.base_tohit = companion.tohit
        companion.dmg = 6.5 + self.proficiency
        companion.base_dmg = companion.dmg
        if self.knows_beastial_fury:  #double attacks Beast
            companion.base_attacks = 2
            companion.attacks = companion.base_attacks
            companion.attack_counter = companion.base_attacks
        #actions
        companion.AI.Choices = [companion.AI.dodgeChoice]  #It can only act if player uses BA, or dodge
        companion.summoner = self  #the player is this companions summoner

        fight.append(companion) #Add companion to the fight
        self.primal_companion = companion

        if self.AI.primalCompanionChoice not in self.AI.Choices:
            self.AI.Choices.append(self.AI.primalCompanionChoice) #activate this choice, to attaack with companion 
        PrimalBeastMasterToken(self.TM, PrimalCompanionToken(companion.TM, subtype='prc')) #The Token will resolve if one of them dies
        self.DM.say(self.name + ' summons its primal companion', True)
        self.used_primal_companion = True #used it once 

    def use_favored_foe(self, target):
        rules = [
            self.knows_favored_foe, #has the Ability
            self.favored_foe_counter > 0, #has counter left
            self.is_concentrating == False 
        ]
        errors = [
            self.name + ' tried to use fav foe without knowing it',
            self.name + ' tried to use fav foe without uses left',
            self.name + ' tried to use fav foe while concentrating'
        ]
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(''.join([self.name, ' marked ', target.name, ' as favored foe']), True)
        FavFoeToken(self.TM, FavFoeMarkToken(target.TM, subtype='fm')) #mark target as fav foe
        self.favored_foe_counter -= 1

    def use_deflect_missiles(self, target, Dmg, wants_to_return_attack):
        #Check if this is allowed
        rules = [
            self.knows_deflect_missiles,
            self.reaction == 1
        ]
        errors = [
            self.name + ' tried to use deflect missiles without knowing it',
            self.name + ' tried to use deflect missiles but already used their reaction'
        ]
        ifstatements(rules, errors, self.DM).check()

        #Reduce dmg
        self.DM.say(''.join([self.name, ' deflected ', target.name, '\'s ranged attack']), True)
        self.reaction = 0
        Dmg.substract(5 + self.modifier[1] + self.ki_points_base) #this will reduce the dmg later when dmg is calculated and changed in changeCHP
        #Wants to return Attack?
        if wants_to_return_attack:
            if Dmg.abs_amount() < 1 and self.ki_points > 0: #You can return attack
                self.DM.say(''.join([self.name, ' catches and redirects ', target.name, '\'s missile back at them!']), True)
                self.ki_points -= 1
                self.attack(target, is_ranged=True) #Make an ranged attack

    def use_stunning_strike(self, target):
        rules = [
            self.knows_stunning_strike,
            self.ki_points >= 1
        ]
        errors = [
            self.name + ' tried to use stunning strike without knowing it.',
            self.name + ' tried to use stunning strike but is out of ki points.'
        ]
        ifstatements(rules, errors, self.DM).check()
        self.DM.say(''.join([self.name, ' used stunning strike, ', target.name]), True)
        self.ki_points -= 1
        if target.make_save(2, DC = self.ki_save_dc) < self.ki_save_dc:
            LinkToken = StunningStrikedToken(target.TM)
            StunningStrikeActive(self.TM, [LinkToken])
            self.DM.say(''.join([target.name, ' failed their saving throw and is stunned.']), True)
        else:
            self.DM.say(''.join([target.name, ' passed their saving throw and avoided being stunned.']), True)

#---------------Spells---------------
    def check_for_armor_of_agathys(self):
        #This function is called if a player is attacked and damaged in changeCHP
        #If the player has THP left, if calles this function to check if it has armor of agathys
        #If true, this functions return the dmg to the attacker
        AgathysDmg = dmg()
        if self.THP > 0:
            if self.has_armor_of_agathys:
                AgathysDmg.add(self.agathys_dmg, 'cold')
        return AgathysDmg #is 0 if nothig added

    def summon_entity(self, Name, archive=True):
        #This is to initialize a entity
        #For spells like conjure animals
        summon = entity(Name, self.team, self.DM, archive=True)
        return summon

#---------------Round Handling------------
    def start_of_turn(self):
        #Attention, is called in the do the fighting function
        #ONLY called if player state = 1
        self.reckless = 0
        self.stepcounter=0 
        self.attack_counter = self.attacks #must be on start of turn, as in the round an attack of opportunity could have happened, also maybe shape was dropped
        self.AC = self.shape_AC  #reset AC to the AC of the shape (maybe wild shape)
        self.TM.startOfTurn() 

        if self.knows_dragons_breath: #charge Dragons Breath
            if random() > 2/3:
                self.dragons_breath_is_charged = True

        if self.knows_recharge_aoe: #Charge aoe
            if random() < self.aoe_recharge_propability:
                self.recharge_aoe_is_charged = True

        if self.knows_spider_web: #charge Spider Web
            if random() > 2/3:
                self.spider_web_is_charged = True

        if self.is_hasted:#additional Hast attack
            self.attack_counter += 1
            self.AC += 2

        if self.is_a_turned_undead:
            #they can also use dodge, so maybe implement 50/50
            self.action = 0
            self.attack_counter = 0
            self.bonus_action = 0
            self.reaction = 0

        if self.is_incapacitated:
            self.action = 0
            self.attack_counter = 0
            self.bonus_action = 0
            self.reaction = 0
        
        if self.start_of_turn_heal != 0:
            self.use_start_of_turn_heal()

    def action_surge(self):
        self.attack_counter = self.attacks #You can do your attacks again
        self.action = 1      #You get one additional action
        self.has_cast_left = True        #You can cast again in your new action

    def end_of_turn(self):    #resets all round counters
        self.bonus_action = 1
        self.reaction = 1
        if self.is_a_turned_undead or self.is_stunned:
            self.reaction = 0
        self.action = 1
        self.has_cast_left = True
        self.poison_bites = 1
        self.sneak_attack_counter = 1
        self.no_attack_of_opportunity_yet = True
        self.action_surge_used = False
        self.is_attacking = False
        self.has_wolf_mark = False #reset totem of wolf mark

        self.TM.endOfTurn() #Resolve and Count all Tokens

        #If you have not dashed this round, you should not have a dash target anymore
        if self.has_dashed_this_round == False:
            self.dash_target = False
        self.has_dashed_this_round = False #reset for next round

        if self.raged == True:
            self.rage_round_counter += 1 #another round of rage
            if self.rage_round_counter >= 10:
                self.end_rage()
        
        if self.has_spiritual_weapon:
            self.SpiritualWeaponCounter += 1
            if self.SpiritualWeaponCounter >= 10:
                self.break_spiritual_weapon()
                
        if self.is_a_turned_undead:
            self.turned_undead_round_counter += 1
            if self.turned_undead_round_counter >= 10:
                self.end_turned_undead()

        if self.interception_amount != 0:
            self.interception_amount = 0 #no longer in interception
        
        self.chill_touched = False

    def long_rest(self):       #resets everything to initial values
        self.name = self.orignial_name
        self.AC = self.base_AC
        self.shape_AC = self.base_AC
        self.dmg = self.base_dmg
        self.tohit = self.base_tohit
        self.attacks = self.base_attacks
        self.type = self.base_type
        self.damage_type = self.base_damage_type

        for i in range(0, len(self.spell_slots)):
            self.spell_slot_counter[i] = self.spell_slots[i]

        self.break_concentration()
        self.TM.resolveAll()

        self.wailsfromthegrave_counter = self.proficiency
        self.sneak_attack_counter = 1
        self.reckless = 0
        self.raged = 0
        self.rage_round_counter = 0
        self.lay_on_hands_counter = self.lay_on_hands
        self.sorcery_points = self.sorcery_points_base
        self.ki_points = self.ki_points_base
        self.action_surge_counter = self.action_surges
        self.action_surge_used = False
        self.has_used_second_wind = False
        self.has_additional_great_weapon_attack = False
        self.used_primal_companion = False
        self.primal_companion = False
        self.favored_foe_counter = self.proficiency
        self.has_favored_foe = False

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False
        self.recharge_aoe_is_charged = False
        self.poison_bites = 1 #restore Poison bite 
        self.legendary_resistances_counter = self.legendary_resistances #regain leg. res.

        self.drop_shape()
        self.is_shape_changed = False
        self.is_in_wild_shape = False
        self.wild_shape_uses = 2
        self.inspired = 0
        self.is_combat_inspired = False
        if self.knows_inspiration:
            self.inspiration_counter = self.base_inspirations
        else:
            self.inspiration_counter = 0

        self.state = 1
        self.death_counter = 0
        self.heal_counter = 0
        self.CHP = self.HP
        self.THP = 0
        self.initiative = 0
        self.attack_counter = self.attacks
        self.position = self.base_position #Go back 
        self.is_attacking = False


        self.modifier = self.base_modifier

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.has_cast_left = True
        self.is_concentrating = False

        self.restrained = False             #will be ckeckt wenn attack/ed 
        self.prone = 0
        self.is_blinded = False
        self.is_dodged = False
        self.is_stunned = False
        self.is_incapacitated = False
        self.is_paralyzed = False
        self.is_poisoned = False
        self.is_invisible = False


        self.dash_target = False
        self.has_dashed_this_round = False
        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0
        self.unconscious_counter = 0

        #Haste
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        #Hex
        self.can_choose_new_hex = False
        #Hunters Mark
        self.can_choose_new_hunters_mark = False
        #Armor of Agathys
        self.has_armor_of_agathys = False
        self.agathys_dmg = 0
        #Spiritual Weapon
        self.has_spiritual_weapon = False
        self.SpiritualWeaponDmg = 0
        self.SpiritualWeaponCounter = 0
        #Summons
        self.has_summons = False
        #Guiding Bolt
        self.is_guiding_bolted = False
        #TurnUnded
        self.is_a_turned_undead = False
        self.turned_undead_round_counter = 0
        #Interception
        self.interception_amount = 0

        self.empowered_spell = False
        self.quickened_spell = False
    
#-------------Monster Abilities-------------
    def use_dragons_breath(self, targets, DMG_Type = 'fire'):
        #only works if charged at begining of turn
        if self.knows_dragons_breath and self.dragons_breath_is_charged and self.action == 1:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.name + ' is breathing fire', True)
            self.dragons_breath_is_charged = False
            for target in targets:
                DragonBreathDC = 12 + self.modifier[2] + int((self.level - 10)/3)  #Calculate the Dragons Breath DC 
                target.last_attacker = self    #target remembers last attacker
                save = target.make_save(1, DC=DragonBreathDC)           #let them make saves
                Dmg = dmg(20 + int(self.level*3.1), DMG_Type)
                if save >= DragonBreathDC:
                    Dmg.multiply(1/2)
                target.changeCHP(Dmg, self, True)
            self.action = 0
        else: 
            print('Dragon breath could not be used')
            quit()

    def use_recharge_aoe(self, targets):
        #only works if charged at begining of turn
        if self.knows_recharge_aoe and self.recharge_aoe_is_charged and self.action == 1:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.name + ' uses its recharge AOE', True)
            self.recharge_aoe_is_charged = False
            for target in targets:
                target.last_attacker = self    #target remembers last attacker
                save = target.make_save(self.aoe_save_type, DC = self.aoe_recharge_dc)   #let them make saves
                Dmg = dmg(self.aoe_recharge_dmg, self.aoe_recharge_type)
                if save >= self.aoe_recharge_dc:
                    Dmg.multiply(1/2)
                target.changeCHP(Dmg, self, True)
            self.action = 0
        else: 
            print('Recharge AOE could not be used')
            quit()

    def use_spider_web(self, target):
        if self.knows_spider_web and self.spider_web_is_charged and self.action == 1:
            self.DM.say(self.name + ' is shooting web', True)
            self.spider_web_is_charged = False
            target.last_attacker = self #remember last attacker
            SpiderWebDC = 9 + self.modifier[1] #Dex
            #Shoot Web at random Target
            if target.make_save(1, DC = SpiderWebDC) < SpiderWebDC:
                self.DM.say(target.name + ' is caugth in the web and restrained', True)
                SpiderToken = Token(target.TM)
                SpiderToken.subtype = 'r'  #restrain Target, no break condition yet
            self.action = 0
        else: 
            print('Spider Web could not be used')
            quit()
        