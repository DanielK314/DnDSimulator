from datetime import datetime
from random import *
import numpy as np
import json
from functools import partial

class DungeonMaster:
    def __init__(self):
        self.AI_blank = False #just ignore, but MUST be False, see AI Class
        self.printing_on = False
        self.start_time = datetime.now()
        self.Battlefield = np.genfromtxt('Battlefield.txt', delimiter= ',')      #load Informations from Battlefield
        self.enemies_per_100_sqft = self.Battlefield[0][1]
    def block_print(self):
        self.printing_on = False
    def enable_print(self):
        self.printing_on = True

    def say(self, text, end=False):
        if self.printing_on:
            if True:                       #This is a hard coded, disabled developer Function 
                if False:#total diff in ms
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                if False:#diff to last 
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                    self.start_time = datetime.now()
            if end == False:
                print(text)
            else:
                print(text, end = end)

class entity:                                          #A NPC or PC
    def __init__(self, name, team, DM, archive = False):                  #Atk - Attack [+x to Hit, mean dmg]
        if archive == False:
            path = 'Entities/' + str(name) + '.json'
        else:
            path = 'Archive/' + str(name) + '.json'
        file = open(path)
        data = json.load(file)
        file.close()
        self.data = data
        self.DM = DM

    #AI
        self.AI = AI(self)

    #Base Properties
        self.name = str(name)
        self.orignial_name = str(name)        #restore name after zB WildShape
        self.team = team                                      #which Team they fight for
        self.NPC = 0                        #NPCs like Skeletons

        self.AC = int(data['AC'])         #Current AC that will be called, and reset at start of turn
        self.shape_AC =int(data['AC'])     #AC of the current form, changed by wild shape
        self.base_AC = int(data['AC'])      #AC of initial form
        self.HP = int(data['HP'])
        self.proficiency = int(data['Proficiency'])
        self.tohit = int(data['To_Hit'])
        self.base_tohit = int(data['To_Hit'])

        self.base_attacks = int(data['Attacks'])    #attacks of original form                           #number auf Attacks
        self.attacks = self.base_attacks  #at end_of_turn attack_counter reset to self.attack
        self.dmg = float(data['DMG'])           #dmg per attack
        self.base_dmg = float(data['DMG'])
        self.level = int(data['Level'])           #!!!!!!! It is not implementet yet, but level is used in some functions already

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
        self.saves_adv_dis = [0,0,0,0,0,0]  #advantage or disadvantage on saves
        #list for saves of all kind. if = 0, no advantage 
        #if > 0 has advantage
        #if < 0 has disadvantage
        self.HeroVillain = int(data['Hero_or_Villain'])

    #Damage Types,
        self.damage_type = data['Damage_Type']
        self.base_damage_type = self.damage_type
        self.damage_resistances = data['Damage_Resistance']
        self.base_damage_resistamces = self.damage_resistances
        self.damage_immunity = data['Damage_Immunity']
        self.base_damage_immunity = self.damage_immunity
        self.damage_vulnerability = data['Damage_Vulnerabilities']
        self.base_damage_vulnerability = self.damage_vulnerability

        self.last_used_DMG_Type = data['Damage_Type']

    #Spellcasting
        self.spell_mod = int(data['Spell_Mod'])                    #spell modifier
        self.spell_dc = int(data['Spell_DC'])                                #spell save DC


        self.spell_slots = [int(data['Spell_Slot_' + str(i)]) for i in range(1,10)]  #fixed spell slots available ( 0 - Level1, 1 - Level2, ...)
        self.spell_slot_counter = [int(data['Spell_Slot_' + str(i)]) for i in range(1,10)] #current counter for used spell slots 

        self.fire_bolt_cast = 0
        self.entangle_cast = 0
        self.burning_hands_cast = 0
        self.cure_wounds_cast = 0
        self.healing_word_cast = 0
        self.magic_missile_cast = 0
        self.aganazzars_sorcher_cast = 0
        self.scorching_ray_cast = 0
        self.fireball_cast = 0
        self.haste_cast = 0
        self.shield_cast = 0
        self.eldritch_blast_cast = 0

        #Spells known
        self.spell_list = data['Spell_List']

        #If this updates, the All_Spells in the GUI will load this
        #Keep this in Order of the Spell Level, so that it also fits for the GUI
        self.SpellNames = ['FireBolt', 'EldritchBlast', 'Entangle', 'BurningHands', 'CureWounds', 'HealingWord', 'Shield', 'MagicMissile', 'AganazzarsSorcher', 'ScorchingRay', 'Fireball', 'Haste']
        self.SpellBook = {SpellName: spell(self, SpellName) for SpellName in self.SpellNames}


    #Special Abilities
        self.other_abilities = data['Other_Abilities']
        #UncannyDodge
        if 'UncannyDodge' in self.other_abilities:
            self.uncanny_dodge = True
        else:
            self.uncanny_dodge = False
        #Cunning Action
        if 'CunningAction' in self.other_abilities:
            self.knows_cunning_action = True
        else:
            self.knows_cunning_action = False
        #Wails from the Grave
        self.wailsfromthegrave = 0
        self.wailsfromthegrave_counter = self.proficiency
        if 'WailsFromTheGrave' in self.other_abilities:
            self.wailsfromthegrave = 1    #is checked in Attack Function, wails from the grave adds just ot sneak attack at the moment, improvement maybe?
        #Sneak Attack
        self.sneak_attack_dmg = float(data['Sneak_Attack_Dmg'])        #If Sneak_Attack is larger then 0, the Entity has sneak Attack
        self.sneak_attack_counter = 1                  #set 0 after sneak attack     
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
            if self.level < 9:
                self.rage_dmg = 2
            elif self.level < 16:
                self.rage_dmg += 3
            else:
                self.rage_dmg += 4
        self.raged = 0     # 1 if currently raging
        self.rage_round_counter = 0
        #Frenzy
        self.knows_frenzy = False
        if 'Frenzy' in self.other_abilities:
            self.knows_frenzy = True
        self.is_in_frenzy = False

        #Lay On Hands
        self.lay_on_hands = int(data['Lay_on_Hands_Pool'])            #pool of lay on hands pool
        self.lay_on_hands_counter = self.lay_on_hands    #lay on hands pool left
        #Smite
        self.knows_smite = False
        if 'Smite' in self.other_abilities:
            self.knows_smite = True
        #Smites use Spellslots
        self.smite_initiated = [False, False, False, False, False]      #  lv1, lv2, lv3, ... lv5 (0 = no smite, 1 = smite)

        #Inspiration
        self.knows_inspiration=False
        if 'Inspiration' in self.other_abilities:
            self.knows_inspiration = True
        self.inspired = 0   #here the amount a target is inspired
        self.inspiration_counter =  self.modifier[5]    #for baric inspiration char mod

        #Agonizing Blast
        self.knows_agonizing_blast = False
        if 'AgonizingBlast' in self.other_abilities:
            self.knows_agonizing_blast = True

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

    #Monster Abilites
        self.knows_dragons_breath = False
        if 'DragonsBreath' in self.other_abilities:
            self.knows_dragons_breath = True
        self.knows_spider_web = False
        if 'SpiderWeb' in self.other_abilities:
            self.knows_spider_web = True
        

    #Wild Shape
        self.knows_wild_shape = False
        if 'WildShape' in self.other_abilities:
            self.knows_wild_shape = True
        self.knows_combat_wild_shape = False
        if 'CombatWildShape' in self.other_abilities:
            self.knows_combat_wild_shape = True
        self.wild_shape_HP = 0                    #temp HP of wild shape
        self.wild_shape_uses = 2
        self.wild_shape_name = ' '

    #Fight Counter
        self.state = 1                       # 1 - alive, 0 - uncouncious, -1 dead
        self.death_counter = 0
        self.heal_counter = 0
        self.CHP = self.HP                                 #CHP - current HP
        self.initiative = 0
        self.attack_counter = self.attacks           #will be reset to attack at start of turn

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.cast = 1 #if a spell is cast, cast = 0
        self.concentration = 0


        self.restrained = 0             #will be ckeckt wenn attack/ed 
        self.prone = 0
        self.blinded = 0   

        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0

        self.dash_target = False
        self.has_dashed_this_round = False
        self.no_attack_of_opportunity_yet = True

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False

    #Concentration Spells
        #Entangle Variables (in break_concentration handeled)
        self.entangled = 0
        self.entangled_by = self
        self.is_entangling = 0
        self.entangling_target = self
        #Haste
        self.hasted = 0           #haste was cast on him
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        self.hasted_by = self
        self.is_hasting = 0  #This Entity has cast haste on someone
        self.hasting_target = self     #target of haste
 
    def rollD20(self, advantage_disadvantage=0): #-1 is disadvantage +1 is advantage
        if advantage_disadvantage > 0:
            d20_1 = randint(1,20)
            d20_2 = randint(1,20)
            d20 = max([d20_1, d20_2])
        elif advantage_disadvantage < 0:
            d20_1 = randint(1,20)
            d20_2 = randint(1,20)
            d20 = min([d20_1, d20_2])
        else:
            d20 = randint(1,20)
        
        #Inspiration hits here, at the top most layer of this simulation, creazy isnt it 
        if self.inspired != 0:
            d20 += self.inspired
            self.inspired = 0
            self.DM.say(' (with inspiration),', end= '')
        return d20

