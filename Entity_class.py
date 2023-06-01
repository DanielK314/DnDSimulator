from Ifstatement_class import ifstatements
from Dmg_class import dmg
from AI_class import AI

from random import random, shuffle
import numpy as np
import json

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


    #Base Properties
        self.name = str(name)
        self.orignial_name = str(name)        #restore name after zB WildShape
        self.team = team                                      #which Team they fight for
        self.NPC = 0                        #NPCs like Skeletons
        self.type = str(data['Type'])
        self.base_type = self.type

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
        self.offhand_dmg = float(data['OffHand']) #If 0, no Offhand dmg

        self.level = float(data['Level'])           #It is not fully implementet yet, but level is used in some functions already, Level is used as CR for wildshape and co

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
        self.hex_cast = 0
        self.armor_of_agathys_cast = 0
        self.false_life_cast = 0
        self.spiritual_weapon_cast = 0
        self.shatter_cast = 0
        self.conjure_animals_cast = 0
        self.guiding_bolt_cast = 0

        #Spells known
        self.spell_list = data['Spell_List']

        #If this updates, the All_Spells in the GUI will load this
        #Keep this in Order of the Spell Level, so that it also fits for the GUI
        self.SpellNames = ['FireBolt', 'EldritchBlast', 'BurningHands', 'MagicMissile', 'GuidingBolt', 'Entangle', 'CureWounds', 'HealingWord', 'Hex', 'ArmorOfAgathys', 'FalseLife', 'Shield', 'AganazzarsSorcher', 'ScorchingRay', 'Shatter', 'SpiritualWeapon', 'Fireball', 'Haste', 'ConjureAnimals']
        self.SpellBook = {SpellName: spell(self, SpellName) for SpellName in self.SpellNames}

        #Haste
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        #Hex 
        self.can_choose_new_hex = False 
        #Armor of Agathys
        self.has_armor_of_agathys = False
        self.agathys_dmg = 0
        #Spiritual Weapon
        self.has_spiritual_weapon = False
        self.SpiritualWeaponDmg = 0
        self.SpiritualWeaponCounter = 0
        #Conjure Animals
        self.has_animals_conjured = False
        self.is_a_conjured_animal = False   #Is a constand state, see spell conjure animals
        self.conjurer = False #This is the player that conjured this entity
        #Guiding Bolt
        self.used_guiding_bolt = False
        self.is_guiding_bolted = False


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
        #Interseption
        if 'Interception' in self.other_abilities:
            self.knows_interseption = True
        else: self.knows_interseption = False
        self.interseption_amount = 0 #is true if a interseptor is close, see end_of_turn

        #UncannyDodge
        if 'UncannyDodge' in self.other_abilities:
            self.knows_uncanny_dodge = True
        else:
            self.knows_uncanny_dodge = False
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
        #Smites use Spellslots
        self.smite_initiated = [False, False, False, False, False]      #  lv1, lv2, lv3, ... lv5 (0 = no smite, 1 = smite)
        #Aura of Protection
        self.knows_aura_of_protection = False
        if 'AuraOfProtection' in self.other_abilities:
            self.knows_aura_of_protection = True
            #Is implemented in the do_your_turn function via area of effect chooser

        #Inspiration
        if 'Inspiration' in self.other_abilities:
            self.knows_inspiration = True
            self.inspiration_die = int(data['Inspiration'])
        else:
            self.knows_inspiration = False
            self.inspiration_die = 0
        self.inspired = 0   #here the amount a target is inspired
        self.inspiration_counter =  self.modifier[5]    #for baric inspiration char mod
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
        self.wild_shape_HP = 0                    #temp HP of wild shape
        self.wild_shape_uses = 2
        self.wild_shape_name = ' '

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
        self.cast = 1 #if a spell is cast, cast = 0
        self.is_concentrating = False
        self.uses_offhand = False

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
                self.DM.say('(with inspiration), ', end= '')
        return d20

#---------------------Character State Handling----------------
    def unconscious(self):
        self.DM.say(self.name + ' is unconscious ', end='')
        self.CHP = 0
        self.state = 0   # now unconscious
        self.unconscious_counter += 1 #for statistics

        #if u get uncounscious:
        self.end_rage()
        self.break_concentration()
        if self.knows_aura_of_protection:
            self.end_aura_of_protection()

        if self.is_hasted():
            self.break_haste()
        if self.is_entangled():
            self.break_entangle()
        if self.is_hexed():
            self.switch_hex()
        if self.is_a_conjured_animal:
            self.end_conjuration()
        self.DM.say('\n', end='')

        if self.team == 1: #this is for Monsters
            self.state = -1
    
    def get_conscious(self):
        self.DM.say(self.name + ' regains consciousness')
        self.state = 1
        self.heal_counter = 0
        self.death_counter = 0

    def death(self):
        self.CHP = 0
        self.state = -1
        #if u die:
        self.end_rage()
        self.break_concentration()
        if self.knows_aura_of_protection:
            self.end_aura_of_protection()


        if self.is_hasted():
            self.break_haste()
        if self.is_entangled():
            self.break_entangle()
        if self.is_hexed():
            self.switch_hex()
        if self.is_a_conjured_animal:
            self.end_conjuration()

    def check_uncanny_dodge(self, dmg):
        #-----------Uncanny Dodge
        if self.knows_uncanny_dodge:
            if dmg.abs_amount() > 0 and self.reaction == 1 and self.state == 1: #uncanny dodge condition
                dmg.multiply(1/2) #Uncanny Dodge halfs all dmg
                self.reaction = 0
                self.DM.say('with Uncanny Dodge, ', end='')

    def check_new_state(self, was_ranged):
        #State Handling after Changing CHP

        #----------State Handling Unconscious
        if self.state == 0:         #if the player is dying
            if self.CHP > 0:           #was healed over 0
                self.get_conscious()
            if self.CHP <0:
                if self.CHP < -1*self.HP:
                    self.death()
                    self.DM.say(str(self.name) + ' died due to the damage ')
                else:
                    self.CHP = 0
                    if was_ranged:
                        self.death_counter += 1
                    else: #melee is auto crit
                        self.death_counter += 2
                    if self.death_counter >= 3:
                        self.death()
                        self.DM.say(str(self.name) + ' was attacked and died')
                    else:
                        self.DM.say(str(self.name) + ' death saves at ' + self.StringDeathCounter())

        #----------State handling alive
        if self.state == 1:                    #the following is if the player was alive before
            if self.CHP < 0-self.HP:              #if more then -HP dmg, character dies
                self.death()
                self.DM.say(str(self.name) + ' died due to the damage ')
            if self.CHP <= 0 and self.state != -1:   #if below 0 and not dead, state dying 
                self.unconscious()

    def changeCHP(self, Dmg, attacker, was_ranged):
        self.check_uncanny_dodge(Dmg)

        damage = Dmg.calculate_for(self) #call dmg class, does the Resistances 
        #This calculates the total dmg with respect to resistances

        #-----------Statistics
        if damage > 0:
            attacker.dmg_dealed += damage
            if attacker.is_a_conjured_animal:
                attacker.conjurer.dmg_dealed += damage
            attacker.last_used_DMG_Type = Dmg.damage_type()
        elif damage < 0:
            attacker.heal_given -= damage

        #---------Damage Deal
        AgathysDmg = dmg() #0 dmg
        if damage > 0:                 #if damage, it will be checkt if wild shape HP are still there
            if self.is_a_turned_undead:
                self.end_turned_undead()
            self.make_concentration_check(damage) #Make Concentration Check for the dmg
            if self.wild_shape_HP > 0:
                self.change_wild_shape_HP(damage, attacker, was_ranged)
                #Not checking resistances anymore, already done 
            else:
                if self.THP > 0:     #Temporary Hitpoints
                    AgathysDmg = self.check_for_armor_of_agathys() #returns the agathys dmg
                    if damage < self.THP: #Still THP
                        self.THP -= damage
                        self.DM.say(self.name + ' takes DMG: ' + Dmg.text() + ' now: ' + str(round(self.CHP,2)) + ' + ' + str(round(self.THP,2)) + ' temporary HP')
                        damage = 0
                    else: #THP gone
                        damage = damage - self.THP #substract THP
                        self.THP = 0
                        self.DM.say('temporaray HP empty, ', end='')

                #Change CHP
                if damage > 0: #If still damage left
                    self.CHP -= damage
                    self.DM.say(self.name + ' takes DMG: ' + Dmg.text() + ' now at: ' + str(round(self.CHP,2)))

        #---------Armor of Agathys 
        if AgathysDmg.abs_amount() > 0 and was_ranged == False:
            self.DM.say(attacker.name + ' is harmed by the Armor of Agathys')
            attacker.changeCHP(AgathysDmg, self, was_ranged=False)

        #---------Heal
        if damage < 0:               #neg. damage is heal
            if self.state == -1:
                self.DM.say('This is stupid, dead cant be healed')
                quit()
            if abs(self.HP - self.CHP) >= abs(damage):
                self.CHP -= damage    
            else:                     #if more heal then HP, only fill HP up
                damage = -1*(self.HP - self.CHP)
                self.CHP -= damage
            self.DM.say(str(self.name) + ' is healed for: ' + str(-damage))

        self.check_new_state(was_ranged)

    def change_wild_shape_HP(self, damage, attacker, was_ranged):
        if damage < self.wild_shape_HP:     #damage hits the wild shape
            self.wild_shape_HP -= damage
            self.DM.say(str(self.name) + ' takes damage in wild shape: ' + str(round(damage,2)) + ' now: ' + str(round(self.wild_shape_HP,2)))
        else:                  #wild shape breakes, overhang goes to changeCHP
            overhang_damage = abs(self.wild_shape_HP - damage)
            
            #reshape after critical damage
            self.wild_shape_drop()  #function that resets the players stats
            self.DM.say(str(self.name) + ' wild shape breaks')
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
        self.DM.say(self.name + ' gains ' + str(newTHP) + ' temporary HP')

    def stand_up(self):
        rules = [self.prone == 1, self.restrained == 0]
        errors = [self.name + ' tried to stand up but is not prone', 
                self.name + ' tried to stand up, but is restrained']
        ifstatements(rules, errors, self.DM).check()
        self.prone = 0
        self.DM.say(self.name + ' stood up to end prone')

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
        if self.restrained == 1:
            Score = Score*0.9
        if self.blinded == 1:
            Score = Score*0.9
        if self.prone == 1:
            Score = Score*0.95
        if self.is_hasted() == 1:
            Score = Score*1.1
        return Score

    def end_conjuration(self):
        #This function is called if this entity is a conjured animal and should vanish
        if self.is_a_conjured_animal:
            self.DM.say(' ' + self.name + ' vanishes ', end='')
            self.state = -1
            if self.conjurer == False:
                self.DM.say(self.name + ' should have a conjurer, but doesnt')
                quit()
            else:
                if self.conjurer.is_concentrating and self.conjurer.has_animals_conjured:
                    #The conjurer has not lost concentration but this entity simply died
                    #Now check if it is maybe the last of the conjured animals
                    ConjuredRelations = [x for x in self.DM.relations if x.type == 'ConjuredAnimal' and x.initiator == self.conjurer]
                    #This is a list with all Relations of the players conjurer that are ConjuredAnimasl
                    for x in ConjuredRelations:
                        if x.target == self: self.DM.resolve(x) #resolve own relation
                    ConjuredRelations = [x for x in self.DM.relations if x.type == 'ConjuredAnimal' and x.initiator == self.conjurer]
                    if len(ConjuredRelations) == 0: #The conjurer is now free of conjurations
                        self.conjurer.is_concentrating = False
                        self.conjurer.has_animals_conjured = False
                        self.DM.say(self.conjurer.name + ' is no longer concentrated')
        else:
            self.DM.say(self.name + ' cant vanish, is not a conjured animal')
            quit()

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

    def check_advantage(self, which_save):
        saves_adv_dis = [0,0,0,0,0,0] #calculate all factors to saves:
        if self.restrained == 1:  #disadvantage in dex if restrained
            saves_adv_dis[1] -= 1
            self.DM.say('restrained, ', end='')
        if self.raged == 1:   #str ad if raged
            saves_adv_dis[0] += 1
            self.DM.say('raging, ', end='')
        if self.is_hasted():
            saves_adv_dis[1] += 1
            self.DM.say('hasted, ', end='')
        if self.is_hexed():
            HexType = int(random()*2 + 1) #random hex disad at Str, Dex or Con
            HexText = ['Str ', 'Dex ', 'Con ']
            self.DM.say('hexed ' + HexText[HexType] + ', ', end='')
            saves_adv_dis[HexType] -= 1 #one rand disad 
        return saves_adv_dis[which_save]

    def make_save(self, which_save):          #0-Str, 1-Dex, ...
    #how to disadvantage and advantage here !!!
        self.DM.say(str(self.name) + ' is ', end='')
        Advantage = self.check_advantage(which_save)
        AuraBonus = self.protection_aura()
        if AuraBonus > 0:
            self.DM.say('in protection aura, ', end='')
        if Advantage < 0:
            d20_roll = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('in disadvantage doing the save: ' + str(d20_roll), end='')
        elif Advantage > 0:
            d20_roll = self.rollD20(advantage_disadvantage=1)
            self.DM.say('in advantage doing the save: ' + str(d20_roll), end='')
        else:
            d20_roll = self.rollD20(advantage_disadvantage=0)
            self.DM.say('doing the save: ' + str(d20_roll), end='')

        result = d20_roll + self.modifier[which_save] + AuraBonus #calc modifier
        save_text = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        if save_text[which_save] in self.saves_prof: #Save Proficiency
            result += self.proficiency
        self.DM.say(' + ' + str(int(result - d20_roll)))
        return result

    def make_death_save(self):
        d20_roll = int(random()*20 + 1)
        AuraBonus = self.protection_aura()
        if AuraBonus > 0:
            d20_roll += AuraBonus
            self.DM.say('Aura of protection +' + str(int(AuraBonus)) + ' : ', end= '')
        self.DM.say(self.StringDeathCheck(d20_roll))
        if self.death_counter >= 3:
            self.death()
            self.DM.say(str(self.name) + ' failed death save and died')
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