#---------------------Character State Handling----------------
    def unconscious(self):
        self.DM.say(self.name + ' is unconscious ', end='')
        self.CHP = 0
        self.state = 0   # now unconscious

        #if u get uncounscious:
        self.end_rage()
        self.break_concentration()

        if self.hasted == 1:
            self.break_haste()
        if self.entangled == 1:
            self.break_entangle()
        self.DM.say('\n', end='')
    
    def death(self):
        self.CHP = 0
        self.state = -1
        #if u die:
        self.end_rage()
        self.break_concentration()

        if self.hasted == 1:
            self.break_haste()
        if self.entangled == 1:
            self.break_entangle()

    def changeCHP(self, damage, attacker, damage_type = 'slashing'):
        if damage != 0:
            if damage_type in self.damage_resistances:
                self.DM.say(str(self.name) + ' is resistant against ' + damage_type)
                damage = damage/2

            if damage_type in self.damage_immunity:
                self.DM.say(str(self.name) + ' is immune against ' + damage_type)
                damage = 0

            if damage_type in self.damage_vulnerability:
                self.DM.say(str(self.name) + ' is vulnarable against ' + damage_type)
                damage = damage*2

        if self.uncanny_dodge == True and damage > 0 and self.reaction == 1 and self.state == 1: #uncanny dodge condition
            if self.wild_shape_HP > 0:                         #Wild Shape HP
                self.change_wild_shape_HP(damage/2, attacker)
                self.make_concentration_check(damage/2)
                self.reaction = 0
            else:                                            #no Wild Shape
                self.CHP -= damage/2
                self.make_concentration_check(damage/2)
                self.reaction = 0
                self.DM.say(self.name + ' used Uncanny Dodge, DMG: ' + str(damage/2))

        else:    
            if damage > 0:                 #if damage, it will be checkt if wild shape HP are still there
                if self.wild_shape_HP > 0:
                    self.change_wild_shape_HP(damage, attacker)
                    self.make_concentration_check(damage)
                else:
                    self.CHP -= damage
                    self.make_concentration_check(damage)
                    self.DM.say(self.name + ' takes DMG: ' + str(round(damage,2)) + ' now at: ' + str(round(self.CHP,2)))

            if damage < 0:               #neg. damage is heal
                if self.state == -1:
                    self.DM.say('This is stupid, it should be dead')
                    quit()
                if abs(self.HP - self.CHP) >= abs(damage):
                    self.CHP -= damage    
                else:                     #if more heal then HP, only fill HP up
                    damage = -1*(self.HP - self.CHP)
                    self.CHP -= damage
                self.DM.say(str(self.name) + ' is healed for: ' + str(-damage))

            if damage == 0:
                self.DM.say('Missed')

        if self.state == 0:         #if the player is dying
            if self.CHP > 0:           #if healed over 0
                self.state = 1
                self.death_counter = 0
                self.heal_counter = 0
                self.DM.say(str(self.name) + ' regains conciousness')
            if self.CHP <0:
                if self.CHP < -1*self.HP:
                    self.death()
                    self.DM.say(str(self.name) + ' died due to the damage ')
                else:
                    self.CHP = 0
                    self.death_counter += 1
                    if self.death_counter >= 3:
                        self.death()
                        self.DM.say(str(self.name) + ' was attacked and died')

        if self.state == 1:                    #the following is if the player was alive before
            if self.CHP < 0-self.HP:              #if more then -HP dmg, character dies
                self.death()
                self.DM.say(str(self.name) + ' died due to the damage ')
            if self.CHP <= 0 and self.state != -1:   #if below 0 and not dead, state dying 
                self.unconscious()

        
        if damage > 0:
            attacker.dmg_dealed += damage
            attacker.last_used_DMG_Type = damage_type
        elif damage < 0:
            attacker.heal_given -= damage

    def change_wild_shape_HP(self, damage, attacker):
        if damage < self.wild_shape_HP:     #damage hits the wild shape
            self.wild_shape_HP -= damage
            self.DM.say(str(self.name) + ' takes damage in wild shape: ' + str(round(damage,2)) + ' now: ' + str(round(self.wild_shape_HP,2)))
        else:                  #wild shape breakes, overhang goes to changeCHP
            overhang_damage = abs(self.wild_shape_HP - damage)
            
            #reshape after critical damage
            self.wild_shape_drop()  #function that resets the players stats
            self.DM.say(str(self.name) + ' wild shape breaks')
            self.changeCHP(overhang_damage, attacker)

    def make_check(self, which_check):  #0-Str, 1-Dex, ...
        d20_roll = self.rollD20()
        result = d20_roll + self.modifier[which_check]  #calc modifier
        return result

    def make_save(self, which_save):          #0-Str, 1-Dex, ...
    #how to disadvantage and advantage here !!!
        self.saves_adv_dis = [0,0,0,0,0,0] #calculate all factors to saves:
        self.DM.say(str(self.name) + ' is', end='')
        if self.restrained == 1:  #disadvantage in dex if restrained
            self.saves_adv_dis[1] -= 1
            self.DM.say(' restrained,', end='')
        if self.raged == 1:   #str ad if raged
            self.saves_adv_dis[0] += 1
            self.DM.say(' raging,', end='')
        if self.hasted == 1:
            self.saves_adv_dis[1] += 1
            self.DM.say(' hasted,', end='')

        if self.saves_adv_dis[which_save] < 0:
            d20_roll = self.rollD20(advantage_disadvantage=-1)
            self.DM.say(' in disadvantage doing the save: ' + str(d20_roll), end='')
        elif self.saves_adv_dis[which_save] > 0:
            d20_roll = self.rollD20(advantage_disadvantage=1)
            self.DM.say(' in advantage doing the save: ' + str(d20_roll), end='')
        else:
            d20_roll = self.rollD20(advantage_disadvantage=0)
            self.DM.say(' doing the save: ' + str(d20_roll), end='')
        result = d20_roll + self.modifier[which_save] #calc modifier
        save_text = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        if save_text[which_save] in self.saves_prof:
            #Save Proficiency
            result += self.proficiency
        self.DM.say(' + ' + str(int(result - d20_roll)))
        return result

    def make_death_save(self):
        d20_roll = randint(1,20)
        if d20_roll < 11:
            self.death_counter += 1
            self.DM.say(str(self.name) + ' did not made the death save')
        elif d20_roll > 10 and d20_roll != 20:
            self.heal_counter += 1
            self.DM.say(str(self.name) + ' made the death save')
        if d20_roll == 20:
            self.heal_counter += 2
            self.DM.say(str(self.name) + ' made the death save critical')
        if self.death_counter >= 3:
            self.death()
            self.DM.say(str(self.name) + ' failed death save and died')
        if self.heal_counter >= 3:
            self.state = 1
            self.CHP = 1
            self.heal_counter = 0
            self.death_counter = 0
            self.DM.say(str(self.name) + ' made death save and became conscious')

    def stand_up(self):
        if self.prone == 1:
            if self.restrained == 0:
                self.prone = 0
                self.DM.say(self.name + ' stood up to end prone')
            else:
                self.DM.say(self.name + ' tried to stand up, but is restrained')
        else:
            self.DM.say(self.name + ' tried to stand up but is not prone')
            quit()

#---------------Concentration and Concentration Spells-----------
    def make_concentration_check(self, damage):
        if self.concentration == 1:
            save_res = self.make_save(2)
            if save_res >= damage/2 and save_res >= 10:   #concentration is con save
                return 
            else:
                self.break_concentration()
                return 
        else:
            return

    def break_concentration(self):
        if self.is_entangling == 1 or self.is_hasting == 1:
            self.DM.say(self.name + ' lost concentration: ', end='')
        self.concentration = 0  #no longer concentrated
        #break entangled
        if self.is_entangling == 1:
            self.entangling_target.break_entangle()
        #break Haste
        if self.is_hasting == 1: 
            self.hasting_target.break_haste()

    def break_haste(self):
        if self.hasted == 1:
            self.DM.say(self.name + ' Haste wares of, '+ self.hasted_by.name + ' no longer concentrated', end='')
            #reset the own haste
            self.hasted = 0
            self.haste_round_counter = 0
            #reset the haste of the entity that was casting haste, restore concentration
            self.hasted_by.is_hasting = 0
            self.hasted_by.hasting_target = self.hasted_by
            self.hasted_by.concentration = 0

            self.hasted_by = self

    def get_hasted_by(self, caster):
        self.hasted = 1
        self.hasted_by = caster
        #advantage in Dex saves in make_save function
        #additional Attack in start_of_turn_function
        #AC added in start_of_turn_function

        caster.is_hasting = 1
        caster.hasting_target = self

    def break_entangle(self):
        if self.entangled == 1:
            self.DM.say(self.name + ' Entangle breaks, '+ self.entangled_by.name + ' no longer concentrated', end='')
            #reset the own entangle
            self.entangled = 0
            self.restrained = 0
            #reset the entangle of the entity that was casting entangle, restore concentration
            self.entangled_by.is_entangling = 0
            self.entangled_by.entangling_target = self.entangled_by#
            self.entangled_by.concentration = 0

            self.entangled_by = self

    def try_break_entangle(self):  #makes an effort to break entangle
        if self.entangled == 0:
            self.DM.say(self.name + ' tried to break entangle but is not entangled')
        elif self.action == 0:
            self.DM.say(self.name + ' tried to break entangle but has no action left')
        else: 
            self.DM.say(self.name + ' tries to break entangle: ', end = '')
            result = self.make_check(0)
            self.DM.say('result/' + self.entangled_by.spell_dc)
            if result < self.entangled_by.spell_dc:
                self.action = 0
                return
            else:
                self.action = 0
                self.break_entangle()
                return

#--------------------Position Management----------------------
    def need_dash(self, target, fight, AttackIsRanged = False):
        #0 - need no dash
        #1 - need dash
        #2 - not reachable

        #ABack-25ft-AMid-25ft-AFront-BFront-25ft-BMid-25ft-BBack
    #no Dash for ranged attacks

        #The Distance between lines scales with how close the Battlefield is
        # 0.5 Wide Space
        # 1 normal
        # 2 crowded
        distance = 25*1/self.DM.enemies_per_100_sqft

        EnemiesLeft = self.AI.enemies_left_sort(fight)
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]

        def compare_speed(OpenLines):
            #example: Mid Attacks Mid, no open front: 1 + 1 = 2*25ft = 50ft 
            if self.speed >= (target.position + self.position - OpenLines)*distance: return 0
            elif self.dash_target == target: return 0 #The player has used dash last round to get to this target
            #Only works if you can still dash with action or cunning action
            elif self.action == 1 or (self.knows_cunning_action and self.bonus_action ==1):
                if 2*self.speed >= (target.position + self.position - OpenLines)*distance: return 1
                else: return 2 
            else: return 2

        if AttackIsRanged: return 0 
        if self.has_range_attack: return 0
        if target.position == 3: return 0 #Airborn is in range
        if self.position < 3: #0,1,2 Front, Mid, Back
            if len(EnemiesInFront) == 0 and len(EnemiesInMid) == 0: return compare_speed(2) #open Front and Mid
            elif len(EnemiesInFront) == 0: return compare_speed(1) #open front
            else: return compare_speed(0) #no open line

        if self.position == 3: #airborn
            if target.position < 3: return compare_speed(3) #basically 3 open lines

    def will_provoke_Attack(self, target, fight, AttackIsRanged = False):
        #this function tells if an attack of opportunity will be provoked
        EnemiesLeft = self.AI.enemies_left_sort(fight)
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]

        def compare_positions(OpenLines):
            #if you cross more then 2 lines (like, front - back or mid - mid) you provoke opp. attack
            if self.position == 2:
                OpenLines += 1 #back Player can attack Front with no Opp Attack 
            if self.position + target.position - OpenLines >= 2:
                return True 
            else: return False

        if AttackIsRanged: return False
        if self.has_range_attack: return False
        if self.dash_target == target: return False
        if self.position < 3: #0,1,2 Front, Mid, Back
            if len(EnemiesInFront) == 0 and len(EnemiesInMid) == 0: return False #open Front and Mid
            elif len(EnemiesInFront) == 0: return compare_positions(1) #open front
            else: return compare_positions(0) #no open line

        if self.position == 3: False #no opp. attacks from the air

    def use_disengage(self):
        if self.bonus_action == 1 and self.knows_cunning_action:
            self.DM.say(self.name + ' used cunning action to disengage')
            self.bonus_action = 0
        elif self.action == 1:
            self.DM.say(self.name + ' used an action to disengage')
            self.action = 0
        else:
            self.DM.say(self.name + ' tried to disengage, but has no action left')
            quit()

    def enemies_reachable_sort(self,fight, AttackIsRanged = False):
        #This function is used to determine which Enemies are theoretically in reach to attack for a Player
        #This also includes Players, that are only reachable by dashing or by provoking attacks of Opportunity

        #The following Rules Apply
        #----------1---------
        #Front can always melee attack the other front
        #Front can attack the other mid, if the player speed suffice
        #Front can attack the other back, if player speed suffice and by provoking an opportunity attack
        #If there is no Player in the other Front, the Front can melee attack mid and back
        #If there is no front, the distance to mid and back reduces
        #----------2---------
        #mid can meelee attack front
        #mid can attack mid, if speed suffices, and by provoking an opportunity attack
        #If there is no Player in the other Front, the mid can melee attack mid and back
        #If there is no Player in the other Front and Mid, mid can attack all
        #----------3---------
        #back can attack Front
        #----------4---------
        #airborn can melee attack all, but must land for that
        #if airborn lands, it is then in front
        #Airborn can not be attacked by melee at this point
        #----------5---------
        #If player has reanged attacks, player can attack all regardless

        #Idden: $. Reihe Airborn, only hittable by ranged 
        #At the start of turn, a creature desides to go airborn or land
        EnemiesLeft = self.AI.enemies_left_sort(fight)
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]
                
        EnemiesInReach = []

        for Enemy in EnemiesLeft:
        #This is to manually say the function that the Attack is ranged, even if the player might not have ranged attacks, for Spells for example
            EnemyIsInRange = True
            if AttackIsRanged:
                EnemiesInReach.append(Enemy)
                continue
        #Range, anyone is in reach
            elif self.has_range_attack:
                EnemiesInReach.append(Enemy)
                continue
            elif self.position == 3:
                EnemiesInReach.append(Enemy)
                continue
            elif Enemy == self.dash_target: #last dash target is always in reach
                EnemiesInReach.append(Enemy)
                continue                

        #All other lines front(0), mid(1), back(2)
            DashValue = self.need_dash(Enemy, fight, AttackIsRanged)
            if DashValue == 2: #target is too far away
                continue
            if self.position == 1:
                if Enemy.position == 2 and len(EnemiesInFront) != 0:
                    EnemyIsInRange = False
            if self.position == 2:
                if Enemy.position == 1 and len(EnemiesInFront) != 0:
                    EnemyIsInRange = False
                if Enemy.position == 2 and len(EnemiesInFront) != 0:
                    EnemyIsInRange = False
                if Enemy.position == 2 and len(EnemiesInMid) != 0:
                    EnemyIsInRange = False
            if Enemy.position == 3 and self.position !=3:
                EnemyIsInRange = False
            if self.bonus_action == 0:
                if self.need_dash(Enemy, fight, AttackIsRanged) > 0:
                    EnemyIsInRange = False


            if EnemyIsInRange: EnemiesInReach.append(Enemy)

        return EnemiesInReach

    def use_dash(self, target):
        if self.knows_cunning_action:
            self.DM.say(self.name + ' uses cunning action to dash to ' + target.name)
            self.bonus_action = 0
            self.dash_target = target
            self.has_dashed_this_round = True
        elif self.action == 0:
            self.DM.say(self.name + ' tried to dash, but has no action left')
            quit()
        else:
            self.action = 0
            self.attack_counter = 0
            self.dash_target = target
            self.has_dashed_this_round = True
            self.DM.say(self.name + ' uses dash to get to ' + target.name)

    def move_position(self):
        #This function will be called, if the player hat no target in reach last turn
        if self.position == 1: #if you are usually in mid go front 
            self.DM.say(self.name + ' moves to the front line')
            self.position = 0
            self.action = 0 #took the action

#-------------------Attack Handling----------------------
    def make_normal_attack_on(self, target, fight):
    #This is the function of a player trying to move to a target und making an attack
    #It also checks for Dash and does opportunity attacks if necessary
    
    #first check if target is in range
        if target not in self.enemies_reachable_sort(fight):
            self.DM.say(self.name + ' tried to attack, but ' + target.name + ' is out of reach')
            quit()            
        else:   #target is within reach
            if self.need_dash(target, fight) == 2:
                self.DM.say(self.name + ' tried to attack, but ' + target.name + ' is out of reach, this is weird here, check enemies_rechable_sort')
                quit()
            else:
            #----attack of opportunity and dash
                if self.need_dash(target, fight) == 1:
                    self.use_dash(target)
                    if self.attack_counter == 0:return  #If you used the action to dash, return and end your turn here, if cunning action, then proceed
                if self.will_provoke_Attack(target, fight):
                    if self.no_attack_of_opportunity_yet:#only one per turn
                        #now choose who did the attack of opportunity
                        EnemiesLeft = self.AI.enemies_left_sort(fight)
                        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
                        if len(EnemiesInFront) > 0:
                            OpportunityAttacker = EnemiesInFront[randint(0, len(EnemiesInFront)-1)]
                        else:
                            OpportunityAttacker = EnemiesLeft[randint(0, len(EnemiesLeft)-1)]
                        if self.provoke_opportunit_attack(OpportunityAttacker) == False:
                            #false means that the attack killed the player
                            return #return and end the turn
                
                #The Player is now in range for attack
                self.action = 0 #if at least one attack, action = 0
                self.attack(target)

    def provoke_opportunit_attack(self, target):
        if self.no_attack_of_opportunity_yet: #only one per turn 
            self.DM.say(self.name + ' has provoked an attack of opportunity:')
            self.no_attack_of_opportunity_yet = False
            target.AI.do_opportunity_attack(self)
            if self.state != 1: return False
            else: return True
        else: return True

    def attack(self, target, other_dmg = False, damage_type = False, other_tohit = False):
    #this is the attack funktion of a player attacking a target with a normak attack
    #if another type of dmg is passed, it will be used, otherwise the player.dmg_type is used
    #if no dmg is passed, the normal entitiy dmg is used
        #this ensures that for a normal attack the dmg type of the entity is used
        if damage_type == False:
            damage_type_of_attack = self.damage_type
        #if another damage type is specified, like for a spell use that:
        else:
            damage_type_of_attack = damage_type
        #if no other dmg is passed, use that of the player
        if other_dmg == False:
            dmg = self.dmg
        else:
            dmg = other_dmg
        #check if other to hit is passsed, like for a spell
        if other_tohit == False:
            tohit = self.tohit
        else:
            tohit = other_tohit

        self.DM.say(self.name + " -> " + target.name + ', ', end='')
        #calculate all effects that might influence Disad or Advantage
        advantage_disadvantage = 0
        if target.reckless == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' reckless, ',end='')
        if self.reckless == 1:
            advantage_disadvantage += 1    
            self.DM.say(self.name + ' reckless, ',end='')
        if target.restrained == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' restrained, ',end='')
        if self.restrained == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' restrained, ',end='')
        if target.blinded == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' blinded, ',end='')
        if self.blinded == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' blinded, ',end='')
        if target.prone == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' prone, ',end='')
        if self.prone == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' prone, ',end='')

        #Roll the Die to hit
        if advantage_disadvantage > 0:
            d20 = self.rollD20(advantage_disadvantage=1)
            self.DM.say('with advantage, ', end='')
        elif advantage_disadvantage < 0:
            d20 = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('with disadvantage, ', end='')
        else:
            d20 = self.rollD20(advantage_disadvantage=0)

        #Does the target AI wants to use Reaction to cast shield? 
        if target.reaction == 1 and target.SpellBook['Shield'].is_known:
            target.AI.want_to_cast_shield(self, dmg)  #call the target AI for shield

        if d20 + tohit >= target.AC or d20 == 20:       #Does it hit
            if d20 == 20:
                self.DM.say('Critical Hit!, ',end='')
            self.DM.say(' hit: ' + str(d20 + tohit) + '/' + str(target.AC), end= '')

        #before attack check if a smite is initiated
            smitedmg = 0
            for i in range(0, len(self.smite_initiated)):
                if self.smite_initiated[i]:             #smite initiated?
                    if self.knows_smite:
                        if self.spell_slot_counter[i] > 0:
                            smitedmg += 4.5*(i+1)
                            if d20 ==20:
                                smitedmg = smitedmg*2                       #smite crit
                            self.spell_slot_counter[i] -= 1
                            damage_type_of_attack = 'radiant'
                            self.smite_initiated[i] = 0
                            self.DM.say('\n' + self.name + ' uses ' + str(i + 1) + '. lv Smite', end='')
            
        #calculate the dmg, maybe smite, maybe sneak attack
        #smite might be 0 
            damage_done = dmg + smitedmg
        #add sneak attack dmg
            if self.sneak_attack_dmg > 0 and self.sneak_attack_counter == 1:    #Sneak Attack 
                damage_done += self.sneak_attack_dmg
                if d20 == 20:
                    damage_done += self.sneak_attack_dmg  #double sneak Attack dmg for crit
                self.DM.say('\n' + self.name + " Sneak Attack: +" + str(self.sneak_attack_dmg), end='')
                if self.wailsfromthegrave == 1 and self.wailsfromthegrave_counter > 0:  #if sneak attack hits and wails from the grave is active
                    damage_done += self.sneak_attack_dmg/2
                    self.wailsfromthegrave_counter -= 1
                    self.DM.say(' and ' + str(self.sneak_attack_dmg/2) + ' wails from the grave', end='')
                self.sneak_attack_counter = 0
        #add rage dmg
            if self.raged == True:
                damage_done += self.rage_dmg

        else:
            damage_done = 0
            self.DM.say(str(d20 + tohit) + '/' + str(target.AC) + ' - ', end= '')

        if d20 == 20:                                            #Critical Hit
            damage_done += dmg*0.8

        self.DM.say('\n', end='')
        target.changeCHP(damage_done, self, damage_type_of_attack)  #actually change HP
        self.attack_counter -= 1      #Attack Counter 
        self.reset_all_smites() 
        target.last_attacker = self
        return damage_done