#---------------Concentration and Concentration Spells-----------
    def make_concentration_check(self, damage):
        if self.is_concentrating:
            save_res = self.make_save(2)
            if save_res >= damage/2 and save_res >= 10:   #concentration is con save
                return 
            else:
                self.break_concentration()
                return 
        else:
            return

    def break_concentration(self):
        player_was_concentrating = self.is_entangling() or self.is_hasting() or self.is_hexing() or self.has_animals_conjured
        if player_was_concentrating:
            self.DM.say(self.name + ' lost concentration, ', end='')

        self.is_concentrating = False  #no longer concentrated
        #break entangled
        if self.is_entangling():
            relations_to_resolve = [x for x in self.DM.relations if x.type == 'Entangle' and x.initiator == self]
            for x in relations_to_resolve:
                #resolve all entangle relations 
                x.target.break_entangle()
        #break Haste
        if self.is_hasting():
            #Here it is important to not do it in a loop, as the break haste removes the relation from the list and this can mess with the loop
            relations_to_resolve = [x for x in self.DM.relations if x.type == 'Haste' and x.initiator == self]
            for x in relations_to_resolve:
                #resolve all initiated hastes by this player
                x.target.break_haste()
        #Break Hex
        if self.is_hexing():
            relations_to_resolve = [x for x in self.DM.relations if x.type == 'Hex' and x.initiator == self]
            for x in relations_to_resolve:
                #resolve all Hex of this player
                self.DM.resolve(x)
                self.DM.say('hex is lifted from ' + x.target.name + ', ', end='')
        #Break Conjured Animals
        if self.has_animals_conjured:
            self.break_conjured_animals()
        
        if player_was_concentrating:
            self.DM.say('\n', end= '')

    def break_haste(self):
        if self.is_hasted():
            #First find the haste realtion
            for x in self.DM.relations:
                if x.type == 'Haste' and x.target == self:
                    HasteRelation = x
                    break
            Haster = HasteRelation.initiator
            #Selfs Haste wares of
            self.DM.say(self.name + ' Haste wares of, ', end='')
            self.DM.resolve(HasteRelation)
            #If not hasting anymore, because it was the only haste, return concentration
            if Haster.is_hasting() == False and Haster.is_concentrating:
                #If this function is called via the break concentration, concentration is already 0
                self.DM.say(Haster.name + ' no longer concentrated, ', end='')
                Haster.is_concentrating = False

            #reset hast counter
            self.haste_round_counter = 0

    def is_hasted(self):
        #advantage in Dex saves in make_save function
        #additional Attack in start_of_turn_function
        #AC added in start_of_turn_function
        #This function checks if the player is hasted and if so, returns True
        #To do so it checks the relations of the DM for itself beeing hasted
        for x in self.DM.relations:
            if x.type == 'Haste' and x.target == self:
                return True
        return False #not hasted
    
    def is_hasting(self):
        #Returns True if self is hasting anyone
        for x in self.DM.relations:
            if x.type == 'Haste' and x.initiator == self:
                return True
        return False

    def break_entangle(self):
        if self.is_entangled():
            #Find the entangle raltion
            for x in self.DM.relations:
                if x.type == 'Entangle' and x.target == self:
                    EntangleRelation = x
                    break
            Entangler = EntangleRelation.initiator
            #Self Entangle Breaks
            self.DM.say(self.name + ' breaks Entangle, ', end='')
            self.DM.resolve(EntangleRelation)
            self.restrained = 0 #no longer restrained
            #If the Caster is not entangling anymore, because was only entangle, break concentration
            if Entangler.is_entangling() == False and Entangler.is_concentrating:
                #If this function is called via the break concentration, concentration is already 0
                self.DM.say(Entangler.name + ' no longer concentrated, ', end='')
                Entangler.is_concentrating = False

    def try_break_entangle(self):  #makes an effort to break entangle
        rules = [self.is_entangled(), self.action != 0]
        errors = [self.name + ' tried to break entangle but is not entangled',
                self.name + ' tried to break entangle but has no action left']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.name + ' tries to break entangle: ', end = '')
        result = self.make_check(0)
        for x in self.DM.relations:
            if x.type == 'Entangle' and x.target == self:
                Entangler = x.initiator
                break
        self.DM.say(str(result) + '/' + self.Entangler.spell_dc)
        if result < self.Entangler.spell_dc:
            self.action = 0
            return
        else:
            self.action = 0
            self.break_entangle()
            return

    def is_entangled(self):
        #This function checks if the player is entangled and if so, returns True
        #To do so it checks the relations of the DM for itself beeing hasted
        for x in self.DM.relations:
            if x.type == 'Entangle' and x.target == self:
                return True
        return False

    def is_entangling(self):
        #Returns True if self is entangling anyone
        for x in self.DM.relations:
            if x.type == 'Entangle' and x.initiator == self:
                return True
        return False

    def switch_hex(self):
        #This function is called if a hexed player goes unconscious or dead
        #It is not called if a player loses concentration and hex is broken
        HexRelations = [x for x in self.DM.relations if x.type == 'Hex' and x.target == self]
        #This is a list of all hex targeted at this player, which is now unconscious or dead
        for x in HexRelations:
            x.initiator.can_choose_new_hex = True #This player can now choose a new hex on turn
            self.DM.resolve(x) #Then resolve the old hex
            self.DM.say('hex of ' + x.initiator.name + ' is unbound, ', end='')

    def is_hexed(self):
        for x in self.DM.relations:
            if x.type == 'Hex' and x.target == self:
                return True
        return False
    
    def is_hexing(self):
        for x in self.DM.relations:
            if x.type == 'Hex' and x.initiator == self:
                return True
        return False

    def break_armor_of_agathys(self):
        if self.has_armor_of_agathys and self.THP > 0:
            self.has_armor_of_agathys = False
            self.THP = 0
            self.agathys_dmg = 0
            self.DM.say(self.name + ' Armor of Agathys breaks, ')
        else:
            self.DM.say(self.name + ' Armor of Agathys broke without having one')
            quit()

    def break_spiritual_weapon(self):
        if self.has_spiritual_weapon:
            self.has_spiritual_weapon = False
            self.SpiritualWeaponCounter = 0 #reset counter
            self.SpiritualWeaponDmg = 0
            self.DM.say('Spiritual Weapon of ' + self.name + ' vanishes, ')
    
    def break_conjured_animals(self):
        #This function is called if all the conjured animals of the player should vanish
        #Is called in break concentration
        if self.has_animals_conjured:
            self.is_concentrating = False
            self.has_animals_conjured = False
            AnimalRelations = [x for x in self.DM.relations if x.type == 'ConjuredAnimal' and x.initiator == self]
            for x in AnimalRelations:
                x.target.death() #The Animal vanishes
                self.DM.resolve(x)

    def end_guiding_bolt(self):
        Relations = [x for x in self.DM.relations if x.type == 'GuidingBolt' and x.initiator == self and x.InitRound == self.DM.rounds_number - 1]
        #All Guding Bolt relations from this player from last round
        BoltedPlayer = [x.target for x in Relations]
        #Resolve all Guided Bolts with this player as initiator from last round
        for x in Relations:
            self.DM.say('For ' + x.target.name + ' guiding bolt ends')
            self.DM.resolve(x)
        #Check is the player are now no longer guided bolted
        RemainingRelations = [x for x in self.DM.relations if x.type == 'GuidingBolt']
        for x in BoltedPlayer:
            if x not in [y.target for y in RemainingRelations]:
                #No longer bolted
                x.is_guiding_bolted = False
        #Check if self is still guiding bolting
        if self not in [x.initiator for x in RemainingRelations]:
            self.used_guiding_bolt = False

    def end_turned_undead(self):
        self.is_a_turned_undead == False #no longer turned
        self.turned_undead_round_counter = 0
        self.DM.say(self.name + ' is no longer turned')

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
            self.DM.say(self.name + ' uses cunning action to dash to ' + target.name)
            is_BADash = True 
        elif self.knows_eagle_totem and self.bonus_action == 1:
            self.DM.say(self.name + ' uses eagle totem to dash to ' + target.name)
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
            self.DM.say(self.name + ' uses dash to get to ' + target.name)
        else:
            self.DM.say(self.name + ' tried to dash, but has no action left')
            quit()

    def move_position(self):
        #This function will be called, if the player hat no target in reach last turn
        if self.position == 1: #if you are usually in mid go front 
            self.DM.say(self.name + ' moves to the front line')
            self.position = 0
            self.action = 0 #took the action