#-------------------Wild Shape---------------
    def wild_shape(self, shape_name):
        #Wild shape needs an action or a bonus action if you know combat_wild_shape
        player_can_wild_shape = False
        if self.wild_shape_uses > 0 and self.wild_shape_HP == 0 and self.knows_wild_shape:
            if self.bonus_action == 1 and self.knows_combat_wild_shape:
                player_can_wild_shape = True
                self.bonus_action = 0
            elif self.action == 1:
                player_can_wild_shape = True
                self.action = 0
        if player_can_wild_shape:
            path = 'WildShapes/' + str(shape_name) + '.json'
            wild_shape_form = json.load(open(path))
        #Wild Shape Properties
            self.name = self.orignial_name + '(' + shape_name + ')'
            self.shape_AC = wild_shape_form['AC']
            self.wild_shape_HP = wild_shape_form['HP']
            self.tohit = wild_shape_form['To_Hit']
            self.attacks = wild_shape_form['Attacks']                               #number auf Attacks
            self.attack_counter = self.attacks
            self.dmg = wild_shape_form['Dmg']
            self.wild_shape_name = shape_name

            #new modifier
            stats_list = [wild_shape_form[stat] for stat in ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']]       #used for temp changes and request
            self.stats_list = stats_list
            self.modifier = [round((stats_list[i] -10)/2 -0.1, 0) for i in range(0,6)]  #calculate the mod


            #new dmg types
            self.damage_type = wild_shape_form['Damage_Type']
            self.damage_resistances = wild_shape_form['Damage_Resistance']
            self.damage_immunity = wild_shape_form['Damage_Immunity']
            self.damage_vulnerability = wild_shape_form['Damage_Vulnerability']

            self.DM.say(self.name + ' goes into wild shape ' + shape_name)
            self.wild_shape_uses -= 1
        else:
            if self.wild_shape_uses < 1:
                self.DM.say(self.name + ' cant go into wild shape anymore')
            elif self.action == 0:
                self.DM.say(self.name + ' cant go into wild shape without an action left')
            elif self.wild_shape_HP != 0:
                self.DM.say(self.name + ' cant go into wild shape while in wildshape')
            elif self.knows_wild_shape == False:
                self.DM.say(self.name + ' tried to go into wild shape without knowing how')
            else:
                self.DM.say('ERROR Wild Shape')

    def wild_shape_drop(self):
        if self.wild_shape_HP != 0:
            self.name = self.orignial_name
            self.shape_AC = self.base_AC  #set the shape AC of Entity back to base AC (for more see __init__)
            self.wild_shape_HP = 0
            self.tohit = self.base_tohit
            self.attacks = self.base_attacks
            self.attack_counter = self.attacks
            self.dmg = self.base_dmg
            
            self.modifier = self.base_modifier
            self.stats_list = self.base_stats_list

            self.damage_immunity = self.base_damage_immunity
            self.damage_resistances = self.base_damage_resistamces
            self.damage_vulnerability = self.base_damage_vulnerability
            self.damage_type = self.base_damage_type

            self.wild_shape_name = ' '

    def wild_reshape(self):
        if self.bonus_action == 1 and self.wild_shape_HP != 0:
            self.bonus_action = 0
            self.wild_shape_drop()
            self.DM.say(self.name + ' drops wild shape')
        else:
            if self.wild_shape_HP == 0:
                self.DM.say(self.name + ' tried to drop wild shape, but is not in wild shape')
            else:
                self.DM.say(self.name + ' tried to drop wild shape, but has no bonus action left')

    def use_combat_wild_shape_heal(self, spell_level=1):
        if self.knows_combat_wild_shape and self.wild_shape_HP > 0 and self.spell_slot_counter[spell_level -1] > 0 and self.bonus_action == 1:
            heal = spell_level*4.5
            self.changeCHP(-heal, self)
            self.spell_slot_counter[spell_level -1] -= 1
            self.bonus_action -= 1
        else:
            if self.knows_combat_wild_shape == False:
                self.DM.say(self.name + ' tried to heal by combat wild shape but does not know how')
            elif self.wild_shape_HP == 0:
                self.DM.say(self.name + ' tried to heal by combat wild shape but is not in wild shape')
            elif self.bonus_action == 0:
                self.DM.say(self.name + ' tried to heal by combat wild shape but has no bonus action left')
            elif self.spell_slot_counter[spell_level -1] == 0:
                self.DM.say(self.name + ' tried to heal by combat wild shape with a ' + str(spell_level) + 'lv spell slot but has non left')

#------------------Special Abilities-----------------
    def rackless_attack(self):
        if self.knows_reckless_attack:
            self.reckless = 1
            self.DM.say(self.name + ' uses reckless Attack')
        else:
            self.DM.say(self.name + ' tried to reckless Attack without knowing it')

    def rage(self):
        #rage dmg is added in attack function
        if self.bonus_action == 1 and self.knows_rage:
            self.bonus_action = 0
            self.raged = 1
            rage_text = self.name + ' falls into a'
            if self.knows_frenzy:
                self.is_in_frenzy = True
                rage_text +=' franzy'
            self.DM.say(rage_text + ' rage')
        else:
            if self.bonus_action == 0:
                self.DM.say(self.name + ' tried to rage, but has no bonus action')
            elif self.knows_rage == False:
                self.DM.say(self.name + ' tried to rage but cant')

    def use_frenzy_attack(self):
        if self.is_in_frenzy and self.bonus_action == 1:
            self.DM.say(self.name + ' uses the bonus action for a frenzy attack')
            self.attack_counter += 1  #additional attack
            self.bonus_action = 0
        elif self.bonus_action == 0:
            self.DM.say(self.name + ' tried to use frenzy attack without a bonus action')
        elif self.is_in_frenzy == False:
            self.DM.say(self.name + ' tried to use franzy attack but is not in a frenzy rage')

    def end_rage(self):
        if self.raged == 1:
            self.raged = 0
            self.is_in_frenzy = False
            self.DM.say(' ' + self.name + ' falls out of rage', end= '')

    def inspire(self, target):
        if self.bonus_action == 0:  #needs a bonus action
            self.DM.say(self.name + ' tried to use bardic inspiration but has no bonus action left')
        else:
            if self.inspiration_counter > 0:
                self.bonus_action = 0
                if self.level < 5:
                    inspiration = 3
                elif self.level < 10:
                    inspiration = 4
                elif self.level < 15:
                    inspiration = 5
                else:
                    inspiration = 6
                target.inspired = inspiration
                self.inspiration_counter -= 1
                self.DM.say(self.name + ' inspired ' + str(target.name) + ' with awesomeness')
            else:
                self.DM.say(self.name + ' tried to use bardic inspiration but has none left')

    def use_lay_on_hands(self, target, heal):
        if self.action == 0:
            self.DM.say(self.name + ' tried to lay on hands, but has no action left')
            return
        else:
            if heal > 0:
                if self.lay_on_hands_counter > heal:
                    self.lay_on_hands_counter -= heal
                    self.DM.say(self.name + ' uses lay on hands')
                    target.changeCHP(-1*heal, self, damage_type = 'heal')
                    self.action = 0
                elif self.lay_on_hands_counter > 0:
                    self.DM.say(self.name + ' uses lay on hands')
                    target.changeCHP(-1*self.lay_on_hands_counter, self, damage_type = 'heal')
                    self.lay_on_hands_counter = 0
                    self.action = 0
                else:
                    self.DM.say(self.name + ' tried to lay on hands, but has no points left')
            else:
                self.DM.say('Lay on Hands was called with a negative heal')

    def initiate_smite(self, smite_level= 1):
        if self.knows_smite and self.spell_slot_counter[smite_level - 1]>0:
            self.smite_initiated[smite_level-1] = True
        elif self.knows_smite == False:
            self.DM.say(self.name + ' tried to initiate smite without knowing it')
        else:
            self.DM.say(self.name + ' tried to initiate smite without spellslots')

    def reset_all_smites(self):
        self.smite_initiated = [False, False, False, False, False]

    def use_empowered_spell(self):
        if self.knows_empowered_spell:
            if self.sorcery_points < 1:
                self.DM.say(self.name + ' tried to use empowered Spell, but has no Sorcery Points left')
            else:
                if self.empowered_spell:
                    self.DM.say(self.name + ' tried to use empowered spell, but has already used it')
                else:
                    self.sorcery_points -= 1
                    self.empowered_spell = True
                    self.DM.say(self.name + ' used Empowered Spell')
        else:
            self.DM.say(self.name + ' tried to use Empowered Spell without knowing it')

#---------------Round Handling------------
    def start_of_turn(self):
        self.reckless = 0
        self.stepcounter=0 
        self.attack_counter = self.attacks #must be on start of turn, as in the round an attack of opportunity could have happened 
        self.AC = self.shape_AC  #reset AC to the AC of the shape (maybe wild shape)

        if self.knows_dragons_breath: #charge Dragons Breath
            if randint(1,6) > 4:
                self.dragons_breath_is_charged = True
        if self.knows_spider_web: #charge Spider Web
            if randint(1,6) > 4:
                self.spider_web_is_charged = True

        if self.hasted == 1:#additional Hast attack
            self.attack_counter += 1
            self.AC += 2
        print_text = '_____________'
        self.DM.say(print_text)

    def end_of_turn(self):    #resets all round counters
        self.bonus_action = 1
        self.reaction = 1
        self.action = 1
        self.cast = 1
        self.sneak_attack_counter = 1
        self.no_attack_of_opportunity_yet = True

        #If you have not dashed this round, you should not have a dash target anymore
        if self.has_dashed_this_round == False:
            self.dash_target = False
        self.has_dashed_this_round = False #reset for next round

        self.reset_all_smites()

        if self.raged == True:
            self.rage_round_counter += 1 #another round of rage
            if self.rage_round_counter >= 10:
                self.end_rage()

        if self.hasted ==1:        #for haste spell counter
            self.haste_round_counter += 1
            if self.haste_round_counter >= 10:  #if longer then 1min / 10 rounds, haste ends
                self.break_haste()
                self.DM.say(str(self.name) + ' runs out of haste')

    def long_rest(self):       #resets everything to initial values
        self.name = self.orignial_name
        self.AC = self.base_AC
        self.shape_AC = self.base_AC
        self.dmg = self.base_dmg
        self.tohit = self.base_tohit
        self.attacks = self.base_attacks

        self.saves_adv_dis = [0,0,0,0,0,0]  #advantage or disadvantage on saves

        for i in range(0, len(self.spell_slots)):
            self.spell_slot_counter[i] = self.spell_slots[i]

        self.reset_all_smites()

        self.wailsfromthegrave_counter = self.proficiency
        self.sneak_attack_counter = 1
        self.reckless = 0
        self.raged = 0
        self.rage_round_counter = 0
        self.lay_on_hands_counter = self.lay_on_hands
        self.sorcery_points = self.sorcery_points_base

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False

        self.wild_shape_HP = 0
        self.wild_shape_uses = 2
        self.inspired = 0
        if self.knows_inspiration:
            self.inspiration_counter = self.modifier[5]
        else:
            self.inspiration_counter = 0

        self.state = 1
        self.death_counter = 0
        self.heal_counter = 0
        self.CHP = self.HP
        self.initiative = 0
        self.attack_counter = self.attacks
        self.position = self.base_position #Go back 

        self.modifier = self.base_modifier

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.cast = 1 #if a spell is cast, cast = 0
        self.concentration = 0

        self.restrained = 0             #will be ckeckt wenn attack/ed 
        self.prone = 0
        self.blinded = 0   

        self.dash_target = False
        self.has_dashed_this_round = False
        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0

        self.entangled = 0
        self.entangled_by = self
        self.is_entangling = 0
        self.entangling_target = self
        #Haste
        self.hasted = 0           #haste was cast on him
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        self.hasted_by = self
        self.is_hasting = 0  #This Entity has cast haste on someone
        self.hasting_target = self     #target of haste

        self.empowered_spell = False
        self.quickened_spell = False

    def moveto(self,newposition,fight): #newposition input form: [x,y]
        fail=0
        x_size,y_size=(10,10)
        grid=np.zeros([x_size,y_size])
        for x in fight: 
            grid[x.position[0]][x.position[1]]=1
            if x.position==newposition: 
                fail+=1
                self.DM.say(self.name+' tried to move to position of '+x.name)
        if self.stepcounter>self.speed:
            fail+=1
            self.DM.say(self.name+' tried to move but has no steps left')
        if newposition[0]<0 or newposition[1]<0:
            fail+=1
            self.DM.say('negative coordinates, postion not found')
        if self.restrained==1:
            fail+=1
            self.DM.say(self.name+' tried to move but is restrained')
        if fail==0: 
            self.stepcounter+=5
            grid[self.position[0]][self.position[1]]=0 #delete old position from grid
            self.position=newposition
            grid[self.position[0]][self.position[1]]=1 #input new position to grid
            self.DM.say(self.name+' moved to '+ str(newposition))
            self.DM.say(grid)
    
#Monster Abilities
    def use_dragons_breath(self, targets, DMG_Type = 'fire'):
        #only works if charged at begining of turn
        if self.knows_dragons_breath and self.dragons_breath_is_charged and self.action == 1:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.name + ' is breathing fire')
            self.dragons_breath_is_charged = False
            for target in targets:
                target.last_attacker = self    #target remembers last attacker
                save = target.make_save(1)           #let them make saves
                dmg = 20 + int(self.level*3.1)
                DragonBreathDC = 12 + self.Con + int((self.level - 10)/3)  #Calculate the Dragons Breath DC 
                if save >= DragonBreathDC:
                    target.changeCHP(dmg/2, self, DMG_Type)             #save made
                else:
                    target.changeCHP(dmg, self, DMG_Type)
            self.action = 0

    def use_spider_web(self, target):
        if self.knows_spider_web and self.action == 1:
            self.DM.say(self.name + ' is shooting web')
            self.spider_web_is_charged = False
            target.last_attacker = self #remember last attacker
            SpiderWebDC = 9 + self.Dex
            #Shoot Web at random Target
            if target.make_save(1) < SpiderWebDC:
                self.DM.say(target.name + ' is caugth in the web and restrained')
                target.restrained = 1
            self.action = 0
                
class AI:
    def __init__(self, player):
    #this class is initialized in the Entity class to controll all the moves and decisions
        self.player = player
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)

        #this is later filled in so_your_turn()
        self.allies = []
        self.dying_allies = []
        self.enemies_left_list = []

    def do_your_turn(self,fight):
        player = self.player
        self.allies = [x for x in fight if x.team == player.team]       #which allies
        self.dying_allies = [i for i in self.allies if i.state == 0]     #who is dying
        self.enemies_left_list = self.enemies_left_sort(fight)    #what enemies are alive

        #stand up if prone
        if player.prone == 1 and player.restrained == 0:
            player.stand_up()

        #------------Not in WildShape
        if player.wild_shape_HP == 0:
        #---------------Healing First----------
            self.smart_heal(fight)

        #--------Evaluate Choices
            TryCounter = 0
            while (player.action == 1 or player.bonus_action == 1) and player.state == 1:
                self.AttackScore = self.player_attack_score()#The potential dmg of a simple attack
                Choices = []
                #What are the players Choices
                
                #Wildshape
                if player.wild_shape_HP == 0: #is not in wild shape (might have just gone into wildshape)
                    if player.knows_wild_shape and player.wild_shape_uses > 0:
                        if player.action == 1 or (player.bonus_action == 1 and player.knows_combat_wild_shape):
                            Choices.append(self.smart_go_wildshape)
                #Inspiration
                if player.knows_inspiration and player.inspiration_counter > 0 and player.bonus_action == 1:
                    Choices.append(self.smart_inspire)
                #Spellcasting
                #If you can cast spells, choose one.
                #This Spell will then be the choosen spell
                #If no Spell is good, the returned Spell is False
                self.ChoosenSpell = False
                for spell in player.SpellNames: #check if player knows any spells
                    if player.SpellBook[spell].is_known:
                        if player.bonus_action == 1 or player.action == 1: #if you have still action left 
                            #print(self.choose_spell(fight))
                            self.ChoosenSpell, SpellScore = self.choose_spell(fight)
                            break
                if self.ChoosenSpell != False:
                    Choices.append(self.smart_spellcasting)
                #Special Abilities
                if (player.dragons_breath_is_charged or player.spider_web_is_charged) and player.action == 1:
                    Choices.append(self.smart_special_abilities)
                
                if player.action == 1 and player.attack_counter > 0:
                    Choices.append(self.smart_attack)

                #Now give the Choices Scores
                ChoiceScores = [0 for i in Choices]
                if len(Choices) == 0: return #if nothing to do, return


                for i in range(0, len(Choices)):
                    Choice = Choices[i]
                    Score = 0
                    #This function will now assign scores to the choices
                    #The Scores should be roughly the amount of dmg, or an dmg equal value

                    #Wildshape
                    if Choice == self.smart_go_wildshape:
                        if player.level < 4: Score += 7*1*2 #Wolf, prop. at least 2 Rounds
                        elif player.level > 4: Score += 9*2*2 #Bear, prop. at least 2 Rounds
                        Score += player.HP/(player.CHP + player.HP/4)*Score   #if low on HP go wild shape
                        #Up to 4 times the score if very low
                        if player.knows_combat_wild_shape:
                            Score = Score*1.2  #if you know combat wild shape freaking go
                    
                    #Inspiration
                    if Choice == self.smart_inspire:
                        if randint(0,1) > 0: #50:50 chance to inspire
                            Score += player.level*2  #if you can inspire go for it

                    #Spellcasting
                    if Choice == self.smart_spellcasting:
                        Score = SpellScore #comes from the choose spell function

                    #Special Abilities
                    if Choice == self.smart_special_abilities:
                        if player.dragons_breath_is_charged:
                            Score += (20 + int(player.level*3.1))*3   #damn strong ability, at least 2-3 Targets
                        if player.spider_web_is_charged:
                            Score += player.dmg*player.attacks*1.5   #good Ability, better then simple attack

                    #Attack
                    if Choice == self.smart_attack:
                        Score = self.AttackScore
                        Score += (player.AC - 12 - player.level/3.5)*3 #encourage high AC to attack

                    ChoiceScores[i] = Score
                ActionDoTo = Choices[np.argmax(ChoiceScores)]
                ActionDoTo(fight) #Do the best Choice
                TryCounter += 1
                #First Round Action and Attacks
                #Secound Round Bonus Action 
                if TryCounter > 2: #sometimes a BA is left, but no choice with BA
                    if player.bonus_action == 1 and player.action == 1:
                        player.DM.say(player.name + ' count not decide what to do!')
                    return

        #------------Still in Wild Shape
        else: self.smart_in_wildshape(fight)

#-----------Smart Actions
    def smart_inspire(self, fight):
        player = self.player
        #Inspire random Ally
        if player.knows_inspiration and player.inspiration_counter > 0 and player.bonus_action == 1:
            player.inspire(self.allies[randint(0,len(self.allies)-1)])

    def smart_special_abilities(self, fight):
        player = self.player
        #Dragon Breath
        if player.knows_dragons_breath and player.action == 1:
            if player.dragons_breath_is_charged:
                if player.level < 10:
                    area = 250
                elif player.level < 15:
                    area = 450 
                elif player.level < 20:#60-ft-cone
                    area = 1800
                else:#90-ft-cone
                    area = 4000
                targets = self.area_of_effect_chooser(fight, area)
                if len(targets) == len([x for x in fight if x.team != player.team]) and len(targets) > 1:
                    max = int(len(targets)*0.25 + 0.5) #some should be able to get out, even for high are of effect
                    targets = targets[0:-1*max]
                player.use_dragons_breath(targets)
        
        #Spider Web
        if player.knows_spider_web and player.action == 1:
            if player.spider_web_is_charged:
                enemies_left = self.enemies_left_sort(fight)
                #Random Target
                player.use_spider_web(enemies_left[randint(0,len(enemies_left)-1)])

    def smart_go_wildshape(self, fight):
        player =self.player 
        if player.knows_wild_shape and player.wild_shape_uses > 0 and player.wild_shape_HP == 0:
            if player.action == 1 or (player.bonus_action == 1 and player.knows_combat_wild_shape):
                if player.level < 4:
                    player.wild_shape('Wolf')
                else:
                    player.wild_shape('BrownBear')

    def smart_in_wildshape(self, fight):
        player = self.player
        #This function is called in do_your_turn if the player is still in wild shape
        if self.dying_allies != []:
        #is someone dying
            dying_allies_deathcounter = [i.death_counter for i in self.dying_allies]
            if np.max(dying_allies_deathcounter) > 1:
                if player.SpellBook['CureWounds'].is_known and player.bonus_action == 1:
                    player.wild_reshape()
                    self.do_your_turn(fight) #this then starts the healing part again

        #Heal in combat wild shape
        self.try_wild_shape_heal()
        if player.action == 1:
            self.smart_attack(fight)
    
    def smart_heal(self, fight):
        player = self.player
        #------------------------Healing first----------------------------
        #!!!!!!!!!!!The Heal Section is still pretty slow
        #self is low
        if player.CHP < int(player.HP/3) and player.lay_on_hands_counter > player.lay_on_hands/5 and player.action == 1:
            player.use_lay_on_hands(player, player.lay_on_hands_counter - int(player.lay_on_hands_counter/5))

        #allies low
        if self.dying_allies != []:      #someone is dying
        #If someone is dying, use a healing Spell!!
            dying_allies_deathcounter = [i.death_counter for i in self.dying_allies]
            if np.max(dying_allies_deathcounter) > 1:
                most_dying_ally = np.argmax(dying_allies_deathcounter)    #most needy ally
                if player.SpellBook['HealingWord'].is_known and player.bonus_action ==1:   #when Someone is dying and u have healing word, heal!
                    for i in range(0,4):
                        if player.spell_slot_counter[i]>0:
                            player.SpellBook['HealingWord'].cast(self.dying_allies[most_dying_ally], cast_level=i+1)
                            break
                elif player.SpellBook['CureWounds'].is_known and player.action ==1:   #when Someone is dying and u have CureWounds, heal!
                    for i in range(0,4):
                        if player.spell_slot_counter[i]>0:
                            player.SpellBook['CureWounds'].cast(self.dying_allies[most_dying_ally], cast_level=i+1)
                            break  
                elif player.lay_on_hands_counter > 4 and player.action ==1:
                    player.use_lay_on_hands(self.dying_allies[most_dying_ally], 5)

    def smart_spellcasting(self,fight):
        player = self.player
        #Empowered Spell, if you have sorcery Points
        if player.sorcery_points > 2 and player.empowered_spell == False and player.knows_empowered_spell:
            Score = 0
            #Encourage for low HP
            if player.CHP < player.HP/2: Score += 10
            if player.CHP < player.HP/3: Score += 10
            if player.CHP < player.HP/4: Score += 10
            #Disencourage for low SP
            Score -= (1-player.sorcery_points/player.sorcery_points_base)*15
            Score*(randint(70,130)/100)
            if Score > 10:
                player.use_empowered_spell()
        if self.ChoosenSpell != False:
            self.ChoosenSpell()

    def smart_attack(self, fight):
        player = self.player
        #This function then actually does the attack
        if player.action == 1: #if nothing else, attack
            #Smite if u can and have not cast
            if player.knows_smite:
                for i in range(0,5):
                    if player.spell_slot_counter[4-i] > 0:  #here 0 - lv1 slot
                        player.initiate_smite(4-i+1)   #here the actual level are important (1 - lv 1 slot)
                        break
            if player.knows_reckless_attack:
                player.rackless_attack()
            if player.knows_rage and player.bonus_action == 1 and player.raged == 0:
                player.rage() #includes frenzy
            if player.is_in_frenzy and player.bonus_action == 1:
                player.use_frenzy_attack()
            while player.attack_counter > 0 and player.state == 1:  #attack enemies as long as attacks are free and alive (attack of opportunity might change that)
                target = self.choose_att_target(fight) #choose a target
                if target == False: #there might be no target
                    return
                else:
                    player.make_normal_attack_on(target, fight)  #attack that target

    def try_wild_shape_heal(self):
        player = self.player
        if player.knows_combat_wild_shape and player.bonus_action == 1:
            #if wild shape is low < 1/4
            if 0 < player.wild_shape_HP < player.wild_shape_HP/4:
                #Still have spell slots?
                for i in range(0,7):
                    if player.spell_slot_counter[6-i] > 0: #try all spell slots, starting at 6
                        player.use_combat_wild_shape_heal(spell_level=6-i+1) #spelllevel is 1+i

#---------Reaction
    def do_opportunity_attack(self,target):
        #this function is called when the player can do an attack of opportunity
        if target.knows_cunning_action and target.bonus_action == 1:
            target.use_disengage() #use cunning action to disengage
            return
        else:
            self.player.attack(target)

    def want_to_cast_shield(self, attacker, dmg):
        #This function is called in the attack function as a reaction, if Shild spell is known
        if self.player.CHP < dmg:
            for i in range(9):
                if self.player.spell_slot_counter[i] > 0:
                    self.player.SpellBook['Shield'].cast(i + 1)   #spell level is i + 1
                    break