#-------------------Attack Handling----------------------
    def make_attack_check(self, target, fight, is_off_hand):
        if self.action == 0 and self.is_attacking == False and is_off_hand == False:
            self.DM.say(self.name + ' tried to attack, but has no action left')
            quit()
        elif self.bonus_action == 0 and is_off_hand:
            self.DM.say(self.name + ' tried to offhand attack, but has no bonus attacks left')
            quit()
        elif is_off_hand and self.is_attacking == False:
            self.DM.say(self.name + ' tried to offhand attack, but has not attacked with action')
            quit()
        elif self.attack_counter < 1 and is_off_hand == False:
            self.DM.say(self.name + ' tried to attack, but has no attacks left')
            quit()
        elif self.state != 1:
            self.DM.say(self.name +' treid to attack but is not conscious')
            quit()
        #check if target is in range
        elif target not in self.enemies_reachable_sort(fight):
            self.DM.say(self.name + ' tried to attack, but ' + target.name + ' is out of reach')
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
            self.DM.say(self.name + ' tried to attack, but ' + target.name + ' is out of reach, this is weird here, check enemies_rechable_sort')
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
            self.uses_offhand = True #will be disabled by attack funtion
            self.attack(target, is_ranged, other_dmg=self.offhand_dmg)
        else:
            self.action = 0 #if at least one attack, action = 0
            self.is_attacking = True #uses action to attack
            self.attack_counter -= 1 #Lower the attack counter 
            self.attack(target, is_ranged)

    def provoke_opportunit_attack(self, target):
        if self.no_attack_of_opportunity_yet: #only one per turn 
            self.DM.say(self.name + ' has provoked an attack of opportunity:')
            self.no_attack_of_opportunity_yet = False
            target.AI.do_opportunity_attack(self)
            if self.state != 1: return False
            else: return True
        else: return True

    def make_attack_roll(self, target, is_ranged, is_opportunity_attack):
        #calculate all effects that might influence Disad or Advantage
        advantage_disadvantage = 0
        if target.state == 0:
            advantage_disadvantage += 1 #advantage against unconscious
            self.DM.say(target.name + ' unconscious, ',end='')
        if target.reckless == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' reckless, ',end='')
        if self.reckless == 1:
            advantage_disadvantage += 1    
            self.DM.say(self.name + ' reckless, ',end='')
        if target.knows_eagle_totem and is_opportunity_attack:
            advantage_disadvantage -= 1
            #disadvantage for opp. att against eagle totem
            self.DM.say('eagle totem, ',end='')
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
            if is_ranged:
                advantage_disadvantage -=1 #disad for ranged against prone
            else:
                advantage_disadvantage += 1
            self.DM.say(target.name + ' prone, ',end='')
        if self.prone == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' prone, ',end='')
        if self.knows_assassinate:
            if self.DM.rounds_number == 1 and self.initiative > target.initiative:
                #Assassins have advantage against player that havnt had a turn
                advantage_disadvantage += 1
                self.DM.say(self.name + ' assassinte, ', end='')
        if target.has_wolf_mark and is_ranged == False:
            self.DM.say(target.name + ' wolf totem, ', end='')
            advantage_disadvantage += 1
        if target.is_guiding_bolted:
            self.DM.say('guiding bolt, ', end='')
            advantage_disadvantage += 1

        #Roll the Die to hit
        if advantage_disadvantage > 0:
            d20 = self.rollD20(advantage_disadvantage=1)
            self.DM.say('\nAdvantage: ', end='')
        elif advantage_disadvantage < 0:
            d20 = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('\nDisadvantage: ', end='')
        else:
            d20 = self.rollD20(advantage_disadvantage=0)
            self.DM.say('\n', end='')
        return d20 , advantage_disadvantage

    def check_smite(self, Dmg, is_ranged):
        if is_ranged == False and self.knows_smite:  #smite only on melee
            for i in range(0, len(self.smite_initiated)):
                if self.smite_initiated[i]:             #smite initiated?
                    if self.spell_slot_counter[i] > 0:
                        smitedmg = 4.5*(i+2) #i=0 -> lv1 -> 2d8
                        Dmg.add(smitedmg, 'radiant')
                        self.spell_slot_counter[i] -= 1
                        self.smite_initiated[i] = 0
                        self.DM.say('\n' + self.name + ' uses ' + str(i + 1) + '. lv Smite: +' + str(smitedmg), end='')

    def check_sneak_attack(self, Dmg, advantage_disadvantage):
        if self.sneak_attack_dmg > 0:    #Sneak Attack 
            if self.sneak_attack_counter == 1 and advantage_disadvantage >= 0: #not in disadv.
                Dmg.add(self.sneak_attack_dmg, self.damage_type)
                self.DM.say('\n' + self.name + " Sneak Attack: +" + str(self.sneak_attack_dmg), end='')
                if self.wailsfromthegrave == 1 and self.wailsfromthegrave_counter > 0:  #if sneak attack hits and wails from the grave is active
                    Dmg.add(self.sneak_attack_dmg/2, 'necrotic')
                    self.wailsfromthegrave_counter -= 1
                    self.DM.say(' and ' + str(self.sneak_attack_dmg/2) + ' wails from the grave', end='')
                self.sneak_attack_counter = 0

    def check_combat_inspiration(self, Dmg, other_dmg):
        if self.is_combat_inspired and self.inspired > 0 and other_dmg == False:
            #Works only for weapon dmg, so other_dmg == False
            Dmg.add(self.inspired, self.damage_type)
            self.DM.say('\n' + self.name + ' uses combat inspiration: +' + str(self.inspired), end='')
            self.inspired = 0
            self.is_combat_inspired = False

    def check_hex(self, Dmg, target):
        for x in self.DM.relations:
            if x.type == 'Hex' and x.target == target and x.initiator == self:
                Dmg.add(3.5, 'necrotic')
                self.DM.say('\n' + target.name + ' was cursed with a hex', end='')
                return

    def check_great_weapon_fighting(self, Dmg, is_ranged, other_dmg):
        rules = [self.knows_great_weapon_fighting,
                self.offhand_dmg == 0,  #no offhand
                is_ranged == False,     #no range
                other_dmg == False]   #no spells or stuff
        if all(rules):
            self.DM.say('\n' + self.name + ' uses great weapon fighting', end='')
            Dmg.multiply(1.15) #no 1,2 in dmg roll, better dmg on attack

    def attack(self, target, is_ranged, other_dmg = False, damage_type = False, tohit = False, is_opportunity_attack = False):
    #this is the attack funktion of a player attacking a target with a normak attack
    #if another type of dmg is passed, it will be used, otherwise the player.dmg_type is used
    #if no dmg is passed, the normal entitiy dmg is used
    #is_ranged tells the function if it is a meely or ranged attack
        #this ensures that for a normal attack the dmg type of the entity is used
        if damage_type == False: damage_type = self.damage_type
        #if no other dmg is passed, use that of the player
        if other_dmg == False: Dmg = dmg(self.dmg, damage_type)
        else: Dmg = dmg(other_dmg, damage_type)

        #check if other to hit is passsed, like for a spell
        if tohit == False: tohit = self.tohit

        self.DM.say(self.name + " -> " + target.name + ', ', end='')

        if is_ranged:
            self.DM.say('ranged, ', end='')
        else:
            self.DM.say('melee, ', end='')
        
        if self.uses_offhand:
            self.DM.say('off hand, ', end='')
            self.uses_offhand == False

        d20, advantage_disadvantage = self.make_attack_roll(target, is_ranged, is_opportunity_attack)
                
        if d20 == 20 or (self.knows_improved_critical and d20 == 19):
            is_crit = True
        else:
            is_crit = False

        #Does the target AI wants to use Reaction to cast shield? 
        if target.state == 1: #is still alive?
            if target.reaction == 1 and target.SpellBook['Shield'].is_known:
                target.AI.want_to_cast_shield(self, Dmg)  #call the target AI for shield

        Modifier = 0 # Will go add to the attack to hit
        ACBonus = 0

        if target.is_combat_inspired and target.inspired > 0:
            if d20 + self.tohit > target.AC:
                self.DM.say('combat inspired AC (' + str(target.inspired) + '), ', end='')
                ACBonus += target.inspired
                self.inspired = 0
                self.is_combat_inspired = False
        
        if target.knows_cutting_words and target.inspiration_counter > 0:
            if d20 + self.tohit > target.AC:
                self.DM.say(target.name + ' uses cutting word, ', end='')
                Modifier += -target.inspiration_die
                target.reaction = 0 #uses reaction
        
        if self.knows_archery and is_ranged:
            self.DM.say(self.name + ' uses Archery, ', end='')
            Modifier += 2 #Archery

        if d20 + tohit + Modifier >= target.AC + ACBonus or is_crit:       #Does it hit
            if is_crit:
                self.DM.say('Critical Hit!, ',end='')
            self.DM.say('hit: ' + str(d20) + '+' + str(tohit) + '+' + str(Modifier) + '/' + str(target.AC) +'+' + str(ACBonus), end= '')

        #Smite
            self.check_smite(Dmg, is_ranged)
        #Snackattack
            self.check_sneak_attack(Dmg, advantage_disadvantage)
        #Combat Inspiration 
            self.check_combat_inspiration(Dmg, other_dmg)
        #Hex
            self.check_hex(Dmg, target)
        #GreatWeapon
            self.check_great_weapon_fighting(Dmg, is_ranged, other_dmg)
        #Critical
            if is_crit: Dmg.multiply(1.8)
        #add rage dmg
            if self.raged == True and is_ranged == False: #Rage dmg only on melee
                Dmg.add(self.rage_dmg, self.damage_type)
        #Interseption
            if target.interseption_amount > 0:
                self.DM.say('Attack was intersepted: -' + str(self.interseption_amount))
                Dmg.substract(target.interseption_amount)
        else:
            Dmg = dmg(amount=0)   #0 dmg
            self.DM.say(str(d20) + '+' + str(tohit) + '+' + str(Modifier) + '/' + str(target.AC) +'+' + str(ACBonus) + ' miss', end= '')
        self.DM.say('\n', end='')
        target.changeCHP(Dmg, self, is_ranged)  #actually change HP
        self.reset_all_smites()
        target.last_attacker = self
        if self.knows_wolf_totem:
            target.has_wolf_mark = True #marked with wolf totem
        return Dmg.abs_amount()