#---------Support
    def area_of_effect_chooser(self, fight, area):   #area in square feet
    #The chooser takes all enemies and chooses amoung those to hit with the area of effect
    #every target can only be hit once, regardless if it is alive or dead 
    #how many targets wil be hit depends on the area and the density in that area from the Battlefield.txt
        enemies = [x for x in fight if x.team != self.player.team]
        target_pool = int(area/100 * self.player.DM.enemies_per_100_sqft + 0.5)   #how many enemies should be in that area
        #1 per 100sqft is about normal
        #0.5 is wide space
        #2 is crowded

        if target_pool < 1: target_pool = 1     #at least one will be hit 
        elif target_pool == 1 and area > 100 and len(enemies) > 3: target_pool = 2 #2 is easy to hit with AoE
        elif target_pool == 2 and area > 300 and len(enemies) > 6: target_pool = 3

        if target_pool > len(enemies)*0.8: #never will all be hit
            target_pool -= 1
        
        target_pool = int(target_pool*(1 + randint(-25,25)/100) + 0.5) #a little random power 
        if target_pool >= len(enemies):
            target_pool = len(enemies) - 1

        shuffle(enemies)
        if len(enemies) < target_pool:
            targets = enemies
        else:
            targets = enemies[0:target_pool]
        return targets

    def player_attack_score(self):
        #This function return a damage equal value, that should represent the dmg that could be expected form this player if it just attacks
        player = self.player
        Score = 0
        dmg = player.dmg
        attacks = player.attacks
        if (player.knows_rage and player.bonus_action == 1) or player.raged == 1:
            dmg += player.rage_dmg
        if player.knows_frenzy:
            attacks += 1
        if player.knows_reckless_attack:
            dmg = dmg*1.2 #improved chance to hit
        if player.hasted == 1:
            attacks += 1
        if player.entangled == 1:
            dmg = dmg*0.8

        #dmg score is about dmg times the attacks
        Score = dmg*attacks

        #Only on one Attack 
        if player.sneak_attack_counter == 1:
            Score += player.sneak_attack_dmg
        if player.wailsfromthegrave_counter > 0:
            Score += player.sneak_attack_dmg/2
        if player.knows_smite:
            for i in range(0,5):
                if player.spell_slot_counter[4-i] > 0:
                    Score += (4-i)*4.5  #Smite Dmg once

        #Other Stuff
        if player.dash_target != False: #Do you have a dash target?
            if player.dash_target.state == 1: Score*1.5 #Encourage a Dash target attack
        if player.has_range_attack == False:
            Score = Score*np.sqrt(player.AC/(13 + player.level/3.5)) #Encourage player with high AC
        return Score

    def choose_att_target(self, fight, AttackIsRanged = False, other_dmg = False):
        player = self.player
        if other_dmg == False:
            dmg = player.dmg
        else:
            dmg = other_dmg
        #function returns False if no target in rech
        #this function takes all targets that are possible in reach and choosed which one to attack
        #the AttackIsRanged is to manually say the function that the Attack is ranged, even if the player might not have ranged attacks, for Spells for example
        EnemiesInReach = player.enemies_reachable_sort(fight, AttackIsRanged)

        ThereIsADashTarget = False
        if player.dash_target != False:
            if player.dash_target.state == 1:
                ThereIsADashTarget = True

        if len(EnemiesInReach) == 0:
            player.DM.say('There are no Enemies in reach for ' + player.name + ' to attack')
            player.move_position() #if no target in range, move a line forward
            player.attack_counter = 0
            return False  #return, there is no target
        elif ThereIsADashTarget:
            #If the Dash Target from last turn is still alive, attack
            return player.dash_target
        else:
            target_list = EnemiesInReach
            #This function is the intelligence behind choosing the best target to hit from a List of given Targets. It chooses reguarding lowest Enemy and AC and so on
            ThreatScore = [0 for x in target_list]
            for i in range(0, len(target_list)):
                target = target_list[i]
                Score = 0
                ScoreList = []
                #Dmg done by the creature
                DmgScore = target.dmg_dealed/player.HP * 40
                if DmgScore > 150: DmgScore = 150
                ScoreList.append(DmgScore)
                #How Low the Enemy is
                HPScore = 25*(target.HP - target.CHP)/target.HP
                ScoreList.append(HPScore)
                #If you can oneshot the target, go for it
                if target.CHP <= dmg: OneShotScore = 120
                else: OneShotScore = 0
                ScoreList.append(OneShotScore)
                #It might be good to hit a target with a low AC
                ACScore = (20 - target.AC)*3
                if ACScore < 0: ACScore = 0
                ScoreList.append(ACScore)
                #Kill Enemies that have your Vulerability as Dmg_type
                DMGTypeScore = 0
                if target.last_used_DMG_Type in player.damage_vulnerability: DMGTypeScore += 20
                ScoreList.append(DMGTypeScore)

                #Spell Score, attack Entangler
                SpellScore = 0
                if player.entangled == 1 and target == player.entangled_by:
                    SpellScore = 100
                if target.is_entangling == 1: SpellScore += 10
                if target.is_hasting == 1: SpellScore += 20
                if target.concentration == 1: SpellScore += 10
                ScoreList.append(SpellScore)

                #Wild Shape Score, it is not so useful to attack wild shape forms
                WildshapeScore = 0
                if target.wild_shape_HP > 0 and target.knows_combat_wild_shape == False: WildshapeScore = -15
                if target.wild_shape_HP <= player.dmg: WildshapeScore += 20
                ScoreList.append(WildshapeScore)

                #Condition Score
                ConditionScore = 0
                if target.restrained or target.prone or target.blinded: ConditionScore = 40
                ScoreList.append(ConditionScore)

                #Line Score, Frontliner will go for front and mid mainly
                LineScore = 0
                if player.position == 0: #front
                    if target.position == 0: LineScore += 30
                elif player.position == 1: #Mid
                    if target.position == 0: LineScore += 40
                    elif target.position == 2: LineScore += 20
                    elif target.position == 3: LineScore += 20
                elif player.position == 2: #Back
                    if target.position == 2: LineScore += 25
                    elif target.position == 3: LineScore += 30
                elif player.position == 3: #Airborn
                    if target.position == 2: LineScore += 20
                ScoreList.append(LineScore)
                
                #Movement Score
                MovementScore = 0
                if player.need_dash(target, fight) == 1 and player.knows_cunning_action == False: MovementScore -= 90
                elif player.need_dash(target, fight) == 1 and player.knows_cunning_action: MovementScore -= 20
                #it costs a turn to dash except if you have cunning action
                if player.will_provoke_Attack(target, fight):
                    if player.CHP > player.HP/3: MovementScore -= 40
                    else: MovementScore -= 60
                ScoreList.append(MovementScore)

                for x in ScoreList:
                    Score += x*randint(1,5)
                    #Every individual Score gets a random weigth
                if player.last_used_DMG_Type in target_list[i].damage_resistances or player.last_used_DMG_Type in target_list[i].damage_immunity:
                    Score -= 120      #makes no sense to attack an immune target 
                ThreatScore[i] = Score
            return target_list[np.argmax(ThreatScore)]

    def spell_cast_check(self, spell):
        player = self.player
        #This function checks if a given Spell is castable for the player, even with quickened Spell
        if spell.is_known == False:
            return False
        #Check if Player has spellslots
        if spell.spell_level > 0:
            good_slots = 0
            for i in range(spell.spell_level - 1,9):
                if player.spell_slot_counter[i] > 0:
                    good_slots += 1
            if good_slots == 0:
                return False
                
        if player.wild_shape_HP > 0:
            return False
        elif spell.is_concentration_spell and player.concentration == 1:
            return False
        elif spell.is_reaction_spell:
            return False   #reaction Spell in own turn makes no sense
        elif spell.is_cantrip == False and player.cast == 0:
            return False


        #Action Check
        if spell.is_bonus_action_spell and player.bonus_action == 1:
            if spell.is_cantrip:
                return 1         #have BA, is cantrip -> cast 
            elif player.cast == 1:
                return 1        #have BA, is spell, have caste left? -> cast
            else:
                return False    #cant cast, have already casted
        elif spell.is_bonus_action_spell == False:
            if player.action == 1:
                if spell.is_cantrip:
                    return 1 #have action and is cantrip? -> cast
                elif player.cast == 1:
                    return 1 #have action and cast left? -> cast
                else:
                    return False
            elif player.bonus_action == 1 and player.knows_quickened_spell and player.sorcery_points >= 2:
                if spell.is_cantrip:
                    return 2  #Cast only with Quickened Spell
                elif player.cast ==1:
                    return 2  #have cast left?
                else:
                    return False
            else:
                return False
        else:
            False

    def choose_quickened_cast(self):
        #This function is called once per trun to determine if player wants to use quickned cast this round
        player = self.player
        QuickScore = 100
        QuickScore = QuickScore*(1.5 - 0.5*(player.CHP/player.HP)) #encourage quickend cast if youre low, if CHP -> 0, Score -> 150
        if player.cast == 1: QuickScore = QuickScore*1.4    #encourage if you havend cast yet
        if player.sorcery_points < player.sorcery_points_base/2: QuickScore = QuickScore*0.9 #disencourage for low SP
        elif player.sorcery_points < player.sorcery_points_base/3: QuickScore = QuickScore*0.8
        elif player.sorcery_points < player.sorcery_points_base/5: QuickScore = QuickScore*0.7
        if player.entangled == 1: QuickScore = QuickScore*1.1  #Do something against the entangle
        #Random Power for quickened Spell
        QuickScore = QuickScore*(1+randint(-35,35)/100) #+/- 35%
        if QuickScore > 100:
            return True
        else:
            return False

    def choose_spell(self, fight):
        #This function chooses a spell for the spell choice
        #If this function return False, spellcasting is not an option for this choice
        player = self.player
        SpellChoice = False

        Choices = []

        #Check Spells
        for spellname in player.SpellNames:
            Checkvalue = self.spell_cast_check(player.SpellBook[spellname])
            if Checkvalue == 1:#check is spell is castable
                Choices.append(player.SpellBook[spellname].cast)
            if Checkvalue == 1 and player.SpellBook[spellname].is_twin_castable and player.sorcery_points > player.SpellBook[spellname].spell_level:
                Choices.append(player.SpellBook[spellname].twin_cast)
            elif Checkvalue == 2: #Spell is only castable via quickened spell
                Choices.append(player.SpellBook[spellname].quickened_cast)

        #This function determines if the player wants to cast a quickened spell this round
        if player.knows_quickened_spell:
            cast_quickened_this_round = self.choose_quickened_cast()
        else:
            cast_quickened_this_round = False

        ChoiceScores = [0 for i in Choices]
        if len(Choices) == 0:
            return False, 0  #if no spell is castable return False
        TargetList = [[player] for i in Choices] #will be filled with targets
        LevelList = [0 for i in Choices]#at what Level the Spell is casted
        for i in range(0, len(Choices)):
            Choice = Choices[i]
            Score = 0

        #In the following all Options will get a score, that roughly resemlbes their dmg or equal dmg value
        #This Score is assigned by a function of the spellcasting class 
        #This function also evalues if it is good to use a quickened or twin cast
        #The evaluation of quickened Cast is currently not handled by these functions
            for spell in player.SpellNames:
                if Choice == player.SpellBook[spell].cast:
                    Score, SpellTargets, CastLevel = player.SpellBook[spell].score(fight)
                elif Choice == player.SpellBook[spell].quickened_cast:
                    if cast_quickened_this_round == True:
                        Score, SpellTargets, CastLevel = player.SpellBook[spell].score(fight, quickened_cast=True)
                    else:
                        #Basically dont cast quickened this round
                        Score = 0
                        SpellTargets = [player]
                        CastLevel = 0
                elif Choice == player.SpellBook[spell].twin_cast:
                    Score, SpellTargets, CastLevel = player.SpellBook[spell].score(fight, twinned_cast=True)

            ChoiceScores[i] = Score
            TargetList[i] = SpellTargets
            LevelList[i] = CastLevel
        #Now find best value and cast that
        ChoiceIndex = np.argmax(ChoiceScores)

        #Before returning the Value check if it is even sensable to cast instaed of doing something else
        #This part gives a Value of the possible alternatives and assignes a dmg equal value to compare with
        #This is the Score that will be compared for the action Spell, so assume an action is left
        AltScore = self.AttackScore #is evaluated in do_your_turn before 
        if player.action == 1:
            #If the player has still its action, compete with this alternative score
            if np.max(ChoiceScores) > AltScore:
                SpellChoice = partial(Choices[ChoiceIndex],TargetList[ChoiceIndex],LevelList[ChoiceIndex])
                return SpellChoice, ChoiceScores[ChoiceIndex]
            else:
                return False, 0 #If you have action and cant beat this Score, dont cast spell
        elif player.bonus_action == 1:
            if np.max(ChoiceScores) > player.dmg + 1:    #just a small threshold
                    SpellChoice = partial(Choices[ChoiceIndex],TargetList[ChoiceIndex],LevelList[ChoiceIndex])
                    return SpellChoice, ChoiceScores[ChoiceIndex]
            else:
                return False, 0
        else: return False, 0

    def enemies_left_sort(self,fight):
        enemies_left_list = [x for x in fight if x.team != self.player.team and x.state == 1]
        return enemies_left_list

    def lowest_enemy(self, fight):
        DM = self.player.DM
        enemies_left_list = self.enemies_left_sort(fight)
        if enemies_left_list == []:
            return self.player  #sometimes the fight is alredy over, then return self
        return enemies_left_list[np.argmin([x.CHP for x in enemies_left_list])]     #find lowest Enemy

class spell:
    def __init__(self, player, spell_name):
        #this class is initiated at the entity for spellcasting
        self.DM = player.DM
        self.player = player            #the Player that is related to this spell Object and which will cast this spell        
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)
        self.spell_name = spell_name          #Specify the Spell

        #Initial
        self.spell_level = 0
        self.is_bonus_action_spell = False
        self.is_concentration_spell = False
        self.is_reaction_spell = False
        self.is_cantrip = False
        self.is_twin_castable = False

        self.is_known = False
        if spell_name in player.spell_list:
            self.is_known = True

        self.spell_save_type = False

        #Here all Information of the Spell that was initiated are assigned 
        #and the Entity.spell.cast() function is assigned to the corresponding Spell
        #the score_spell_name function evalues dmg like scores for choose_spell_function in AI
        if spell_name == 'FireBolt':
            self.spell_level = 0
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = True
            self.is_twin_castable = True
            self.cast = self.cast_fire_bolt
            self.score = self.score_fire_bolt

        if spell_name == 'Entangle':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = True
            self.is_cantrip = False
            self.cast = self.cast_entangle
            self.score = self.score_entangle

        if spell_name == 'BurningHands':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.spell_save_type = 1 #Dex
            self.cast = self.cast_burning_hands
            self.score = self.score_burning_hands

        if spell_name == 'CureWounds':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_cure_wounds
            self.score = self.score_cure_wounds

        if spell_name == 'HealingWord':
            self.spell_level = 1
            self.is_bonus_action_spell = True
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_healing_word
            self.score = self.score_healing_word

        if spell_name == 'MagicMissile':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_magic_missile
            self.score = self.score_magic_missile

        if spell_name == 'AganazzarsSorcher':
            self.spell_level = 2
            self.spell_save_type = 1 #Dex
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_aganazzars_sorcher
            self.score = self.score_aganazzars_scorcher

        if spell_name == 'ScorchingRay':
            self.spell_level = 2
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_scorching_ray
            self.score = self.score_scorching_ray

        if spell_name == 'Fireball':
            self.spell_level = 3
            self.spell_save_type = 1 #Dex
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_fireball
            self.score = self.score_fireball

        if spell_name == 'Haste':
            self.spell_level = 3
            self.is_bonus_action_spell = False
            self.is_concentration_spell = True
            self.is_cantrip = False
            self.cast = self.cast_haste
            self.score = self.score_haste

        if spell_name == 'Shield':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.is_reaction_spell = True
            self.cast = self.cast_shield
            self.score = self.score_shield
        
        if spell_name == 'EldritchBlast':
            self.spell_level = 0
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = True
            self.cast = self.cast_eldritch_blast
            self.score = self.score_eldritch_blast
       
    #any spell has a specific Spell cast function that does what the spell is supposed to do
    #To do so, the make_spell_check function makes sure, that everything is in order for the self.player to cast the spell
    #The make_action_check function checks if Action, Bonus Action is used
    #the spell class objects will be linked to the player casting it by self.player

    def make_spell_check(self, cast_level):
        #check if spell is known
        if self.is_known == False:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', without knowing the spell')
            return False
        #check if player is under casting
        elif cast_level < self.spell_level:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ' at a lower level: ' + str(cast_level))
            return False
        #check if player has Spellslots
        elif self.player.spell_slot_counter[cast_level -1] <= 0:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name +', but spell slots level ' + str(cast_level) + ' are empty')
            return False        
        #check if player is in wild shape
        elif self.player.wild_shape_HP > 0:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but is in wild shape')
            return False
        #check if player is concentrating and tries to cast a concentration spell
        elif self.is_concentration_spell and self.player.concentration == 1:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but is currently concentrating')
            return False
        #Is reaction Spell break here
        elif self.is_reaction_spell:
            if self.player.reaction == 0:
                return False
            else:
                self.player.reaction = 0
                self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
                return True
        #check if player has cast this round
        elif self.player.cast == 0:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has already cast a spell')
            return False
        #check is player has action/bonus action left
        elif self.make_action_check() == False:
            return False
        #everything clear for cast
        else:
            self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
            return True

    def make_cantrip_check(self):
        #check if spell is known
        if self.is_known == False:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', without knowing the spell')
            return False
        #check if player is in wild shape
        elif self.player.wild_shape_HP > 0:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but is in wild shape')
        #check if player is concentrating and tries to cast a concentration spell
        elif self.is_concentration_spell and self.player.concentration == 1:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but is currently concentrating')
            return False
        #check is player has action/bonus action left
        elif self.make_action_check() == False:
            return False
        #everything clear for cast
        else:
            return True        

    def make_action_check(self):
        #Bonus Action Spell
        if self.is_bonus_action_spell:
            #Bonus Action used?
            if self.player.bonus_action == 0:
                self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has no Bonus Action left')
                return False
            #Allow cast and use bonus_action
            else:
                self.player.bonus_action = 0       #Bonus Action used
                if self.is_cantrip == False:
                    self.player.cast = 0
                return True
            
        #Action Spell
        else:
            #Quickened Spell
            if self.player.quickened_spell == 1:
                #Bonus Action free?
                if self.player.bonus_action == 1:
                    #Cast Spell as quickened BA
                    self.player.bonus_action = 0
                    self.player.quickened_spell = 0
                    if self.is_cantrip == False:
                        self.player.cast = 0
                    return True
                #No Bonus Action left
                else:
                    self.DM.say(self.player.name + ' tried to quickened cast ' + self.spell_name + ', but has no Bonus Action left')
                    return False
            #No Quickened Spell
            else:
                if self.player.action == 0:
                    self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has no action left')
                    return False
                else:
                    self.player.action = 0  #action used
                    if self.is_cantrip == False:
                        self.player.cast = 0
                    return True

#-------------Meta Magic------------------
    #the twin_cast function needs exectly two targets
    def twin_cast(self, targets, cast_level=False):
        if len(targets) != 2:
            self.player.DM.say('Twin Cast needs 2 Targets')
            quit()
        if self.player.knows_twinned_spell and self.player.sorcery_points >= 2 and len(targets) == 2:
            #If twinned spell is known and sorcery Points there, cast spell twice 
            if self.make_action_check() == True:
                #player should be able to cast, so a True came back. But in the macke_action_check function the bonus_action, action, and/or cast was diabled, so it will be enabled here before casting 
                if cast_level==False:
                    cast_level = self.spell_level
                if cast_level == 0:
                    self.player.sorcery_points -= 1
                else:
                    self.player.sorcery_points -= self.spell_level
                self.DM.say(self.player.name + ' twinned casts ' + self.spell_name)
                for x in targets:
                    #everything will be enabeled in order for the spell do be cast twice
                    if self.is_bonus_action_spell:
                        self.player.bonus_action = 1
                    else:
                        self.player.action = 1
                    if self.is_cantrip == False:
                        self.player.cast = 1
                    self.cast(x, cast_level)
        else:
            if self.player.knows_twinned_spell == False:
                self.DM.say(self.player.name + ' tried to twinned spell ' + self.spell_name + ' without knwoing it')
            elif self.player.sorcery_points < 2:
                self.DM.say(self.player.name + ' tried to twinned spell ' + self.spell_name + ' but has not enough sorcery points')
            elif len(targets) != 2:
                self.DM.say(self.player.name + ' tried to twinned spell ' + self.spell_name + ' but not with 2 targets')

    def quickened_cast(self, targets, cast_level=False):
        if len(targets) != 1: #if spell has just one target 
            targets = targets[0]

        if self.player.knows_quickened_spell:
            if self.player.sorcery_points < 2:
                self.DM.say(self.player.name + ' tried to use quickened Spell, but has no Sorcery Points left')
            else:
                if self.player.quickened_spell == 1:
                    self.say(self.name + ' tried to use quickened spell, but has already used it')
                else:
                    self.player.sorcery_points -= 2
                    self.player.quickened_spell = 1
                    self.DM.say(self.player.name + ' used Quickened Spell')
                    if cast_level==False:
                        cast_level = self.spell_level
                    self.cast(targets, cast_level)

        else:
            self.DM.say(self.player.name + ' tried to use Quickened Spell without knowing it')