#-------------------Wild Shape---------------
    def wild_shape(self, ShapeIndex):
        #ShapeIndex is Index in BeastFroms from entity __init__
        #Wild shape needs an action or a bonus action if you know combat_wild_shape
        player_can_wild_shape = False
        if self.wild_shape_uses > 0 and self.wild_shape_HP == 0 and self.knows_wild_shape and self.DruidCR >= self.BeastForms[ShapeIndex]['Level']:
                if self.bonus_action == 1 and self.knows_combat_wild_shape:
                    player_can_wild_shape = True
                    self.bonus_action = 0
                elif self.action == 1:
                    player_can_wild_shape = True
                    self.action = 0

        if player_can_wild_shape:
            #A Shape form is choosen and then initiated as entity to use their stats
            ShapeName = self.BeastForms[ShapeIndex]['Name']
            NewShape = entity(ShapeName, self.team, self.DM, archive=True)
        #Wild Shape Properties
            self.name = self.orignial_name + '(' + ShapeName + ')'
            self.shape_AC = NewShape.AC
            self.wild_shape_HP = NewShape.HP
            self.tohit = NewShape.tohit
            self.attacks = NewShape.attacks
            self.type = NewShape.type
            #number auf Attacks
            self.attack_counter = self.attacks
            self.dmg = NewShape.dmg
            self.wild_shape_name = ShapeName

            #new modifier
            self.stats_list = NewShape.stats_list
            self.modifier = NewShape.modifier

            #new dmg types
            self.damage_type = NewShape.damage_type
            self.damage_resistances = NewShape.damage_resistances
            self.damage_immunity = NewShape.damage_immunity
            self.damage_vulnerability = NewShape.damage_vulnerability

            self.DM.say(self.name + ' goes into wild shape ' + ShapeName)
            self.wild_shape_uses -= 1

        #Cant go into wild shape
        else:
            if self.wild_shape_uses < 1:
                self.DM.say(self.name + ' cant go into wild shape anymore')
            elif self.action == 0:
                self.DM.say(self.name + ' cant go into wild shape without an action left')
            elif self.wild_shape_HP != 0:
                self.DM.say(self.name + ' cant go into wild shape while in wildshape')
            elif self.knows_wild_shape == False:
                self.DM.say(self.name + ' tried to go into wild shape without knowing how')
                quit()
            elif self.DruidCR < self.BeastForms[ShapeIndex]['Level']:
                self.DM.say(self.name + ' tried to go into a too high CR shape: ' + str(self.BeastForms[ShapeIndex]['Level']))
                quit()
            else:
                self.DM.say('ERROR Wild Shape')
            quit()

    def wild_shape_drop(self):
        if self.wild_shape_HP != 0:
            self.name = self.orignial_name
            self.shape_AC = self.base_AC  #set the shape AC of Entity back to base AC (for more see __init__)
            self.wild_shape_HP = 0
            self.tohit = self.base_tohit
            self.attacks = self.base_attacks
            self.attack_counter = self.attacks
            self.dmg = self.base_dmg
            self.type = self.base_type
            
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
                quit()
            else:
                self.DM.say(self.name + ' tried to drop wild shape, but has no bonus action left')
                quit()

    def use_combat_wild_shape_heal(self, spell_level=1):
        rules = [self.knows_combat_wild_shape,
                self.wild_shape_HP > 0,
                self.spell_slot_counter[spell_level -1] > 0,
                self.bonus_action == 1]
        errors = [self.name + ' tried to heal by combat wild shape but does not know how',
                self.name + ' tried to heal by combat wild shape but is not in wild shape',
                self.name + ' tried to heal by combat wild shape but has no bonus action left',
                self.name + ' tried to heal by combat wild shape with a ' + str(spell_level) + 'lv spell slot but has non left']
        ifstatements(rules, errors, self.DM).check()

        heal = spell_level*4.5
        self.changeCHP(dmg(-heal, 'heal'), self, was_ranged=False)
        self.spell_slot_counter[spell_level -1] -= 1
        self.bonus_action -= 1

#------------------Special Abilities-----------------
    def rackless_attack(self):
        if self.knows_reckless_attack:
            self.reckless = 1
            self.DM.say(self.name + ' uses reckless Attack')
        else:
            self.DM.say(self.name + ' tried to reckless Attack without knowing it')
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
            self.DM.say(rage_text + ' rage')
        else:
            if self.bonus_action == 0:
                self.DM.say(self.name + ' tried to rage, but has no bonus action')
                quit()
            elif self.knows_rage == False:
                self.DM.say(self.name + ' tried to rage but cant')
                quit()

    def use_frenzy_attack(self):
        if self.is_in_frenzy and self.bonus_action == 1:
            self.DM.say(self.name + ' uses the bonus action for a frenzy attack')
            self.attack_counter += 1  #additional attack
            self.bonus_action = 0
        elif self.bonus_action == 0:
            self.DM.say(self.name + ' tried to use frenzy attack without a bonus action')
            quit()
        elif self.is_in_frenzy == False:
            self.DM.say(self.name + ' tried to use franzy attack but is not in a frenzy rage')
            quit()

    def end_rage(self):
        if self.raged == 1:
            self.raged = 0
            self.update_additional_resistances()
            self.is_in_frenzy = False
            self.DM.say(self.name + ' falls out of rage, ', end= '')

    def inspire(self, target):
        if self.bonus_action == 0:  #needs a bonus action
            self.DM.say(self.name + ' tried to use bardic inspiration but has no bonus action left')
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
                self.DM.say(self.name + CombatInspirationText + ' inspired ' + str(target.name) + ' with awesomeness')
            else:
                self.DM.say(self.name + ' tried to use bardic inspiration but has none left')
                quit()

    def use_lay_on_hands(self, target, heal):
        if self.action == 0:
            self.DM.say(self.name + ' tried to lay on hands, but has no action left')
            quit()
        elif heal <= 0:
            self.DM.say('Lay on Hands was called with a negative heal')
            quit()
        elif self.lay_on_hands_counter <= 0:
            self.DM.say(self.name + ' tried to lay on hands, but has no points left')
            quit()
        else:
            if self.lay_on_hands_counter > heal:
                self.lay_on_hands_counter -= heal
            elif self.lay_on_hands_counter > 0:
                heal = self.lay_on_hands_counter
                self.lay_on_hands_counter = 0
            self.action = 0
            self.DM.say(self.name + ' uses lay on hands')
            target.changeCHP(dmg(-1*heal, 'heal'), self, False)

    def initiate_smite(self, smite_level= 1):
        if self.knows_smite and self.spell_slot_counter[smite_level - 1]>0:
            self.smite_initiated[smite_level-1] = True
        elif self.knows_smite == False:
            self.DM.say(self.name + ' tried to initiate smite without knowing it')
            quit()
        else:
            self.DM.say(self.name + ' tried to initiate smite without spellslots')
            quit()

    def reset_all_smites(self):
        self.smite_initiated = [False, False, False, False, False]

    def use_empowered_spell(self):
        rules = [self.knows_empowered_spell, self.sorcery_points > 0, self.empowered_spell==False]
        errors= [
            self.name + ' tried to use Empowered Spell without knowing it',
            self.name + ' tried to use empowered Spell, but has no Sorcery Points left',
            self.name + ' tried to use empowered spell, but has already used it']
        ifstatements(rules, errors, self.DM).check()

        self.sorcery_points -= 1
        self.empowered_spell = True
        self.DM.say(self.name + ' used Empowered Spell')

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
        self.DM.say(self.name + ' used action surge')

    def use_aura_of_protection(self, allies):
        #passiv ability, restes at end of turn for the targets
        if self.knows_aura_of_protection:
            if len(allies) > 5: #at least 4 ally
                targetnumber = int(random()*3 +1) #plus self
            elif len(allies) > 1:
                targetnumber = int(random() + 1)
            else:
                targetnumber = 0 #only self

            #Now choose random targtes plus self
            targets = []
            targets.append(self)
            AllyChoice = [ally for ally in allies if ally != self]
            shuffle(AllyChoice)
            for i in range(0,targetnumber):
                targets.append(AllyChoice[i])
            
            #Now apply Bonus
            for ally in targets:
                self.DM.relate(self, ally, 'AuraOfProtection')
        else: return

    def protection_aura(self):
        #Returns the current Bonus of all Auras of Protection in relation to self
        AuraBonus = 0
        for x in self.DM.relations:
            if x.type == 'AuraOfProtection' and x.target == self:
                PlayerBonus = x.initiator.modifier[5]
                if PlayerBonus < 1:
                    PlayerBonus = 1 #Aura of Protection min +1
                AuraBonus += PlayerBonus #Add to Bonus, Aura stacks
        return AuraBonus

    def end_aura_of_protection(self):
        #Resolve all your aura relations
        OldAuraRelations = [x for x in self.DM.relations if x.type == 'AuraOfProtection' and x.initiator == self]
        for x in OldAuraRelations: self.DM.resolve(x)
        if self.state != 1:
            self.DM.say(', aura of protection fades ', end='')

    def use_second_wind(self):
        rules = [self.bonus_action==1, self.knows_second_wind, self.has_used_second_wind == False]
        errors = [self.name + ' tried to use second wind without a BA',
            self.name + ' tried to use second wind without knowing it',
            self.name + ' tried to use second wind, but has used it already']
        ifstatements(rules, errors, self.DM).check()

        heal = 5.5 + self.level
        self.DM.say(self.name + ' used second wind')
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

        self.DM.say(self.name + ' uses turn undead:')
        for target in targets:
            if target.type == 'undead':
                if target.make_save(4) < self.spell_dc:
                    #Destroy undead
                    if target.level <= self.destroy_undead_CR:
                        self.DM.say(target.name + ' is destroyed')
                        target.death()
                    else:
                        target.is_a_turned_undead = True
                        self.DM.say(target.name + ' is turned')
            else:
                continue
        self.action = 0
        self.channel_divinity_counter -= 1 #used a channel divinity

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