#-------------Cast Spells------------------
    def cast_fire_bolt(self, target, cast_level=0):
        if type(target) == list:
            target = target[0]
        if self.make_cantrip_check() == False:
            return
        else:
            tohit = self.player.spell_mod + self.player.proficiency

            if self.player.level < 5:
                dmg = 5.5
            elif self.player.level < 11:
                dmg = 5.5*2
            elif self.player.level < 17:
                dmg = 5.5*3
            else:
                dmg = 5.5*4

            if self.player.empowered_spell:
                dmg = dmg*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')

            self.DM.say(str(self.player.name) + ' casts fire bolt: ', end='')
            #all specifications for this spell are given to the attack function
            self.player.attack(target, other_dmg=dmg, damage_type='fire', other_tohit=tohit)
            self.player.fire_bolt_cast += 1
    
    def cast_eldritch_blast(self, targets, cast_level=0):
        if self.make_cantrip_check() == False:
            return
        else:
            tohit = self.player.spell_mod + self.player.proficiency

            if self.player.level < 5:
                atk_counter = 1
            elif self.player.level < 11:
                atk_counter = 2
            elif self.player.level < 17:
                atk_counter = 3
            else:
                atk_counter = 4

            dmg = 5.5
            if self.player.knows_agonizing_blast:
                dmg += self.player.modifier[5] #Add Cha Mod
            if self.player.empowered_spell:
                dmg = dmg*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            if self.player.knows_agonizing_blast:
                self.DM.say('Agonizing: ', end='')
            self.DM.say(self.player.name + ' casts eldritch blast: ', end='')

            if type(targets) != list:  #if targets is only one Entity passed
                targets = [targets]
            target_counter = 0
            while atk_counter > 0:    #loop for missile cast
                #attack fist target with spell specifications and then move to next
                self.player.attack(targets[target_counter], other_dmg=dmg, damage_type='force', other_tohit=tohit)
                atk_counter -= 1
                target_counter += 1
                if target_counter == len(targets):    #if all targets are hit once, restart 
                    target_counter = 0

            self.player.eldritch_blast_cast += 1

    def cast_entangle(self, target, cast_level=1):
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            target.last_attacker = self.player    #target remembers last attacker
            save = target.make_save(0)           #let them make save
            if save < self.player.spell_dc:
                #write the entagle variables for the player and target
                self.player.is_entangling = 1
                self.player.entangling_target = target
                target.entangled = 1
                target.entangled_by = self.player
                target.restrained = 1               #make them restrained
                self.DM.say(self.player.name + ' casts Entangle and ' + str(target.name) + ' failed save with: ' + str(save))
                self.player.entangle_cast += 1
                self.player.concentration = 1
            else:
                self.DM.say(self.player.name + ' casts Entangle but ' + str(target.name) + ' made save with: ' + str(save))
                self.player.entangle_cast += 1

    def cast_burning_hands(self, targets, cast_level=1):
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.player.name + ' casts Burning Hands at Level: ' + str(cast_level))
            self.player.burning_hands_cast += 1
            dmg = 10.5 + 3.5*(cast_level - 1)   #upcast dmg 3d6 + 1d6 per level over 2
            if self.player.empowered_spell:
                dmg = dmg*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            for i in targets:
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(1)           #let them make dex saves
                if save >= self.player.spell_dc:
                    i.changeCHP(dmg/2, self.player, 'fire')             #save made
                else:
                    i.changeCHP(dmg, self.player, 'fire')

    def cast_cure_wounds(self, target, cast_level=1):
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Cure Wounds at level: ' + str(cast_level))
            self.player.cure_wounds_cast += 1
            heal = 4.5*cast_level + self.player.spell_mod
            target.changeCHP(-heal, self.player)

    def cast_healing_word(self, target, cast_level=1):
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Healing Word at level: ' + str(cast_level))
            self.player.healing_word_cast += 1
            heal = 2.5*cast_level + self.player.spell_mod
            target.changeCHP(-heal, self.player)

    def cast_magic_missile(self, targets, cast_level=1):           #needs list of targets
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.player.name + ' casts Magic Missile at level ' + str(cast_level))
            self.player.magic_missile_cast += 1
            missile_counter = 2 + cast_level          #overcast mag. mis. for more darts 
            target_counter = 0
            dmg = 3.5   #1d4 + 1
            if self.player.empowered_spell:
                dmg = dmg*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            while missile_counter > 0:    #loop for missile cast
                missile_counter -= 1
                targets[target_counter].last_attacker = self.player    #target remembers last attacker
                targets[target_counter].changeCHP(dmg, self.player, 'force')    #target takes damage
                target_counter += 1
                if target_counter == len(targets):    #if all targets are hit once, restart 
                    target_counter = 0

    def cast_aganazzars_sorcher(self, targets, cast_level=2):
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Aganazzars Sorcher at Level: ' + str(cast_level))
            self.player.aganazzars_sorcher_cast += 1
            if type(targets) != list:
                targets = [targets]
            dmg = 13.5 + 4.5*(cast_level - 2)   #upcast dmg 3d6 + 1d6 per level over 2
            #empowered Spell
            if self.player.empowered_spell:
                dmg = dmg*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            for i in targets:
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(1)           #let them make saves
                if save >= self.player.spell_dc:
                    i.changeCHP(dmg/2, self.player, 'fire')             #save made
                else:
                    i.changeCHP(dmg, self.player, 'fire')

    def cast_scorching_ray(self, targets, cast_level=2):           #needs list of targets
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list:  #if targets is only one Entity passed
                targets = [targets]
            self.DM.say(self.player.name + ' casts Scorching Ray at Level: ' + str(cast_level))
            self.player.scorching_ray_cast += 1
            tohit = self.player.spell_mod + self.player.proficiency
            dmg = 7
            if self.player.empowered_spell:
                dmg = dmg*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            ray_counter = 1 + cast_level          #overcast + 1 Ray per level
            target_counter = 0
            while ray_counter > 0:    #loop for missile cast
                #attack fist target with spell specifications and then move to next
                self.player.attack(targets[target_counter], other_dmg=dmg, damage_type='fire', other_tohit=tohit)
                ray_counter -= 1
                target_counter += 1
                if target_counter == len(targets):    #if all targets are hit once, restart 
                    target_counter = 0

    def cast_fireball(self, targets, cast_level=3):
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.player.name + ' casts Fireball at Level: ' + str(cast_level))
            self.player.fireball_cast += 1
            dmg = 28 + 3.5*(cast_level - 3)   #upcast dmg 3d6 + 1d6 per level over 2
            spell_is_empowered = False
            if self.player.empowered_spell:
                dmg=dmg*1.21
                self.player.empowered_spell = False
                spell_is_empowered = True                
            for i in targets:
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(1)           #let them make saves
                if spell_is_empowered:
                    self.DM.say('Empowered: ', end='')
                if save >= self.player.spell_dc:
                    i.changeCHP(dmg/2, self.player, 'fire')             #save made
                else:
                    i.changeCHP(dmg, self.player, 'fire')

    def cast_haste(self, target, cast_level = 3):
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Haste for ' + target.name)
            self.player.haste_cast += 1
            self.player.concentration = 1
            target.get_hasted_by(self.player)
    
    def cast_shield(self, cast_level = 1):
        if self.make_spell_check(cast_level): #return True if everything is in order, reaction and spellslots are then expendet
            self.DM.say(self.player.name + ' casts Shield, ', end='') #interrupts the attack function prints 
            self.player.shield_cast += 1
            self.player.AC += 5

#---------------DMG Scores---------------
#This Scores are returned to the choose_spell_AI function and should resemble about 
#the dmg that the spell makes or an appropriate counter value if the spell does not 
#make direkt dmg, like haste or entangle
#The Function must also return the choosen Targets and Cast Level
#If a Score 0 is returned the spell will not be considered to be cast that way

    def hit_propability(self, target):
    #This function evaluetes how propable a hit with a spell attack will be
        SpellToHit = self.player.spell_mod + self.player.proficiency
        AC = target.AC
        prop = (20 - AC + SpellToHit)/20
        return prop

    def save_sucess_propability(self, target):
        SaveMod = target.modifier[self.spell_save_type]  #Currently Dex
        #Save Sucess Propability:
        prop = (20 - self.player.spell_dc + SaveMod)/20
        return prop

    def dmg_score(self, SpellTargets, dmg, dmg_type, SpellAttack=True, SpellSave=False):
        DMGScore = 0
        for target in SpellTargets:
            target_dmg = dmg
            if SpellSave: #Prop that target makes save
                target_dmg = dmg/2 + (dmg/2)*(1-self.save_sucess_propability(target))
            if SpellAttack:   #it you attack, account for hit propabiltiy
                target_dmg = target_dmg*self.hit_propability(target)#accounts for AC
            #DMG Type, Resistances and stuff
            if dmg_type in target.damage_vulnerability:
                target_dmg = target_dmg*2
            elif dmg_type in target.damage_resistances:
                target_dmg = target_dmg/2
            elif dmg_type in target.damage_immunity:
                target_dmg = 0
            DMGScore += target_dmg #Add this dmg to Score
        return DMGScore

    def return_0_score(self):
        #this function returns a 0 score, so that spell is not cast
        Score = 0
        SpellTargets = [self.player]
        CastLevel = 0
        return Score, SpellTargets, CastLevel

    def random_score_scale(self):
        Scale = 1+randint(-40,40)/100
        return Scale

    #originally the quickened_Cast and twinned_cast where designed to encourage and discourage meta magic cast for every spell individually, currently this is already done for quickened cast for all spells in the choose spell function.
    #But it could be done here too 

    def score_fire_bolt(self, fight, quickened_cast = False, twinned_cast = False):
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True)]
        if SpellTargets == [False]: #No Target
            return self.return_0_score()
        if twinned_cast:
            #Secound Target for Twin Cast
            twin_target = self.player.AI.choose_att_target(fight, AttackIsRanged=True)
            if twin_target == False:
                return self.return_0_score()
            SpellTargets.append(twin_target)
        
        CastLevel = 0 #always 0 for cantrip
        if self.player.level >=17: dmg= 5.5*4
        elif self.player.level >=11: dmg= 5.5*3
        elif self.player.level >= 5: dmg = 5.5*2
        else: dmg = 5.5        
        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=True)

        Score = Score*self.random_score_scale() # a little random power 
        return Score, SpellTargets, CastLevel

    def score_entangle(self, fight, quickened_cast = False, twinned_cast = False):
        #Choose One Target
        #Not twincastable currently
        SpellTargets =  [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=0)]
        if SpellTargets[0] == False: #No Target
            return self.return_0_score()
        #Score is equal to how dangerous the target is
        Score = (SpellTargets[0].AC - 12) + SpellTargets[0].dmg/2 + SpellTargets[0].level/3
        if self.player.spell_slot_counter[0]>0:
            CastLevel = 1
        elif self.player.spell_slot_counter[0]>0:
            CastLevel = 2
        elif self.player.spell_slot_counter[0]>0:
            CastLevel = 3
        else: #just dont cast if entangle is the best u can do at lv 4
            CastLevel = 0
            Score = 0
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel
    
    def score_burning_hands(self, fight, quickened_cast = False, twinned_cast = False):
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 115) #15ft**2/2
        for j in range(0,9): #What Level to cast
            if self.player.spell_slot_counter[8-j] > 0:
                CastLevel = 8-j+1  #cast level is +1
        Score = 0
        #Dmg Score
        dmg = 3*3.5 + 3.5*(CastLevel-1)
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale() #a little random power
        return Score, SpellTargets, CastLevel

    def score_cure_wounds(self, fight, quickened_cast = False, twinned_cast = False):
        return self.return_0_score() #at the moment, healing is handeled differently

    def score_healing_word(self, fight, quickened_cast = False, twinned_cast = False):
        return self.return_0_score() #at the moment, healing is handeled differently

    def score_magic_missile(self, fight, quickened_cast = False, twinned_cast = False):
        for j in range(0,9): #What Level to cast
            if self.player.spell_slot_counter[8-j] > 0:
                CastLevel = 8-j+1  #cast level is +1
        TargetNumer = CastLevel + 2
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5) for i in range(0, TargetNumer)]
        if False in SpellTargets:
            return self.return_0_score()

        #DMG Score
        Score = self.dmg_score(SpellTargets, 3.5, dmg_type='force', SpellAttack=False)
        Score += 2*CastLevel #a little extra for save hit 
        Score = Score*self.random_score_scale() # +/-20% range to vary spells
        return Score, SpellTargets, CastLevel

    def score_aganazzars_scorcher(self, fight, quickened_cast = False, twinned_cast = False):    
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 150) #30ft*5ft
        for j in range(0,8):
            if self.player.spell_slot_counter[8-j] > 0:
                CastLevel = 8-j+1  #cast level is +1
        
        #DMG Score
        dmg = 13.5 + 4.5*(CastLevel-2)
        Score = self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_scorching_ray(self, fight, quickened_cast = False, twinned_cast = False):
        for j in range(0,8): #What Level to cast
            if self.player.spell_slot_counter[8-j] > 0:
                CastLevel = 8-j+1  #cast level is +1
        TargetNumer = CastLevel + 1
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5) for i in range(0, TargetNumer)]
        if False in SpellTargets: #No Target
            return self.return_0_score()

        #Dmg Score
        dmg = 7
        Score = 0
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=True)
        Score = Score*self.random_score_scale() # +/-20% range to vary spells
        return Score, SpellTargets, CastLevel

    def score_fireball(self, fight, quickened_cast = False, twinned_cast = False):
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 315) #pi*10ft**2
        for j in range(0,7):
            if self.player.spell_slot_counter[8-j] > 0:
                CastLevel = 8-j+1  #cast level is +1
        
        #DMG Score
        dmg = 28
        Score = self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_haste(self, fight, quickened_cast = False, twinned_cast = False):
        SpellTargets = [self.player.AI.allies[randint(0,len(self.player.AI.allies)-1)]] #random Ally
        Score = 0
        Score += SpellTargets[0].dmg*SpellTargets[0].attacks
        Score += SpellTargets[0].tohit
        Score += SpellTargets[0].AC - self.player.AC
        #Dont haste low Ally
        if SpellTargets[0].CHP < SpellTargets[0].HP/4:
            Score -= SpellTargets[0].dmg

        if self.player.spell_slot_counter[2]>0:
            CastLevel = 3
        elif self.player.spell_slot_counter[3]>1:
            CastLevel = 4
        elif self.player.spell_slot_counter[4]>1:
            CastLevel = 5
        else: #just dont cast if Haste is the best u can do at lv 6
            CastLevel = 0
            Score = 0
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_shield(self, fight, quickened_cast = False, twinned_cast = False):
        return self.return_0_score() #shield should not be considered to cast in turn 

    def score_eldritch_blast(self, fight, quickened_cast = False, twinned_cast = False):
        if self.player.level >=17:TargetNumer = 4
        elif self.player.level >=11:TargetNumer = 3
        elif self.player.level >= 5:TargetNumer = 2
        else:TargetNumer = 1
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True) for i in range(0,TargetNumer)]
        if False in SpellTargets: #No Target
            return self.return_0_score()        

        CastLevel = 0 #always for cantrip

        #DMG Score
        Score = 0
        dmg = 5.5
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=True)
        
        Score = Score*self.random_score_scale() # a little random power
        return Score, SpellTargets, CastLevel