#---------------Round Handling------------
    def start_of_turn(self):
        #Attention is called in the do the fighting function
        #ONLY called if player state = 1
        self.reckless = 0
        self.stepcounter=0 
        self.attack_counter = self.attacks #must be on start of turn, as in the round an attack of opportunity could have happened 
        self.AC = self.shape_AC  #reset AC to the AC of the shape (maybe wild shape)

        if self.knows_dragons_breath: #charge Dragons Breath
            if random() > 2/3:
                self.dragons_breath_is_charged = True
        if self.knows_spider_web: #charge Spider Web
            if random() > 2/3:
                self.spider_web_is_charged = True

        if self.is_hasted():#additional Hast attack
            self.attack_counter += 1
            self.AC += 2

        if self.is_a_turned_undead:
            self.action = 0
            self.attack_counter = 0
            self.bonus_action = 0
    
    def action_surge(self):
        self.attack_counter = self.attacks #You can do your attacks again
        self.action = 1      #You get one additional action
        self.cast = 1        #You can cast again in your new action

    def end_of_turn(self):    #resets all round counters
        self.bonus_action = 1
        if self.is_a_turned_undead == False:
            self.reaction = 1
        self.action = 1
        self.cast = 1
        self.sneak_attack_counter = 1
        self.no_attack_of_opportunity_yet = True
        self.action_surge_used = False
        self.uses_offhand = False
        self.is_attacking = False
        self.has_wolf_mark = False #reset totem of wolf mark


        #If you have not dashed this round, you should not have a dash target anymore
        if self.has_dashed_this_round == False:
            self.dash_target = False
        self.has_dashed_this_round = False #reset for next round

        self.reset_all_smites()

        if self.raged == True:
            self.rage_round_counter += 1 #another round of rage
            if self.rage_round_counter >= 10:
                self.end_rage()

        if self.is_hasted():        #for haste spell counter
            self.haste_round_counter += 1
            if self.haste_round_counter >= 10:  #if longer then 1min / 10 rounds, haste ends
                self.break_haste()
        
        if self.has_spiritual_weapon:
            self.SpiritualWeaponCounter += 1
            if self.SpiritualWeaponCounter >= 10:
                self.break_spiritual_weapon()
        
        if self.used_guiding_bolt:
            self.end_guiding_bolt()
        
        if self.is_a_turned_undead:
            self.turned_undead_round_counter += 1
            if self.turned_undead_round_counter >= 10:
                self.end_turned_undead()

        if self.interseption_amount != 0:
            self.interseption_amount = 0 #no longer in interseption

    def long_rest(self):       #resets everything to initial values
        self.name = self.orignial_name
        self.AC = self.base_AC
        self.shape_AC = self.base_AC
        self.dmg = self.base_dmg
        self.tohit = self.base_tohit
        self.attacks = self.base_attacks
        self.type = self.base_type

        for i in range(0, len(self.spell_slots)):
            self.spell_slot_counter[i] = self.spell_slots[i]

        self.reset_all_smites()
        self.DM.reset_relations()

        self.wailsfromthegrave_counter = self.proficiency
        self.sneak_attack_counter = 1
        self.reckless = 0
        self.raged = 0
        self.rage_round_counter = 0
        self.lay_on_hands_counter = self.lay_on_hands
        self.sorcery_points = self.sorcery_points_base
        self.action_surge_counter = self.action_surges
        self.action_surge_used = False
        self.has_used_second_wind = False

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False

        self.wild_shape_HP = 0
        self.wild_shape_uses = 2
        self.inspired = 0
        self.is_combat_inspired = False
        if self.knows_inspiration:
            self.inspiration_counter = self.modifier[5]
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

        self.modifier = self.base_modifier

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.cast = 1 #if a spell is cast, cast = 0
        self.is_concentrating = False

        self.restrained = 0             #will be ckeckt wenn attack/ed 
        self.prone = 0
        self.blinded = 0   

        self.dash_target = False
        self.has_dashed_this_round = False
        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0
        self.unconscious_counter = 0

        #Haste
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        self.can_choose_new_hex = False
        #Armor of Agathys
        self.has_armor_of_agathys = False
        self.agathys_dmg = 0
        #Spiritual Weapon
        self.has_spiritual_weapon = False
        self.SpiritualWeaponDmg = 0
        self.SpiritualWeaponCounter = 0
        #ConjureAnimals
        self.has_animals_conjured = False
        self.is_a_conjured_animal = False #Should be anyway
        self.conjurer = False #Should be anyway
        #Guiding Bolt
        self.is_guiding_bolted = False
        self.used_guiding_bolt = False
        #TurnUnded
        self.is_a_turned_undead = False
        self.turned_undead_round_counter = 0
        #Interseption
        self.interseption_amount = 0

        self.empowered_spell = False
        self.quickened_spell = False
    
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
                Dmg = dmg(20 + int(self.level*3.1), DMG_Type)
                DragonBreathDC = 12 + self.Con + int((self.level - 10)/3)  #Calculate the Dragons Breath DC 
                if save >= DragonBreathDC:
                    Dmg.multiply(1/2)
                target.changeCHP(Dmg, self, True)
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

        elif spell_name == 'Entangle':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = True
            self.is_cantrip = False
            self.is_twin_castable = True
            self.cast = self.cast_entangle
            self.score = self.score_entangle

        elif spell_name == 'BurningHands':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.spell_save_type = 1 #Dex
            self.cast = self.cast_burning_hands
            self.score = self.score_burning_hands

        elif spell_name == 'CureWounds':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_cure_wounds
            self.score = self.score_cure_wounds

        elif spell_name == 'HealingWord':
            self.spell_level = 1
            self.is_bonus_action_spell = True
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_healing_word
            self.score = self.score_healing_word

        elif spell_name == 'MagicMissile':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_magic_missile
            self.score = self.score_magic_missile

        elif spell_name == 'AganazzarsSorcher':
            self.spell_level = 2
            self.spell_save_type = 1 #Dex
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_aganazzars_sorcher
            self.score = self.score_aganazzars_scorcher

        elif spell_name == 'ScorchingRay':
            self.spell_level = 2
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_scorching_ray
            self.score = self.score_scorching_ray

        elif spell_name == 'Fireball':
            self.spell_level = 3
            self.spell_save_type = 1 #Dex
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.cast = self.cast_fireball
            self.score = self.score_fireball

        elif spell_name == 'Haste':
            self.spell_level = 3
            self.is_bonus_action_spell = False
            self.is_concentration_spell = True
            self.is_cantrip = False
            self.is_twin_castable = True 
            self.cast = self.cast_haste
            self.score = self.score_haste

        elif spell_name == 'Shield':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = False
            self.is_reaction_spell = True
            self.cast = self.cast_shield
            self.score = self.score_shield
        
        elif spell_name == 'EldritchBlast':
            self.spell_level = 0
            self.is_bonus_action_spell = False
            self.is_concentration_spell = False
            self.is_cantrip = True
            self.cast = self.cast_eldritch_blast
            self.score = self.score_eldritch_blast
       
        elif spell_name == 'Hex':
            self.spell_level = 1
            self.is_bonus_action_spell = True
            self.is_concentration_spell = True
            self.is_cantrip = False 
            self.is_twin_castable = False
            self.cast = self.cast_hex
            self.score = self.score_hex

        elif spell_name == 'ArmorOfAgathys':
            self.spell_level = 1
            self.is_bonus_action_spell = False
            self.is_cantrip = False
            self.is_concentration_spell = False
            self.is_twin_castable = False
            self.cast = self.cast_armor_of_agathys
            self.score = self.score_armor_of_agathys

        elif spell_name == 'FalseLife':
            self.spell_level = 1
            self.cast = self.cast_false_life
            self.score = self.score_false_life
        
        elif spell_name == 'SpiritualWeapon':
            self.spell_level = 2
            self.is_bonus_action_spell = True
            self.cast = self.cast_spiritual_weapon
            self.score = self.score_spiritual_weapon

        elif spell_name == 'Shatter':
            self.spell_level = 2
            self.spell_save_type = 2 #Con
            self.cast = self.cast_shatter
            self.score = self.score_shatter

        elif spell_name == 'ConjureAnimals':
            self.spell_level = 3
            self.is_concentration_spell = True
            self.cast = self.cast_conjure_animals
            self.score = self.score_conjure_animals

        elif spell_name == 'GuidingBolt':
            self.spell_level = 1
            self.is_twin_castable = True
            self.cast = self.cast_guiding_bolt
            self.score = self.score_guiding_bolt

    #any spell has a specific Spell cast function that does what the spell is supposed to do
    #To do so, the make_spell_check function makes sure, that everything is in order for the self.player to cast the spell
    #The make_action_check function checks if Action, Bonus Action is used
    #the spell class objects will be linked to the player casting it by self.player

    def make_spell_check(self, cast_level):
        rules = [self.is_known, 
                self.player.raged == 0,
                cast_level >= self.spell_level, 
                self.player.spell_slot_counter[cast_level -1] > 0,
                self.player.wild_shape_HP == 0,
                self.is_concentration_spell == False or self.player.is_concentrating==False]
        errors = [self.player.name + ' tried to cast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to cast ' + self.spell_name + ' but is raging',
                self.player.name + ' tried to cast ' + self.spell_name + ' at a lower level: ' + str(cast_level),
                self.player.name + ' tried to cast ' + self.spell_name +', but spell slots level ' + str(cast_level) + ' are empty',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is in wild shape',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is currently concentrating']
        ifstatements(rules, errors, self.DM).check()

        #Is reaction Spell break here
        if self.is_reaction_spell:
            if self.player.reaction == 0:
                quit()
            else:
                self.player.reaction = 0
                self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
                return True
        #check if player has cast this round
        elif self.player.cast == 0:
            self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has already cast a spell')
            quit()
        #check is player has action/bonus action left
        elif self.make_action_check() == False:
            quit()
        #everything clear for cast
        else:
            self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
            return True

    def make_cantrip_check(self):
        rules = [self.is_known,
                self.player.raged == 0,
                self.player.wild_shape_HP == 0,
                self.is_concentration_spell == False or self.player.is_concentrating==False]
        errors = [self.player.name + ' tried to cast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to cast ' + self.spell_name + ' but is raging',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is in wild shape',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is currently concentrating']
        ifstatements(rules, errors, self.DM).check()
        #check is player has action/bonus action left
        if self.make_action_check() == False:
            quit()
        #everything clear for cast
        else:
            return True        

    def make_action_check(self):
        #Bonus Action Spell
        if self.is_bonus_action_spell:
            #Bonus Action used?
            if self.player.bonus_action == 0:
                self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has no Bonus Action left')
                quit()
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
                    quit()
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
        rules = [len(targets)==2,
                self.player.knows_twinned_spell,
                self.player.sorcery_points >= 2]
        errors = [self.player.name + ' tried to twinned spell ' + self.spell_name + ' but not with 2 targets',
                self.player.name + ' tried to twinned cast ' + self.spell_name + ' without knwoing it',
                self.player.name + ' tried to twinned cast ' + self.spell_name + ' but has not enough sorcery points']
        ifstatements(rules, errors, self.DM).check()
        #If twinned spell is known and sorcery Points there, cast spell twice 
        if self.make_action_check() == True:
            #player should be able to cast, so a True came back. But in the macke_action_check function the bonus_action, action, and/or cast was diabled, so it will be enabled here before casting 
            if cast_level==False:
                cast_level = self.spell_level
            if cast_level == 0:
                self.player.sorcery_points -= 1
            else:
                self.player.sorcery_points -= cast_level
                self.player.spell_slot_counter[cast_level -1] += 1 #add another spell Slots as two will be used in the twin cast
            self.DM.say(self.player.name + ' twinned casts ' + self.spell_name)
            for x in targets:
                #everything will be enabeled in order for the spell do be cast twice
                if self.is_bonus_action_spell:
                    self.player.bonus_action = 1
                else:
                    self.player.action = 1
                if self.is_cantrip == False:
                    self.player.cast = 1
                if self.is_concentration_spell:
                    self.player.is_concentrating = False #enable double concentration castst
                self.cast(x, cast_level)

    def quickened_cast(self, targets, cast_level=False):
        rules = [self.player.knows_quickened_spell,
                self.player.sorcery_points >= 2,
                self.player.quickened_spell==0]
        errors = [self.player.name + ' tried to use Quickened Spell without knowing it',
                self.player.name + ' tried to use quickened Spell, but has no Sorcery Points left',
                self.player.name + ' tried to use quickened spell, but has already used it']
        ifstatements(rules, errors, self.player.DM).check()

        self.player.sorcery_points -= 2
        self.player.quickened_spell = 1
        self.DM.say(self.player.name + ' used Quickened Spell')
        if cast_level==False:
            cast_level = self.spell_level
        self.cast(targets, cast_level)

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

            self.DM.say(str(self.player.name) + ' casts fire bolt: ')
            #all specifications for this spell are given to the attack function
            self.player.attack(target, is_ranged=True, other_dmg=dmg, damage_type='fire', tohit=tohit)
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
            self.DM.say(self.player.name + ' casts eldritch blast: ')

            if type(targets) != list:  #if targets is only one Entity passed
                targets = [targets]
            target_counter = 0
            while atk_counter > 0:    #loop for missile cast
                #attack fist target with spell specifications and then move to next
                self.player.attack(targets[target_counter], is_ranged=True, other_dmg=dmg, damage_type='force', tohit=tohit)
                atk_counter -= 1
                target_counter += 1
                if target_counter == len(targets):    #if all targets are hit once, restart 
                    target_counter = 0

            self.player.eldritch_blast_cast += 1

    def cast_entangle(self, target, cast_level=1):
        if type(target) == list:
            target = target[0]
        if target.is_entangled():
            self.DM.say(self.player.name + ' tried to entangle ' + target.name + ', who is already entangled')
            quit()#double cast makes no sene 
        if self.make_spell_check(cast_level) == False:
            return
        else:
            target.last_attacker = self.player    #target remembers last attacker
            save = target.make_save(0)           #let them make save
            if save < self.player.spell_dc:
                #write the entagle variables for the player and target
                self.DM.say(self.player.name + ' casts Entangle and ' + str(target.name) + ' failed save with: ' + str(save))
                self.player.entangle_cast += 1
                self.player.is_concentrating = True
                self.DM.relate(self.player, target, 'Entangle')
                target.restrained = 1               #make them restrained
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
            damage = 10.5 + 3.5*(cast_level - 1)   #upcast dmg 3d6 + 1d6 per level over 2
            if self.player.empowered_spell:
                damage = damage*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            for i in targets:
                Dmg = dmg(damage, 'fire')
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(1)           #let them make dex saves
                if save >= self.player.spell_dc:
                    Dmg.multiply(1/2)                 #save made
                i.changeCHP(Dmg, self.player, True)

    def cast_cure_wounds(self, target, cast_level=1):
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Cure Wounds at level: ' + str(cast_level))
            self.player.cure_wounds_cast += 1
            heal = 4.5*cast_level + self.player.spell_mod
            target.changeCHP(dmg(-heal, 'heal'), self.player, False)

    def cast_healing_word(self, target, cast_level=1):
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Healing Word at level: ' + str(cast_level))
            self.player.healing_word_cast += 1
            heal = 2.5*cast_level + self.player.spell_mod
            if heal < 0:
                heal = 1
            target.changeCHP(dmg(-heal,'heal'), self.player, True)

    def cast_magic_missile(self, targets, cast_level=1):           #needs list of targets
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.player.magic_missile_cast += 1
            missile_counter = 2 + cast_level          #overcast mag. mis. for more darts 
            target_counter = 0
            damage = 3.5   #1d4 + 1
            if self.player.empowered_spell:
                damage = damage*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            self.DM.say(self.player.name + ' casts Magic Missile at level ' + str(cast_level))
            while missile_counter > 0:    #loop for missile cast
                missile_counter -= 1
                Dmg = dmg(damage, 'force')
                for x in self.DM.relations:
                    if x.type == 'Hex' and x.target == targets[target_counter] and x.initiator == self.player:
                        Dmg.add(3.5,'necrotic')
                        self.DM.say(' Hex ', end= '')
                targets[target_counter].last_attacker = self.player    #target remembers last attacker
                targets[target_counter].changeCHP(Dmg, self.player, True)    #target takes damage
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
            damage = 13.5 + 4.5*(cast_level - 2)   #upcast dmg 3d6 + 1d6 per level over 2
            #empowered Spell
            if self.player.empowered_spell:
                damage = damage*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            for i in targets:
                Dmg = dmg(damage, 'fire')
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(1)           #let them make saves
                if save >= self.player.spell_dc:
                    Dmg.multiply(1/2)             #save made
                i.changeCHP(Dmg, self.player, True)

    def cast_scorching_ray(self, targets, cast_level=2):           #needs list of targets
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list:  #if targets is only one Entity passed
                targets = [targets]
            self.DM.say(self.player.name + ' casts Scorching Ray at Level: ' + str(cast_level))
            self.player.scorching_ray_cast += 1
            tohit = self.player.spell_mod + self.player.proficiency
            damage = 7
            if self.player.empowered_spell:
                damage = damage*1.21
                self.player.empowered_spell = False
                self.DM.say('Empowered: ', end='')
            ray_counter = 1 + cast_level          #overcast + 1 Ray per level
            target_counter = 0
            while ray_counter > 0:    #loop for missile cast
                #attack fist target with spell specifications and then move to next
                self.player.attack(targets[target_counter], is_ranged=True, other_dmg=damage, damage_type='fire', tohit=tohit)
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
            damage = 28 + 3.5*(cast_level - 3)   #upcast dmg 8d6 + 1d6 per level over 2
            spell_is_empowered = False
            if self.player.empowered_spell:
                damage=damage*1.21
                self.player.empowered_spell = False
                spell_is_empowered = True                
            for i in targets:
                Dmg = dmg(damage, 'fire')
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(1)           #let them make saves
                if spell_is_empowered:
                    self.DM.say('Empowered: ', end='')
                if save >= self.player.spell_dc:
                    Dmg.multiply(1/2)                #save made
                i.changeCHP(Dmg, self.player, True)

    def cast_haste(self, target, cast_level = 3):
        if type(target) == list:
            target = target[0]
        if target.is_hasted():
            self.DM.say(self.player.name + ' tried to cast Haste for ' + target.name + ', who is already hasted')
            quit()#double cast makes no sene 
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Haste for ' + target.name)
            self.player.haste_cast += 1
            self.player.is_concentrating = True 
            self.DM.relate(self.player, target, 'Haste')
    
    def cast_shield(self, cast_level = 1):
        if self.make_spell_check(cast_level): #return True if everything is in order, reaction and spellslots are then expendet
            self.DM.say(self.player.name + ' casts Shield, ', end='') #interrupts the attack function prints 
            self.player.shield_cast += 1
            self.player.AC += 5

    def cast_hex(self, target, cast_level = 1):
        #Hex needs exactly one target
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(self.player.name + ' casts Hex at ' + target.name + ' with level ' + str(cast_level))
            self.player.hex_cast += 1
            self.player.is_concentrating = True
            self.DM.relate(self.player, target, 'Hex')

    def change_hex(self, target):
        rules = [self.player.can_choose_new_hex,
                self.is_known,
                target.state == 1,
                self.player.bonus_action == 1]
        errors = [self.player.name + ' tried to change a bound hex',
                self.player.name + ' tried to change a hex without knowing it',
                self.player.name + ' tried to change to a not conscious target',
                self.player.name + ' tried to change a hex without having a bonus action']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.player.name + ' changes the hex to ' + target.name)
        self.player.bonus_action = 0 #takes a BA
        self.player.can_choose_new_hex = False
        self.DM.relate(self.player, target, 'Hex')

    def cast_armor_of_agathys(self, target, cast_level = 1):
        #Armor only works for self
        player = self.player
        target = player
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(player.name + ' casts Armor of Agathys at level ' + str(cast_level))
            player.armor_of_agathys_cast += 1
            player.has_armor_of_agathys = True
            TempHP = 5*cast_level
            player.agathys_dmg = 5*cast_level
            player.addTHP(TempHP) #add THP to self

    def cast_false_life(self, target, cast_level = 1):
        #Only works for you
        player = self.player
        target = player
        if self.make_spell_check(cast_level) == False: #check if castable
            return
        else:
            self.DM.say(player.name + ' casts False Life at level '+ str(cast_level))
            player.false_life_cast += 1
            TempHP = 1.5 + 5*cast_level
            player.addTHP(TempHP) #Add the THP

    def cast_spiritual_weapon(self, target, cast_level = 2):
        player = self.player
        #target is first attack target
        if self.make_spell_check(cast_level) == False:
            return
        else:
            self.DM.say(player.name + ' casts Spiritual Weapon at level ' + str(cast_level))
            player.spiritual_weapon_cast += 1
            player.has_spiritual_weapon = True
            player.SpiritualWeaponDmg = player.spell_mod + 4.5*(cast_level -1) 
            player.SpiritualWeaponCounter = 0 #10 Rounds of Weapon

            #Attack Once as BA
            self.spiritual_weapon_attack(target)

    def use_spiritual_weapon(self, target):
        player = self.player
        rules = [player.has_spiritual_weapon,
                player.bonus_action == 1]
        errors = [player.name + ' tried using the Spiritual Weapon without having one',
                player.name + ' tried using the Spiritual Weapon without having a bonus action']
        ifstatements(rules, errors, self.DM).check()

        self.spiritual_weapon_attack(target)

    def spiritual_weapon_attack(self, target):
        if type(target) == list:
            target = target[0]
        player = self.player
        WeaponTohit = player.spell_mod + player.proficiency #ToHit of weapon
        WeaponDmg = player.SpiritualWeaponDmg #Set by the Spell 
        self.DM.say('Spiritual Weapon of ' + player.name + ' attacks: ')
        #Make a weapon Attack against first target
        self.player.attack(target, is_ranged=False, other_dmg=WeaponDmg, damage_type='force', tohit=WeaponTohit)
        self.player.bonus_action = 0 #It uses the BA to attack

    def cast_shatter(self, targets, cast_level=2):
        if self.make_spell_check(cast_level) == False:
            return
        else:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.player.name + ' casts Shatter at Level: ' + str(cast_level))
            self.player.shatter_cast += 1
            damage = 13.5 + 4.5*(cast_level - 2)   #upcast dmg 3d8 + 1d8 per level over 2
            spell_is_empowered = False
            if self.player.empowered_spell:
                damage=damage*1.21
                self.player.empowered_spell = False
                spell_is_empowered = True                
            for i in targets:
                Dmg = dmg(damage, 'thunder')
                i.last_attacker = self.player    #target remembers last attacker
                save = i.make_save(self.spell_save_type)           #let them make con saves
                if spell_is_empowered:
                    self.DM.say('Empowered: ', end='')
                if save >= self.player.spell_dc:
                    Dmg.multiply(1/2) #made save
                i.changeCHP(Dmg, self.player, True)

    def cast_conjure_animals(self, fight, cast_level=3):
        #Work in Progress 
        #Im am using a trick here, ususally a target is passed, but this spell needs the fight
        #As a solution the score function of this spell passes the fight as 'targtes' 
        #The cunjured Animals are initiated as fully functunal entity objects
        #The Stats are loaded from the Archive
        #If they reach 0 CHP they will die and not participate in the fight anymore
        #The do_the_fightinf function will then pic them out and delete them from the fight list
        player = self.player
        if self.make_spell_check(cast_level) == False:
            return 
        else:
            player.DM.say(player.name + ' cast cunjure Animals at level ' + str(cast_level))
            player.conjure_animals_cast += 1
            player.is_concentrating = True #Conc Spell

            level = 10
            while level > 2:
                Index = int(random()*len(player.BeastForms))
                AnimalName = player.BeastForms[Index]['Name'] #Random Animal
                level = player.BeastForms[Index]['Level'] #Choose a Animal of level 2 or less

            Number = int(2/level)     #8 from CR 1/4, 4 from CR 1/2 ...
            
            if cast_level < 5:
                Number = Number
            elif cast_level < 7:
                Number = Number*2
            elif cast_level < 9: 
                Number = Number*3
            else: 
                Number = Number*4

            #Initiate a new entity for the Animals ans add them to the fight
            for i in range(0,Number):
                animal = entity(AnimalName, player.team, player.DM, archive=True)
                animal.name = 'Conjured ' + AnimalName + str(i+1)
                self.DM.say(animal.name + ' appears')
                animal.is_a_conjured_animal = True
                animal.conjurer = player
                fight.append(animal)
                self.DM.relate(player, fight[-1], 'ConjuredAnimal')
                player.has_animals_conjured = True

    def cast_guiding_bolt(self, target, cast_level=1):
        player = self.player
        if type(target) == list:
            target = target[0]
        if self.make_spell_check(cast_level) == False:
            return
        else:
            tohit = player.spell_mod + player.proficiency
            dmg = 3*3.5 + 3.5*cast_level

            if player.empowered_spell:
                dmg = dmg*1.21
                player.empowered_spell = False
                self.DM.say('Empowered: ', end='')

            self.DM.say(str(player.name) + ' casts guiding bolt at Level: ' + str(cast_level))
            #all specifications for this spell are given to the attack function
            damage_done = player.attack(target, is_ranged=True, other_dmg=dmg, damage_type= 'radiant', tohit=tohit)
            if damage_done > 0:
                self.DM.relate(player, target, 'GuidingBolt')
                target.is_guiding_bolted = True
                player.used_guiding_bolt = True
            player.guiding_bolt_cast += 1
            

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

            #Account for Hex
            if target.is_hexed():
                for x in self.DM.relations: 
                    if x.type == 'Hex' and x.target == target and x.initiator == self.player:
                        DMGScore += 3.5
        return DMGScore

    def return_0_score(self):
        #this function returns a 0 score, so that spell is not cast
        Score = 0
        SpellTargets = [self.player]
        CastLevel = 0
        return Score, SpellTargets, CastLevel

    def random_score_scale(self):
        Scale = 0.6+0.8*random()
        return Scale

    def choose_smallest_slot(self, MinLevel, MaxLevel):
        #Returns the smallest spellslot that is still available
        #MaxLevel is cast level, so MaxLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in range(MinLevel-1, MaxLevel):
            if self.player.spell_slot_counter[i]>0:
                return i+1
        return False 

    def choose_highest_slot(self, MinLevel, MaxLevel):
        #Returns the highest spellslot that is still available
        #MinLevel is cast level, so MinLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in reversed(range(MinLevel-1, MaxLevel)):
            if self.player.spell_slot_counter[i]>0:
                return i+1
        return False 

    #Scores and Targets 

    def score_fire_bolt(self, fight, twinned_cast = False):
        CastLevel = 0 #always 0 for cantrip
        if self.player.level >=17: dmg= 5.5*4
        elif self.player.level >=11: dmg= 5.5*3
        elif self.player.level >= 5: dmg = 5.5*2
        else: dmg = 5.5        

        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg = dmg, other_dmg_type='fire')]
        if SpellTargets == [False]: #No Target
            return self.return_0_score()
        if twinned_cast:
            #Secound Target for Twin Cast
            twin_target = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg = dmg, other_dmg_type='fire')
            if twin_target == False:
                return self.return_0_score()
            SpellTargets.append(twin_target)
        
        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=True)
        if twinned_cast: Score = Score*2

        Score = Score*self.random_score_scale() # a little random power 
        return Score, SpellTargets, CastLevel

    def score_entangle(self, fight, twinned_cast = False):
        #Choose One Target
        player = self.player
        SpellTargets = []
        Choices = [x for x in fight if x.team != player.team and x.state == 1 and x.is_entangled() == False]
        if len(Choices) > 0: #if there are any
            SpellTargets.append(self.player.AI.choose_att_target(Choices, AttackIsRanged=True, other_dmg=0, other_dmg_type='true')) #append best enemy to entangle
        else: return self.return_0_score()
        if twinned_cast:
            Choices.remove(SpellTargets[0]) #Dont double haste
            if len(Choices) > 0:
                SpellTargets.append(self.player.AI.choose_att_target(Choices, AttackIsRanged=True, other_dmg=0, other_dmg_type='true')) #append best 2nd enemy to entangle
            else: return self.return_0_score()

        #Maybe no targets found
        if SpellTargets[0] == False:
            return self.return_0_score()
        if len(SpellTargets) > 1:
            if SpellTargets[1] == False:
                return self.return_0_score()

        #Score is equal to how dangerous the target is
        Score = 0
        allies = [x for x in fight if x.state == 1 and x.team == player.team]
        Score += sum([x.dmg*x.attacks/10 for x in fight if x.state == 1 and x.team == player.team])
        for x in SpellTargets:
            Score += x.dps()/4 #disadvantage helps do reduce dmg of enemy
            #Add dmg for the other players
            Score += player.spell_dc - 10 - x.modifier[0] #good against weak enemies
        CastLevel = self.choose_smallest_slot(1,3)
        if CastLevel == False: #Didnt find slot 3 or smaller
        #just dont cast if entangle is the best u can do at lv 4
            CastLevel = 0
            Score = 0
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel
    
    def score_burning_hands(self, fight, twinned_cast = False):
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 115) #15ft**2/2
        CastLevel = self.choose_highest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        Score = 0
        #Dmg Score
        dmg = 3*3.5 + 3.5*(CastLevel-1)
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale() #a little random power
        return Score, SpellTargets, CastLevel

    def score_cure_wounds(self, fight, twinned_cast = False):
        return self.return_0_score() #at the moment, healing is handeled differently

    def score_healing_word(self, fight, twinned_cast = False):
        return self.return_0_score() #at the moment, healing is handeled differently

    def score_magic_missile(self, fight, twinned_cast = False):
        CastLevel = self.choose_highest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        TargetNumer = CastLevel + 2
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='force') for i in range(0, TargetNumer)]
        if False in SpellTargets:
            return self.return_0_score()

        #DMG Score
        Score = self.dmg_score(SpellTargets, 3.5, dmg_type='force', SpellAttack=False)
        Score += 2*CastLevel #a little extra for save hit 
        Score = Score*self.random_score_scale() # +/-20% range to vary spells
        return Score, SpellTargets, CastLevel

    def score_aganazzars_scorcher(self, fight, twinned_cast = False):    
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 300) #30ft*10ft
        CastLevel = self.choose_highest_slot(2,9)
        if CastLevel == False: return self.return_0_score()
        
        #DMG Score
        dmg = 13.5 + 4.5*(CastLevel-2)
        Score = self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_scorching_ray(self, fight, twinned_cast = False):
        CastLevel = self.choose_highest_slot(2,9)
        if CastLevel == False: return self.return_0_score()

        TargetNumer = CastLevel + 1
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='fire') for i in range(0, TargetNumer)]
        if False in SpellTargets: #No Target
            return self.return_0_score()

        #Dmg Score
        dmg = 7
        Score = 0
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=True)
        Score = Score*self.random_score_scale() # +/-20% range to vary spells
        return Score, SpellTargets, CastLevel

    def score_fireball(self, fight, twinned_cast = False):
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 1250) #pi*20ft**2
        CastLevel = self.choose_highest_slot(3,9)
        if CastLevel == False: return self.return_0_score()
        
        #DMG Score
        dmg = 28 + 3.5*(CastLevel - 3)
        Score = self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_haste(self, fight, twinned_cast = False):
        player = self.player
        SpellTargets = []
        Choices = [x for x in fight if x.team == player.team and x.state == 1  and x.is_hasted() == False]
        ChoicesScore = [x.dmg*(random()*0.5 +0.5) + x.AC*(random()*0.2 +0.2) + x.CHP/3*(random()*0.2 + 0.1) for x in Choices]
        SpellTargets.append(Choices[np.argmax(ChoicesScore)]) #append best player for Haste
        if twinned_cast:
            Choices.remove(SpellTargets[0]) #Dont double haste
            if len(Choices) == 0:
                return self.return_0_score()
            ChoicesScore = [x.dmg*(random()*0.5 +0.5) + x.AC*(random()*0.2 +0.2) + x.CHP/3*(random()*0.2 + 0.1) for x in Choices]
            SpellTargets.append(Choices[np.argmax(ChoicesScore)]) #append best player for 2nd Haste

        Score = 0
        for x in SpellTargets:
            Score += x.dmg/2*(random()*3.5 + 0.7) #lasts for some rounds
            Score += x.AC - player.AC #Encourage High AC
            #Dont haste low Ally
            if x.CHP < x.HP/4:
                Score -= x.dmg

        CastLevel = self.choose_smallest_slot(3,5) #not higher then 5
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_shield(self, fight, twinned_cast = False):
        return self.return_0_score() #shield should not be considered to cast in turn 

    def score_eldritch_blast(self, fight, twinned_cast = False):
        if self.player.level >=17:TargetNumer = 4
        elif self.player.level >=11:TargetNumer = 3
        elif self.player.level >= 5:TargetNumer = 2
        else:TargetNumer = 1
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=5.5, other_dmg_type='force') for i in range(0,TargetNumer)]
        if False in SpellTargets: #No Target
            return self.return_0_score()        

        CastLevel = 0 #always for cantrip

        #DMG Score
        Score = 0
        dmg = 5.5
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='fire', SpellAttack=True)
        
        Score = Score*self.random_score_scale() # a little random power
        return Score, SpellTargets, CastLevel

    def score_hex(self, fight, twinned_cast = False):
        SpellTargets = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='true') #Choose best target
        if SpellTargets == False: return self.return_0_score()

        Score = 0
        Score = 3.5*self.player.attacks*(random()*2 + 3) #hex holds for some rounds
        if self.player.SpellBook['MagicMissile'].is_known:
            Score += 3.5
        if self.player.SpellBook['EldritchBlast'].is_known:
            Score += 3.5*2

        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_armor_of_agathys(self, fight, twinned_cast = False):
        player = self.player
        SpellTargets = [player] #only self cast

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(1,9)
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(1,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        if player.has_armor_of_agathys: return self.return_0_score() #no double cast
        
        Score = 5*CastLevel #does at least 5dmg and 5 TPH for you
        Score = Score*(3 - 2*player.CHP/player.HP) #tripples for low player 
        Score -= player.THP*1.5 #If you still have THP, rather keep it

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_false_life(self, fight, twinned_cast = False):
        player = self.player
        SpellTargets = [player] #only self cast

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(1,9)
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(1,Highest_Slot-2) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        #Score 
        Score = 3 + 3*CastLevel  #dmg equal value but for THP, a bit lower then 5
        Score = Score*(3 - 2*player.CHP/player.HP) #tripples for low player
        if player.THP > 0:
            return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_spiritual_weapon(self, fight, twinned_cast = False):
        player = self.player

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(2,9) 
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(2,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        #DMG
        SpellDmg = player.spell_mod + 4.5*(CastLevel - 1)

        #Target
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=SpellDmg, other_dmg_type='force')]
        if SpellTargets[0] == False:
            return self.return_0_score()#no Enemy in reach

        if player.has_spiritual_weapon:
            return self.return_0_score() #has already sw 

        Score = self.dmg_score(SpellTargets, dmg=SpellDmg, dmg_type='force', SpellAttack=True)
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_shatter(self, fight, twinned_cast = False):
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, 315) #pi*10ft**2
        CastLevel = self.choose_highest_slot(2,7)
        if CastLevel == False: return self.return_0_score()
        
        #DMG Score
        dmg = 13.5 + 4.5*(CastLevel - 2)
        Score = self.dmg_score(SpellTargets, dmg, dmg_type='thunder', SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def score_conjure_animals(self, fight, twinned_cast = False):
        #Work in Progress
        player = self.player
        SpellTargets = fight #this is a trick to pass the fight to the spell cast function
        #Okay, the critical level are 3, 5, 7, 9
        #So 4, 6, 8 would be a bit wasted
        TryLevel = [9,7,5,3]
        for x in TryLevel:
            CastLevel = self.choose_smallest_slot(x,9)
            if CastLevel != False: break

        if CastLevel == False: return self.return_0_score()
        Score = 0 #for now
        if player.has_animals_conjured: quit() #nonsense
        #Ape has CR 1/2 with +5 to hit, 6.5 dmg, 2 attacks -> 6.5/4 *2attacks /0.5CR -> 6.5dmg/1CR
        #BrownBear CR 1 +5 9.75dmg, 2 attacks -> 4.8dmg/1CR
        #Wolf 7dmg/4 /0.25CR -> 7dmg/1CR
        #About 6 dmg/1CR, HP matters less because of Concentration

        #As concentration can be interrupted, they might not last so long, lets say 1-3 Rounds
        if CastLevel < 5:
            TotalCR = 2
        elif CastLevel < 7:
            TotalCR = 4
        elif CastLevel < 9: 
            TotalCR = 6
        else: 
            TotalCR = 8
        Score = TotalCR*6*(random()*1.2 + 1.5) #CR * 6dmg/CR * 1.5-2.7 Rounds
        return Score, SpellTargets, CastLevel

    def score_guiding_bolt(self, fight, twinned_cast = False):
        CastLevel = self.choose_highest_slot(1,9)
        if CastLevel == False: return self.return_0_score()
        dmg = 3.5*3 + 3.5*CastLevel
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg = dmg, other_dmg_type='radiant')]
        if SpellTargets == [False]: #No Target
            return self.return_0_score()
        if twinned_cast:
            #Secound Target for Twin Cast
            twin_target = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg = dmg, other_dmg_type='radiant')
            if twin_target == False:
                return self.return_0_score()
            SpellTargets.append(twin_target)
        
        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, dmg, dmg_type='radiant', SpellAttack=True)
        Score += self.player.dps()*0.2 #to account for advantage given
        if twinned_cast: Score = Score*2

        Score = Score*self.random_score_scale() # a little random power 
        return Score, SpellTargets, CastLevel
