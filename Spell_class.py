from Ifstatement_class import ifstatements
from random import random
from Entity_class import * #should be disabled before running
from Token_class import *
from numpy import argmax
from Dmg_class import dmg

class spell:
    def __init__(self, player):
        #this class is initiated at the entity for spellcasting
        self.DM = player.DM
        self.player = player            #the Player that is related to this spell Object and which will cast this spell
        self.TM = self.player.TM       #Token Manager of player 
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived, AI_blank should be false
            self.player = entity('test', 0, 0)


        #Initial
        if hasattr(self, 'spell_name') == False:
            self.spell_name = 'undefined'          #Give Name, if not specified in subclass
        if hasattr(self, 'spell_text') == False:
            self.spell_text = 'undefined'         #This is the text name that will be printed

        self.spell_level = 0
        self.cast_level = 0 #Will be set before every cast
        self.spell_save_type = False        #Type of the Spell Save 
        self.is_bonus_action_spell = False
        self.is_concentration_spell = False
        self.is_reaction_spell = False
        self.is_cantrip = False
        self.is_twin_castable = False      #Meta Magic Option
        self.is_range_spell = False

        #Activate the Spell, if the player knows it
        self.is_known = False
        if self.spell_name in player.spell_list:
            self.is_known = True

        self.was_cast = 0

    #any spell has a specific Spell cast function that does what the spell is supposed to do
    #This Function is the cast function and will be overwritten in the subclasses
    #To do so, the make_spell_check function makes sure, that everything is in order for the self.player to cast the spell
    #The make_action_check function checks if Action, Bonus Action is used
    #the spell class objects will be linked to the player casting it by self.player

    def cast(self, targets, cast_level = False, twinned = False):
        if cast_level == False: cast_level = self.spell_level
        self.autorize_cast(cast_level)
        self.announce_cast()

    def autorize_cast(self, cast_level):
        #Checks if cast is autorized
        #Make a check if cast is possible
        if cast_level == False:
            cast_level = self.spell_level #cast as level if nothing else

        if self.is_cantrip:
            if self.make_cantrip_check() == False:
                return
        else:
            if self.make_spell_check(cast_level=cast_level) == False:
                return
        
        #If everything is autorized, set cast_level
        self.cast_level = cast_level
        self.was_cast += 1  #for spell recap

    def announce_cast(self):
        text = ''.join([self.player.name,' casts ',self.spell_text,' at lv.', str(self.cast_level)])
        self.player.DM.say(text, True)

    def score(self, fight, twinned_cast = False):
        #The Score function is called in the Choices Class
        #It is supposed to return a dmg equal score
        #It also returns the choosen SpellTargts and the CastLevel
        #If this spell is not soposed to be considered as an option this turn, return 0 score
        #This function should be overwritten in the subclassses
        return self.return_0_score()

    def make_spell_check(self, cast_level):
        #This function also sets the action, reaction or bonus action ans spell counter down
        rules = [self.is_known, 
                self.player.raged == 0,
                cast_level >= self.spell_level, 
                self.player.spell_slot_counter[cast_level -1] > 0,
                self.player.is_shape_changed == False,
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
                print(self.player.name + ' tired to cast ' + self.spell_name + ', but hast no reaction')
                quit()
            else:
                self.player.reaction = 0
                self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
                return True
        #check if player has cast this round
        elif self.player.has_cast_left == False:
            print(self.player.name + ' tried to cast ' + self.spell_name + ', but has already cast a spell')
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
                self.player.is_shape_changed == False,
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
        #This function checks is the player has the required action left and sets it off if so
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
                    self.player.has_cast_left = False
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
                        self.player.has_cast_left = False
                    return True
                #No Bonus Action left
                else:
                    print(self.player.name + ' tried to quickened cast ' + self.spell_name + ', but has no Bonus Action left')
                    quit()
            #No Quickened Spell
            else:
                if self.player.action == 0:
                    self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has no action left', True)
                    return False
                else:
                    self.player.action = 0  #action used
                    if self.is_cantrip == False:
                        self.player.has_cast_left = False
                    return True

#-------------Meta Magic------------------
    #The mega magic functions do their job and then cast the individual spell
    #See cast function in subclasses
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
            self.DM.say(self.player.name + ' twinned casts ' + self.spell_name, True)
            if self.is_concentration_spell and self.is_twin_castable:
                #Must enable these here again, as they are disabled in make_action_check()
                if self.is_bonus_action_spell:
                    self.player.bonus_action = 1
                else:
                    self.player.action = 1
                if self.is_cantrip == False:
                    self.player.has_cast_left = True
                #This kind of spells must handle their twin cast in the cast function
                self.cast(targets, cast_level, twinned=True)
            else:
                for x in targets:
                    #everything will be enabeled in order for the spell do be cast twice
                    if self.is_bonus_action_spell:
                        self.player.bonus_action = 1
                    else:
                        self.player.action = 1
                    if self.is_cantrip == False:
                        self.player.has_cast_left = True
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
        self.player.quickened_spell = 1  #see make_spell_check
        self.DM.say(self.player.name + ' used Quickened Spell', True)
        if cast_level==False:
            cast_level = self.spell_level
        self.cast(targets, cast_level)

#---------------DMG Scores---------------
#This Scores are returned to the choose_spell_AI function and should resemble about 
#the dmg that the spell makes or an appropriate counter value if the spell does not 
#make direkt dmg, like haste or entangle
#The Function must also return the choosen Targets and Cast Level
#If a Score 0 is returned the spell will not be considered to be cast that way
#The individual sores are in the subclasses

    def hit_propability(self, target):
    #This function evaluetes how propable a hit with a spell attack will be
        SpellToHit = self.player.spell_mod + self.player.proficiency
        AC = target.AC
        prop = (20 - AC + SpellToHit)/20
        return prop

    def save_sucess_propability(self, target):
        SaveMod = target.modifier[self.spell_save_type]
        Advantage = target.check_advantage(self.spell_save_type, notSilent = False)
        #Save Sucess Propability:
        prop = (20 - self.player.spell_dc + SaveMod)/20
        if Advantage < 0:
            prop = prop*prop  #Disadvantage, got to get it twice
        elif Advantage > 0:
            prop = 1 - (1-prop)**2  #would have to miss twice
        return prop

    def dmg_score(self, SpellTargets, CastLevel, SpellAttack=True, SpellSave=False):
        #This returns a dmg score for the score functions
        DMGScore = 0
        dmg = self.spell_dmg(CastLevel) #is defined in the subclasses that need it
        for target in SpellTargets:
            target_dmg = dmg
            if SpellSave: #Prop that target makes save
                target_dmg = dmg/2 + (dmg/2)*(1-self.save_sucess_propability(target))
            if SpellAttack:   #it you attack, account for hit propabiltiy
                target_dmg = target_dmg*self.hit_propability(target)#accounts for AC
            #DMG Type, Resistances and stuff
            if self.dmg_type in target.damage_vulnerability:
                target_dmg = target_dmg*2
            elif self.dmg_type in target.damage_resistances:
                target_dmg = target_dmg/2
            elif self.dmg_type in target.damage_immunity:
                target_dmg = 0
            DMGScore += target_dmg #Add this dmg to Score

            #Account for Hex
            if target.is_hexed and self.player.is_hexing:
                for HexToken in self.player.CurrentHexToken.links: #This is your Hex target
                    if HexToken.TM.player == target:
                        DMGScore += 3.5
                        break
            #Account for Hunters Mark
            if target.is_hunters_marked and self.player.is_hunters_marking:
                for Token in self.player.CurrentHuntersMarkToken.links: #This is your HM target
                    if Token.TM.player == target:
                        DMGScore += 3.5
                        break


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
        #Returns the smallest spellslot that is still available in the range
        #MaxLevel is cast level, so MaxLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in range(MinLevel-1, MaxLevel):
            if self.player.spell_slot_counter[i]>0:  #i = 0 -> lv1 slot
                return i+1
        return False 

    def choose_highest_slot(self, MinLevel, MaxLevel):
        #Returns the highest spellslot that is still available in the range
        #MinLevel is cast level, so MinLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in reversed(range(MinLevel-1, MaxLevel)):
            if self.player.spell_slot_counter[i]>0:
                return i+1
        return False 

#Specialized Spell Types
class attack_spell(spell):
    #This Class is a spell that makes one or more single target spell attacks
    def __init__(self, player, dmg_type, number_of_attacks = 1):
        super().__init__(player)
        self.number_of_attacks = number_of_attacks
        self.dmg_type = dmg_type
        self.spell_text = 'spell name' #This will be written as the spell name in print
    
    def cast(self, targets, cast_level=False, twinned=False):
        if type(targets) != list:
            targets = [targets]  #if a list, take first target
        super().cast(targets, cast_level, twinned) #self.cast_level is set in spell super.cast
        #Cast is authorized, so make a spell attack
        tohit = self.player.spell_mod + self.player.proficiency
        dmg = self.spell_dmg(self.cast_level)

        if self.player.empowered_spell:
            dmg = dmg*1.21
            self.player.empowered_spell = False #reset empowered spell
            self.DM.say(' Empowered: ')

        #Everything is set up and in order
        #Now make the attack/attacks       
        return self.make_spell_attack(targets, dmg, tohit)

    def make_spell_attack(self,targets, dmg, tohit):
        #This function is called in cast function and makes the spell attacks
        #all specifications for this spell are given to the attack function
        #Can attack multiple targts, if one target is passed and num of attacks == 1 this is just one attack
        target_counter = 0
        attack_counter = self.number_of_attacks
        dmg_dealed = 0
        while attack_counter > 0:
            dmg_dealed += self.player.attack(targets[target_counter], is_ranged=self.is_range_spell, other_dmg=dmg, damage_type=self.dmg_type, tohit=tohit, is_spell=True)
            attack_counter -= 1
            target_counter += 1
            if target_counter == len(targets):
                target_counter = 0  #if all targets were attacked once, return to first
        return dmg_dealed

    def spell_dmg(self, cast_level):
        #This function will return the dmg according to Cast Level
        print('No dmg defined for spell: ' + self.spell_name)

    def score(self, fight, twinned_cast=False):
        #This function takes an attack spell and chooses targets and a cast level
        #It then returns an expactation damage score for the choice class
        #Choose CastLevel:
        if self.is_cantrip: CastLevel = 0
        else:
            CastLevel = self.choose_highest_slot(self.spell_level,9) #Choose highest Spell Slot
            if CastLevel == False: return self.return_0_score()

        #Find a suitable target/targts for this spell
        Choices = [x for x in fight if x.team != self.player.team]
        SpellTargets = []
        for i in range(0,self.number_of_attacks):
            #Append as many targets as attack numbers
            SpellTarget = self.player.AI.choose_att_target(Choices, AttackIsRanged=self.is_range_spell, other_dmg = self.spell_dmg(CastLevel), other_dmg_type=self.dmg_type, is_silent=True)
            if SpellTarget == False: #No target found
                return self.return_0_score()
            else: SpellTargets.append(SpellTarget)

        #Twin Cast
        if twinned_cast:
            if all([self.is_twin_castable, self.number_of_attacks == 1]):
                Choices.remove(SpellTargets[0]) #do not double twin cast
                TwinTarget = self.player.AI.choose_att_target(Choices, AttackIsRanged=self.is_range_spell, other_dmg = self.spell_dmg(CastLevel), other_dmg_type=self.dmg_type, is_silent=True)
                if TwinTarget == False: return self.return_0_score()  #No Target found
                SpellTargets.append(TwinTarget)
            else:
                print(self.player.name + ' requested twincast score, but target number does not check out')
                quit()

        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, CastLevel, SpellAttack=True, SpellSave=False)
        if twinned_cast: Score = Score*2

        Score = Score*self.random_score_scale()  #a little random power
        return Score, SpellTargets, CastLevel

class save_spell(spell):
    #This Class is a spell that makes one target make a spell save check
    #If it fails the save, an effect occures
    def __init__(self, player, spell_save_type):
        #spell save type is what check they make
        super().__init__(player)
        self.spell_save_type = spell_save_type
        self.spell_text = 'spell name' #This will be written as the spell name in print

    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        self.make_save(self, target, twinned)

    def make_save(self, target, twinned):
        #Single Target only
        if type(target) == list:
            target = target[0]
        
        target.last_attacker = self.player #target remembers last attacker/spell
        save = target.make_save(self.spell_save_type, DC = self.player.spell_dc) #make the save
        if save < self.player.spell_dc:
            #If failed, then take the individual effect
            self.DM.say(': failed the save')
            self.take_effect(target, twinned)
        else:
            self.DM.say(': made the save')
    
    def take_effect(self, target, twinned):
        #Take effect on a single target
        #This must be implemented in the subclasses
        print('The Save Spell has no effect')
        quit()

class aoe_dmg_spell(spell):
    #This class is a spell that targts multiple targts with a AOE dmg spell
    #On a Save the target gets half dmg
    def __init__(self, player, spell_save_type, dmg_type, aoe_area):
        super().__init__(player)
        self.spell_save_type = spell_save_type #What kind of save
        self.dmg_type = dmg_type
        self.spell_text = 'spell name' #This will be written as the spell name in print
        self.aoe_area = aoe_area  #area of the AOE in ft**2

    def cast(self, targets, cast_level=False, twinned=False):
        #Multiple Targts
        if type(targets) != list: targets = [targets]
        super().cast(targets, cast_level, twinned) #self.cast_level now set in spell super cast

        #Damage and empowered Spell
        damage = self.spell_dmg(self.cast_level)
        if self.player.empowered_spell:
            damage = damage*1.21
            self.player.empowered_spell = False
            self.DM.say(' Empowered: ')

        for target in targets:
            #Every target makes save
            self.make_save_for(target, damage=damage)

    def make_save_for(self, target, damage):
        #This function is called for every target to make the save and apply the dmg
        save = target.make_save(self.spell_save_type,DC = self.player.spell_dc)
        if save >= self.player.spell_dc:
            self.apply_dmg(target, damage=damage/2)
        else: self.apply_dmg(target, damage=damage)

    def apply_dmg(self, target, damage):
        #This finally applies the dmg dealed
        dmg_to_apply = dmg(damage, self.dmg_type)
        target.last_attacker = self.player
        target.changeCHP(dmg_to_apply, self.player, True)

    def spell_dmg(self, cast_level):
        #This function will return the dmg according to Cast Level
        print('No dmg defined for spell: ' + self.spell_name)

    def score(self, fight, twinned_cast=False):
        #This function takes an AOE spell and chooses targets and a cast level
        #It then returns an expactation damage score for the choice class
        #Choose CastLevel:
        if self.is_cantrip: CastLevel = 0
        else:
            CastLevel = self.choose_highest_slot(self.spell_level,9) #Choose highest Spell Slot
            if CastLevel == False: return self.return_0_score()

        #Find suitable targts for this spell
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, self.aoe_area)

        #DMG Score
        Score = self.dmg_score(SpellTargets, CastLevel, SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()  #a little random power
        return Score, SpellTargets, CastLevel

#Specific Spells
#Cantrips
class firebolt(attack_spell):
    def __init__(self, player):
        dmg_type = 'fire'
        self.spell_name = 'FireBolt'
        super().__init__(player, dmg_type)
        self.spell_text = 'fire bolt'
        self.spell_level = 0
        self.is_cantrip = True
        self.is_range_spell = True
        self.is_twin_castable = True
    
    def spell_dmg(self, cast_level):
        self.firebolt_dmg = 0
        if self.player.level < 5:
            self.firebolt_dmg = 5.5
        elif self.player.level < 11:
            self.firebolt_dmg = 5.5*2
        elif self.player.level < 17:
            self.firebolt_dmg = 5.5*3
        else:
            self.firebolt_dmg = 5.5*4
        return self.firebolt_dmg

class chill_touch(attack_spell):
    def __init__(self, player):
        dmg_type = 'necrotic'
        self.spell_name = 'ChillTouch'

        super().__init__(player, dmg_type)
        self.spell_text = 'chill touch'
        self.spell_level = 0
        self.is_cantrip = True
        self.is_range_spell = False
        self.is_twin_castable = True

    def spell_dmg(self, cast_level):
        self.chill_touch_dmg = 0
        #Calculate DMG
        if self.player.level < 5:
            self.chill_touch_dmg = 4.5
        elif self.player.level < 11:
            self.chill_touch_dmg = 4.5*2
        elif self.player.level < 17:
            self.chill_touch_dmg = 4.5*3
        else:
            self.chill_touch_dmg = 4.5*4
        return self.chill_touch_dmg
    
    def cast(self, target, cast_level=0, twinned=False):
        #class cast function returns dealed dmg
        dmg_dealed = super().cast(target, cast_level, twinned)

        if type(target) == list: target = target[0]
        if dmg_dealed > 0:
            target.chill_touched = True
            self.DM.say(str(target.name) + ' was chill touched', True)
    
    def score(self, fight, twinned_cast=False):
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score += SpellTargets[0].heal_given/8 #for the anti heal effect
        Score += SpellTargets[0].start_of_turn_heal #if the target gets heat at start of turn
        return Score, SpellTargets, CastLevel

class eldritch_blast(attack_spell):
    def __init__(self, player):
        dmg_type = 'force'
        self.spell_name = 'EldritchBlast'
        super().__init__(player, dmg_type)

        #Number of attacks at higher level 
        if player.level < 5:
            self.number_of_attacks = 1
        elif player.level < 11:
            self.number_of_attacks = 2
        elif player.level < 17:
            self.number_of_attacks = 3
        else:
            self.number_of_attacks = 4

        self.spell_text = 'eldritch blast'
        self.spell_level = 0
        self.is_cantrip = True
        self.is_range_spell = True
        self.is_twin_castable = False
    
    def spell_dmg(self, cast_level):
        damage = 5.5 #1d10
        #Aganizing Blast
        if self.player.knows_agonizing_blast:
            damage += self.player.modifier[5] #Add Cha Mod
        return damage

    def announce_cast(self):
        super().announce_cast()
        if self.player.knows_agonizing_blast:
            self.DM.say(', Agonizing: ')

#1-Level Spell
class burning_hands(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'BurningHands'
        super().__init__(player, spell_save_type, dmg_type='fire', aoe_area=115) #15ft^2/2
        self.spell_text = 'burning hands'
        self.spell_level = 1
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 10.5 + 3.5*(cast_level-1)   #upcast dmg 3d6 + 1d6 per level over 2
        return damage

class magic_missile(spell):
    def __init__(self, player):
        self.spell_name = 'MagicMissile'
        super().__init__(player)
        self.spell_text = 'magic missile'
        self.spell_level = 1
        self.is_range_spell = True
        self.dmg_type = 'force'
    
    def cast(self, targets, cast_level=False, twinned=False):
        damage = 3.5   #1d4 + 1
        if self.player.empowered_spell:
            damage = damage*1.21
            self.player.empowered_spell = False
            self.DM.say(' Empowered: ')
        super().cast(targets, cast_level, twinned)
        if type(targets) != list: targets = [targets]
        self.hurl_missile(targets, damage)

    def hurl_missile(self, targets, damage):
        missile_counter = 2 + self.cast_level          #overcast mag. mis. for more darts 
        target_counter = 0
        while missile_counter > 0:    #loop for missile cast
            missile_counter -= 1
            Dmg = dmg(damage, 'force')
            #Check for Tokens Trigger
            self.player.TM.hasHitWithAttack(targets[target_counter], Dmg, is_ranged=True, is_spell=True)
            targets[target_counter].TM.washitWithAttack(self.player, Dmg, is_ranged=True, is_spell=True)

            targets[target_counter].last_attacker = self.player    #target remembers last attacker
            targets[target_counter].changeCHP(Dmg, self.player, True)    #target takes damage
            target_counter += 1
            if target_counter == len(targets):    #if all targets are hit once, restart 
                target_counter = 0

    def score(self, fight, twinned_cast=False):
        CastLevel = self.choose_highest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        TargetNumer = CastLevel + 2
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='force') for i in range(0, TargetNumer)]
        if False in SpellTargets:
            return self.return_0_score()

        #DMG Score
        Score = self.dmg_score(SpellTargets, CastLevel, SpellAttack=False)
        Score += 2*CastLevel #a little extra for save hit
        Score = Score*self.random_score_scale() # +/-20% range to vary spells
        return Score, SpellTargets, CastLevel

    def spell_dmg(self, cast_level):
        return 3.5

class guiding_bolt(attack_spell):
    def __init__(self, player):
        dmg_type = 'radiant'
        self.spell_name = 'GuidingBolt'
        super().__init__(player, dmg_type)
        self.spell_text = 'guiding bolt'
        self.spell_level = 1
        self.is_twin_castable = True
        self.is_range_spell = True

    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        dmg_dealed = super().cast(target, cast_level, twinned)

        #On hit:
        if dmg_dealed > 0:
            LinkToken = GuidingBoltedToken(target.TM) #Target gets guiding bolted token
            GuidingBoltToken(self.TM, [LinkToken]) #Timer Dock Token for player
   
    def spell_dmg(self, cast_level):
        return 14 + 3.5*(cast_level-1) #3d10 + 1d10/level > 1

    def score(self, fight, twinned_cast=False):
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        if Score != 0:
            Score += SpellTargets[0].dps()*0.2 #to account for advantage given
        return Score, SpellTargets, CastLevel

class entangle(save_spell):
    def __init__(self, player):
        spell_save_type = 0 #str
        self.spell_name = 'Entangle'
        super().__init__(player, spell_save_type)
        self.spell_text = 'entangle'
        self.spell_level = 1
        self.is_twin_castable = True
        self.is_concentration_spell = True
        self.is_range_spell = True
    
    def cast(self, targets, cast_level=False, twinned=False):
        #Rewrite cast function to be suited for entangle
        #Entangle takes one target, or two if twinned
        if len(targets) > 2 or len(targets) == 2 and twinned == False: 
            print('Too many entangle targets')
            quit()
        if cast_level == False: cast_level = self.spell_level
        self.autorize_cast(cast_level) #self.cast_level now set
        self.player.DM.say(self.player.name + ' casts ' + self.spell_text, True)

        self.EntangleTokens = [] #List for entagle Tokens
        for target in targets:
            self.make_save(target, twinned)  #This triggeres the super class make save function, if failed the take_effect function is called
            #Here self.EntangleTokens is filled with tokens if it takes effect
        if len(self.EntangleTokens) != 0:
            ConcentrationToken(self.TM, self.EntangleTokens)
            #player is concentrating on a Entagled Target or targets

    def take_effect(self, target, twinned):
        EntangleToken = EntangledToken(target.TM, subtype='r') #Target gets a entangled token
        self.EntangleTokens.append(EntangleToken) #Append to list

    def score(self, fight, twinned_cast=False):
        #Find lowest spellslot to cast
        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        TargetNumber = 1
        if twinned_cast: TargetNumber = 2

        TargetChoices = fight.copy() #to remove from
        SpellTargets = []
        for i in range(0,TargetNumber): #choose 1-2 targets
            Target = self.player.AI.choose_att_target(TargetChoices, AttackIsRanged=True, other_dmg=0, other_dmg_type='true', is_silent=True) # Find target for entangle
            if Target == False: return self.return_0_score() #no target
            else:
                SpellTargets.append(Target)
                TargetChoices.remove(Target) #Dont double cast
        Score = 0
        
        for x in SpellTargets:
            Score += x.dps()/4 #disadvantage helps do reduce dmg of enemy
            #Add dmg for the other players
            Score += self.player.spell_dc - 10 - x.modifier[0] #good against weak enemies
            if x.restrained: Score = 0 #Do not cast on restrained targets
        if self.player.knows_wild_shape: Score = Score*1.2 #good to cast before wild shape
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

class cure_wounds(spell):
    def __init__(self, player):
        self.spell_name = 'CureWounds'
        super().__init__(player)
        self.spell_text = 'cure wounds'
        self.spell_level = 1
        self.is_twin_castable = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned) #self.cast_level now set
        heal = 4.5*self.cast_level + self.player.spell_mod
#        self.DM.say(self.player.name + ' touches ' + target.name + ' with magic:')
        target.changeCHP(dmg(-heal, 'heal'), self.player, False)

class healing_word(spell):
    def __init__(self, player):
        self.spell_name = 'HealingWord'
        super().__init__(player)
        self.spell_text = 'healing word'
        self.spell_level = 1
        self.is_twin_castable = True
        self.is_range_spell = True
        self.is_bonus_action_spell = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned) #self.cast_level now set
        heal = 2.5*self.cast_level + self.player.spell_mod
        if heal < 0: heal = 1
#        self.DM.say(self.player.name + ' speaks to ' + target.name)
        target.changeCHP(dmg(-heal, 'heal'), self.player, True)

class hex(spell):
    def __init__(self, player):
        self.spell_name = 'Hex'
        super().__init__(player)
        self.spell_text = 'hex'
        self.spell_level = 1
        self.is_bonus_action_spell = True
        self.is_twin_castable = False
        self.is_range_spell = True
        self.is_concentration_spell = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned)
        HexToken = HexedToken(target.TM, subtype='hex') #hex the Tagret
        self.player.CurrentHexToken = HexingToken(self.TM, HexToken) #Concentration on the caster
        #Assign that Token as the Current HEx Token of the Player

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

        self.DM.say(self.player.name + ' changes the hex to ' + target.name, True)
        self.player.bonus_action = 0 #takes a BA
        self.player.can_choose_new_hex = False
        NewHexToken = HexedToken(target.TM, subtype='hex') #hex the Tagret
        self.player.CurrentHexToken.addLink(NewHexToken) #Add the new Hex Token

    def score(self, fight, twinned_cast=False):
        SpellTarget = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='necrotic', is_silent=True) #Choose best target
        if SpellTarget == False: return self.return_0_score()

        Score = 0
        attacks = self.player.attacks
        if 'EldritchBlast' in self.player.SpellBook:
            Score += 3.5 #A warlock would want to cast hex
            attacks = self.player.SpellBook['EldritchBlast'].number_of_attacks
        Score = 3.5*attacks*(random()*3 + 2) #hex holds for some rounds
        if 'MagicMissile' in self.player.SpellBook:
            Score += 3.5 #Mag Missile Combi

        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTarget, CastLevel 

class hunters_mark(spell):
    def __init__(self, player):
        self.spell_name = 'HuntersMark'
        super().__init__(player)
        self.spell_text = 'hunters mark'
        self.spell_level = 1
        self.is_bonus_action_spell = True
        self.is_twin_castable = False
        self.is_range_spell = True
        self.is_concentration_spell = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned)
        self.DM.say(' at ' + target.name)
        HuntersMarkToken = HuntersMarkedToken(target.TM, subtype='hm') #hunters mark the Tagret
        self.player.CurrentHuntersMarkToken = HuntersMarkingToken(self.TM, HuntersMarkToken) #Concentration on the caster
        #Assign that Token as the Current Hunters Mark Token of the Player

    def announce_cast(self):
        text = ''.join([self.player.name,' casts ',self.spell_text,' at lv.',str(self.cast_level)])
        self.player.DM.say(text, True)

    def change_hunters_mark(self, target):
        rules = [self.player.can_choose_new_hunters_mark,
                self.is_known,
                target.state == 1,
                self.player.bonus_action == 1]
        errors = [self.player.name + ' tried to change a bound hunters mark',
                self.player.name + ' tried to change a hunters mark without knowing it',
                self.player.name + ' tried to change to a not conscious target',
                self.player.name + ' tried to change a hunters mark without having a bonus action']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.player.name + ' changes the hunters mark to ' + target.name, True)
        self.player.bonus_action = 0 #takes a BA
        self.player.can_choose_new_hunters_mark = False
        NewHuntersMarkToken = HuntersMarkedToken(target.TM, subtype='hm') #hunters mark the Tagret
        self.player.CurrentHuntersMarkToken.addLink(NewHuntersMarkToken) #Add the new Token

    def score(self, fight, twinned_cast=False):
        SpellTarget = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type=self.TM.player.damage_type, is_silent=True) #Choose best target
        if SpellTarget == False: return self.return_0_score()

        Score = 0
        attacks = self.player.attacks
        Score = 3.5*attacks*(random()*3 + 2) #hunters mark holds for some rounds
        if 'MagicMissile' in self.player.SpellBook:
            Score += 3.5 #Mag Missile Combi

        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTarget, CastLevel 

class armor_of_agathys(spell):
    def __init__(self, player):
        self.spell_name = 'ArmorOfAgathys'
        super().__init__(player)
        self.spell_text = 'armor of agathys'
        self.spell_level = 1
    
    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        player = self.player
        player.has_armor_of_agathys = True
        TempHP = 5*self.cast_level
        player.agathys_dmg = TempHP
        player.addTHP(TempHP) #add THP to self

    def score(self, fight, twinned_cast=False):
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
        
        Score = 10*CastLevel #does at least 5dmg and 5 TPH for you
        Score = Score*(3 - 2*player.CHP/player.HP) #tripples for low player
        Score -= player.THP*2 #If you still have THP, rather keep it

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel
 
class false_life(spell):
    def __init__(self, player):
        self.spell_name = 'FalseLife'
        super().__init__(player)
        self.spell_text = 'false life'
        self.spell_level = 1
    
    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        TempHP = 1.5 + 5*self.cast_level
        self.player.addTHP(TempHP) #Add the THP

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = [player] #only self cast

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(1,9)
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(1,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        #Score 
        Score = 1.5 + 3*CastLevel  #dmg equal value but for THP, a bit lower then 5
        Score = Score*(3 - 2*player.CHP/player.HP) #tripples for low player
        if player.THP > 0:
            return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

class shield(spell):
    def __init__(self, player):
        self.spell_name = 'Shield'
        super().__init__(player)
        self.spell_text = 'shield'
        self.spell_level = 1
        self.is_reaction_spell = True
    
    def cast(self, target=False, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        self.player.AC += 5
        #Shield does not ware of when unconscious, but I think that is actually correct

    def announce_cast(self):
        super().announce_cast()
        self.DM.say(' ') #for printing in attacks so it fits with next print

class inflict_wounds(attack_spell):
    def __init__(self, player):
        dmg_type = 'necrotic'
        self.spell_name = 'InflictWounds'
        super().__init__(player, dmg_type)
        self.spell_text = 'inflict wounds'
        self.spell_level = 1
        self.is_twin_castable = True
    
    def spell_dmg(self, cast_level):
        return 16.5 + 5.5*(cast_level-1) #3d10 + 1d10/level > 1

#2-Level Spell

class scorching_ray(attack_spell):
    def __init__(self, player):
        dmg_type = 'fire'
        self.spell_name = 'ScorchingRay'
        super().__init__(player, dmg_type)
        self.spell_text = 'scorching ray'
        self.spell_level = 2
        self.is_range_spell = True
    
    def spell_dmg(self, cast_level):
        return 7 #2d6 dmg per ray

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level == False: cast_level = self.spell_level
        self.number_of_attacks = 1 + cast_level
        #Set the number of attacks, then let the super cast function handle the rest
        super().cast(targets, cast_level, twinned)

class aganazzars_sorcher(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'AganazzarsSorcher'
        super().__init__(player, spell_save_type, dmg_type='fire', aoe_area=300) #30ft*10ft 
        self.spell_text = 'aganazzars scorcher'
        self.spell_level = 2
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 13.5 + 4.5*(cast_level-2)   #upcast dmg 3d8 + 1d8 per level over 2
        return damage

class shatter(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 2 #Con
        self.spell_name = 'Shatter'
        super().__init__(player, spell_save_type, dmg_type='thunder', aoe_area=315) #pi*10ft^2
        self.spell_text = 'shatter'
        self.spell_level = 2
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 13.5 + 4.5*(cast_level-2)   #upcast dmg 3d8 + 1d8 per level over 2
        return damage

class spiritual_weapon(spell):
    def __init__(self, player):
        self.spell_name = 'SpiritualWeapon'
        super().__init__(player)
        self.spell_text = 'spiritual weapon'
        self.spell_level = 1
        self.dmg_type = 'force'
    
    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        #remember, if use cast level, use self.cast_level not cast_level
        player = self.player
        player.has_spiritual_weapon = True
        player.SpiritualWeaponDmg = player.spell_mod + 4.5*(self.cast_level -1) 
        player.SpiritualWeaponCounter = 0 #10 Rounds of Weapon

        #If a player cast this spell for the first time, the choice will be aded to the AI
        #The Score function will still check if the player is allowed to use it
        if player.AI.spiritualWeaponChoice not in player.AI.Choices:
            player.AI.Choices.append(player.AI.spiritualWeaponChoice)

        #Attack Once as BA
        if player.bonus_action == 1:
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
        self.DM.say('Spiritual Weapon of ' + player.name + ' attacks: ', True)
        #Make a weapon Attack against first target
        self.player.attack(target, is_ranged=False, other_dmg=WeaponDmg, damage_type='force', tohit=WeaponTohit, is_spell=True)
        self.player.bonus_action = 0 #It uses the BA to attack

    def spell_dmg(self, cast_level):
        return self.player.spell_mod + 4.5*(cast_level - 1)

    def score(self, fight, twinned_cast=False):
        player = self.player

        if player.has_spiritual_weapon:
            return self.return_0_score() #has already sw 

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(2,9) 
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(2,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        #Choose Target for first attack
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=self.spell_dmg(CastLevel), other_dmg_type=self.dmg_type, is_silent=True)]
        if SpellTargets[0] == False:
            return self.return_0_score()#no Enemy in reach


        Score = self.dmg_score(SpellTargets, CastLevel, SpellAttack=True)
        Score = Score*(2 + 2*random()) #expecting to hit with it multiple times
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

#3-Level Spell
class fireball(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'Fireball'
        super().__init__(player, spell_save_type, dmg_type='fire', aoe_area=1250) #pi*20ft**2
        self.spell_text = 'fireball'
        self.spell_level = 3
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 28 + 3.5*(cast_level-3)   #upcast dmg 8d6 + 1d6 per level over 2
        return damage

class lightningBolt(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'LightningBolt'
        super().__init__(player, spell_save_type, dmg_type='lightning', aoe_area=1000) #100ft*10ft
        self.spell_text = 'lightning bolt'
        self.spell_level = 3
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 28 + 3.5*(cast_level-3)   #upcast dmg 3d6 + 1d6 per level over 2
        return damage

class haste(spell):
    def __init__(self, player):
        self.spell_name = 'Haste'
        super().__init__(player)
        self.spell_text = 'haste'
        self.spell_level = 3
        self.is_twin_castable = True
        self.is_concentration_spell = True
        self.is_range_spell = True
    
    def cast(self, targets, cast_level=False, twinned=False):
        if len(targets) > 2 or len(targets) == 2 and twinned == False: 
            print('Too many entangle targets')
            quit()
        super().cast(targets, cast_level, twinned)
        HasteTokens = []
        for target in targets:
            HasteToken = HastedToken(target.TM, subtype='h')
            HasteTokens.append(HasteToken)
            self.DM.say(self.player.name + ' gives haste to ' + target.name, True)
        ConcentrationToken(self.TM, HasteTokens)
        #Player is now concentrated on 1-2 Haste Tokens

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = []
        Choices = [x for x in fight if x.team == player.team and x.state == 1]
        ChoicesScore = [x.dmg*(random()*0.5 +0.5) + x.AC*(random()*0.2 +0.2) + x.CHP/3*(random()*0.2 + 0.1) for x in Choices]
        SpellTargets.append(Choices[argmax(ChoicesScore)]) #append best player for Haste
        if twinned_cast:
            removeIndex = argmax(ChoicesScore)
            Choices.pop(removeIndex) #Dont double haste
            ChoicesScore.pop(removeIndex)
            if len(Choices) == 0: return self.return_0_score()
            SpellTargets.append(Choices[argmax(ChoicesScore)]) #append best player for 2nd Haste

        Score = 0
        for x in SpellTargets:
            Score += x.dmg/2*(random()*3.5 + 0.7) #lasts for some rounds
            Score += x.AC - player.AC #Encourage High AC
            #Dont haste low Ally
            if x.CHP < x.HP/4:
                Score -= x.dmg
            if x.is_summoned: Score = 0 #do not haste summons

        CastLevel = self.choose_smallest_slot(3,9) #smalles slot 
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

class conjure_animals(spell):
    def __init__(self, player):
        self.spell_name = 'ConjureAnimals'
        super().__init__(player)
        self.spell_text = 'conjure animals'
        self.spell_level = 3
        self.is_concentration_spell = True

    def cast(self, fight, cast_level=False, twinned=False):
        #Im am using a trick here, ususally only a target is passed, but this spell needs the fight
        #As a solution the score function of this spell passes the fight as 'targtes' 
        #The cunjured Animals are initiated as fully functunal entity objects
        #The Stats are loaded from the Archive
        #If they reach 0 CHP they will die and not participate in the fight anymore
        #The do_the_fighting function will then pic them out and delete them from the fight list
        super().cast(fight, cast_level, twinned)

        Number, AnimalName = self.choose_animal()
        player = self.player
        #Initiate a new entity for the Animals and add them to the fight
        conjuredAnimals = []
        for i in range(0,Number):
            animal = player.summon_entity(AnimalName, archive=True)
            animal.name = 'Conjured ' + AnimalName + str(i+1)
            self.DM.say(animal.name + ' appears', True)
            animal.summoner = player
            fight.append(animal)

            conjuredAnimals.append(SummenedToken(animal.TM, 'ca')) #add a SummonedToken to the animal
        #Add a Summoner Token to the Player
        SummonerToken(self.TM, conjuredAnimals)

    def choose_animal(self):
        level = 10 #will be set to Beast level for test
        while level > 2:
            Index = int(random()*len(self.player.BeastForms))
            AnimalName = self.player.BeastForms[Index]['Name'] #Random Animal
            level = self.player.BeastForms[Index]['Level'] #Choose a Animal of level 2 or less

        Number = int(2/level)     #8 from CR 1/4, 4 from CR 1/2 ...
        
        if self.cast_level < 5:
            Number = Number
        elif self.cast_level < 7:
            Number = Number*2
        elif self.cast_level < 9: 
            Number = Number*3
        else: 
            Number = Number*4
        
        return Number, AnimalName

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = fight #this is a trick to pass the fight to the spell cast function
        #Okay, the critical level are 3, 5, 7, 9
        #So 4, 6, 8 would be a bit wasted
        TryLevel = [9,7,5,3]
        CastLevel = False
        for x in TryLevel:  #find best slot
            if self.player.spell_slot_counter[x-1] > 0:
                CastLevel = x
                break
        if CastLevel == False:
            CastLevel = self.choose_smallest_slot(x,9)

        if CastLevel == False: return self.return_0_score()  #no slot


        Score = 0 #for now
        if player.has_summons:
            print('Has sommons already')
            quit() #nonsense
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
        Score = TotalCR*6*(random()*2 + 1) #CR * 6dmg/CR * 1-3 Rounds
        if self.player.knows_wild_shape: Score = Score*1.3 #good to cast before wild shape
        return Score, SpellTargets, CastLevel

class call_lightning(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'CallLightning'
        super().__init__(player, spell_save_type, dmg_type='lightning', aoe_area=315) #Are 5ft Radius, but 
        self.spell_text = 'call lightning'
        self.spell_level = 3
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.recast_damge = 0

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level != False: self.recast_damge = self.spell_dmg(cast_level) #set damage for later recast
        else: self.recast_damge = self.spell_dmg(self.spell_level) #level 3 spell
        #Empowered spell does not affect recast, so it checks out 
        super().cast(targets, cast_level, twinned) #Cast Spell as simple AOE once
        #Add Token for late recast
        CallLightningToken(self.TM, [], cast_level) #no links
        #Okay so this has some layers:
        #1. The ClalLightningToken adds the callLightningChoice to the AI (and removes it aswell, when resolved)
        #2. The AI then can use the CallLightningChoice for score and use the Choice to call lighning as recast
        #3. The Choice then uses the players call_lightning spell to recast, which brings it back to this call here
        #Okay not thaaaat many layers, but still

    def recast(self, targets, cast_level=False, twinned=False):
        #Recast the spell laster, if still concentrated
        rules = [self.is_known,
                 self.player.action == 1,
                 self.player.is_concentrating,]
        errors = [self.player.name + ' tried to recast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to recast ' + self.spell_name + 'but has no action left',
                self.player.name + ' tried to recast ' + self.spell_name + 'but is no longer concentrated']
        ifstatements(rules, errors, self.DM).check()
        #Recast for targets
        self.player.action = 0 #uses action
        self.DM.say(self.player.name + ' recasts call lighning', True)
        for target in targets:
            self.make_save_for(target, damage=self.recast_damge) #lets targets make saves and applies dmg
    
    def spell_dmg(self, cast_level):
        dmg = 16.5 + 5.5*(cast_level-3) #3d10 + 1d10 per lv over 3
        return dmg

    def score(self, fight, twinned_cast=False):
        #Modify super score function
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score*(random()*2 + 1) #expecting the spell to last for 1-3 Rounds
        return Score, SpellTargets, CastLevel

#4-Level Spell

class blight(aoe_dmg_spell):
    #has aoe as super class, will be modified for single target
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'Blight'
        super().__init__(player, spell_save_type, dmg_type='necrotic', aoe_area=0) #No AOE
        self.spell_text = 'blight'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_twin_castable = True

    def cast(self, target, cast_level=False, twinned=False):
        if target == list: target = target[0] #mod for single cast
        super().cast(target, cast_level, twinned)

    def make_save_for(self, target, damage):
        #This function is called for every target to make the save and apply the dmg
        #It is only called once, for one target

        #calculate damage manually to account for plants
        damage = 18 + 4.5*(self.cast_level)   #upcast dmg 3d6 + 1d6 per level over 2
        extraAdvantage = 0
        if target.type == 'plant':
            extraAdvantage = -1 #disadvantage for plants
            damage = 32 + 8*self.cast_level #max dmg
            self.DM.say('is plant: ')
        save = target.make_save(self.spell_save_type,DC = self.player.spell_dc, extraAdvantage=extraAdvantage)

        if target.type == 'undead' or target.type == 'construct':
            self.DM.say('Is undead or construct and immune', True)
            self.apply_dmg(target, damage=0) #no effect on this types        
        elif save >= self.player.spell_dc:
            self.apply_dmg(target, damage=damage/2)        
        else: self.apply_dmg(target, damage=damage)
    
    def score(self, fight, twinned_cast=False):
        CastLevel = self.choose_highest_slot(4,9)
        if CastLevel == False: return self.return_0_score()

        self.addedDmg = 0  #is later added for plants, undead and constructs
        dmg = self.spell_dmg(CastLevel)
        Choices = [x for x in fight if x.team != self.player.team]
        SpellTargets = [self.player.AI.choose_att_target(Choices, AttackIsRanged=True, other_dmg = dmg, other_dmg_type=self.dmg_type, is_silent=True)]
        if SpellTargets == [False]: #No Target
            return self.return_0_score()
        if twinned_cast:
            #Secound Target for Twin Cast
            Choices.remove(SpellTargets[0]) #Do not double cast
            twin_target = self.player.AI.choose_att_target(Choices, AttackIsRanged=True, other_dmg = dmg, other_dmg_type=self.dmg_type, is_silent=True)
            if twin_target == False:
                return self.return_0_score()
            SpellTargets.append(twin_target)

        
        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, CastLevel, SpellAttack=False, SpellSave=True)
        Score = Score*1.2 #good to dead focused dmg

        #Creature Type 
        for x in SpellTargets:
            if x.type == 'plant': Score += dmg/1.5
            if x.type == 'undead' or x.type == 'construct': Score -= dmg

        if twinned_cast: Score = Score*2

        Score = Score*self.random_score_scale() # a little random power 
        return Score, SpellTargets, CastLevel

    def spell_dmg(self, cast_level):
        dmg = 36 + 4.5*(cast_level-4) #8d8 + 1d8 for sl lv > 4
        return dmg
    
class sickeningRadiance(aoe_dmg_spell):
    #Not done, recheck
    def __init__(self, player):
        spell_save_type = 2 #Con
        self.spell_name = 'SickeningRadiance'
        super().__init__(player, spell_save_type, dmg_type='poison', aoe_area=2800) #No AOE
        self.spell_text = 'sickening radiance'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.recast_damge = 0

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level != False: self.recast_damge = self.spell_dmg(cast_level) #set damage for later recast
        else: self.recast_damge = self.spell_dmg(self.spell_level) #level 5 spell
        #Empowered spell does not affect recast, so it checks out 
        super().cast(targets, cast_level, twinned) #Cast Spell as simple AOE once
        #Add Token for late recast
        SickeningRadianceToken(self.TM, [], cast_level) #no links

    def make_save_for(self, target, damage):
        #Modified function to account for not taking half dmg on failed save
        #This function is called for every target to make the save and apply the dmg
        save = target.make_save(self.spell_save_type,DC = self.player.spell_dc)
        if save < self.player.spell_dc:
            self.apply_dmg(target, damage=damage)

    def recast(self, targets, cast_level=False, twinned=False):
        #Recast the spell laster, if still concentrated
        rules = [self.is_known,
                 self.player.is_concentrating,]
        errors = [self.player.name + ' tried to recast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to recast ' + self.spell_name + 'but is no longer concentrated']
        ifstatements(rules, errors, self.DM).check()
        #Recast for targets
        self.DM.say(self.player.name + 's sickening radiance is still on the field', True)
        for target in targets:
            self.make_save_for(target, damage=self.recast_damge) #lets targets make saves and applies dmg
    
    def spell_dmg(self, cast_level):
        dmg = 22 #4d10 no upcast improvement
        return dmg

    def score(self, fight, twinned_cast=False):
        #Modify super score function
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score*0.75 #Reduce score, as on save no dmg
        Score = Score*(random()*2 + 1) #expecting the spell to last for 1-3 Rounds
        return Score, SpellTargets, CastLevel

class wallOfFire(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        dmg_type = 'fire'
        aoe_area = 1000 #Higher then it is, but you can shape it to hit many targets
        self.spell_name = 'WallOfFire'
        super().__init__(player, spell_save_type, dmg_type, aoe_area)
        self.spell_text = 'wall of fire'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_concentration_spell = True
    
    def cast(self, targets, cast_level=False, twinned=False):
        #The wall of fire token is designed to that it will not hit the same target twice in a row
        #It will only hit 3 times
        #makes all the checks and saves and dmg
        super().cast(targets, cast_level, twinned)
        protectTarget = self
        dmg = self.spell_dmg(self.cast_level)
        #Protect yourself and one other with W.o.F.
        protectTokenSelf = WallOfFireProtectedToken(protectTarget.TM, 'wf', dmg)
        #Find another player to protect
        #self.player.AI.choose_player_to_protect(fight)
        #Problem here, cant get access to the fight list
        #Fix later
        #protectTokenOther = WallOfFireProtectedToken(protectTarget.TM, 'wf', dmg)
        spellConToken = ConcentrationToken(self.TM, [protectTokenSelf])
        self.DM.say(self.player.name + ' is protected by the wall of fire', True)

    def spell_dmg(self, cast_level):
        dmg = 22.5 + 4.5*(cast_level-4) #5d8 + 1d8/lv > 4
        return dmg
    
    def score(self, fight, twinned_cast=False):
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score + self.spell_dmg(CastLevel)*(1.5*random()+1) #1-3 add hits while concentrated
        if self.player.knows_wild_shape: Score = Score*1.3 #good to cast before wild shape
        return Score, SpellTargets, CastLevel

class polymorph(spell):
    def __init__(self, player):
        self.spell_name = 'Polymorph'
        super().__init__(player)
        self.spell_text = 'polymorph'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.is_twin_castable = True

    def cast(self, targets, cast_level=False, twinned=False):
        if type(targets) != list: targets = [targets]
        if len(targets) > 2 or len(targets) == 2 and twinned == False:
            print('Too many polymorph targets')
            quit()
        super().cast(targets, cast_level, twinned)

        #!!!!!!!!!!!!!!!!Still to do:
        ShapeName = 'TRex'
        ShapeDict = {
            'AC' : 13, 
            'HP' : 136,
            'To_Hit' : 10,
            'Type' : 'beast',
            'Attacks' : 2,
            'DMG' : 26.5,
            'Str' : 25,
            'Dex' : 10,
            'Con' : 19,
            'Int' : 2,
            'Wis' : 12,
            'Cha' : 9,
            'Damage_Type' : 'piercing',
            'Damage_Resistance' : 'none', 
            'Damage_Immunity' : 'none',
            'Damage_Vulnerabilities' : 'none'
        }

        PolymorphTokens = []
        for target in targets:
            PolymorphToken = PolymorphedToken(target.TM, subtype='pm')
            PolymorphTokens.append(PolymorphToken)
            self.DM.say(self.player.name + ' polymorphs ' + target.name + ' into ' + ShapeName, True)
            target.assume_new_shape(ShapeName, ShapeDict, Remark = 'polymorph') #make them assume new shape
            #Reshaping is handled via th ChangeCHP Function or the Concentration Token

        ConcentrationToken(self.TM, PolymorphTokens)
        #Player is now concentrated on 1-2 Polymoph Tokens

    def score(self, fight, twinned_cast=False):
        CastLevel = self.choose_smallest_slot(4,7) #Try to use low slot, higher does not make sense as polymorph does not scale
        if CastLevel == False: return self.return_0_score()

        #target must be conscious, your team and not shape changing
        potentialTargetList = [target for target in fight if target.state == 1 and target.team == self.player.team and target.is_shape_changed == False]
        if len(potentialTargetList) == 0 or (len(potentialTargetList) == 1 and twinned_cast):
            return self.return_0_score() #not enough targets
        
        SpellTargets = [self.choose_polymorph_target(potentialTargetList)]
        if twinned_cast: #choose second target
            potentialTargetList.remove(SpellTargets[0]) #remove the already choosen
            SpellTargets.append(self.choose_polymorph_target(potentialTargetList))

        Score = 0
        Score += 26.5*2*0.7*(random()*2 + 1) #dmg*2 attack + 0.7 projected hit prop. *1-3 rounds
        Score += 50*(1-self.player.CHP/self.player.HP) #add bonus for absorped damage, increases as CHP lower
        if self.player in SpellTargets: Score = Score*1.3 #prefer self to polymorph
        if twinned_cast: Score = Score*2 #twin cast
        if self.player.knows_wild_shape: Score = Score*1.2 #good to cast before wild shape

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def choose_polymorph_target(self, target_list):
        scoreList = [self.polymorph_target_score(target) for target in target_list]
        #evaluate what target is the best to polymorph
        return target_list[argmax(scoreList)]

    def polymorph_target_score(self, target):
        #This Score here is not dmg euqal, becaus I did not know how to gauge it
        Score = 0
        if target.is_shape_changed: return 0
        Score += 100*(1-target.CHP/target.HP) #higher for low HP
        if target == self.player:
            if self.player.CHP < self.player.HP/3:
                Score = Score*1.5 #Cast on self preferably
        if target.heal_given > 0: Score*0.75 #rather dont polymorph healer
        return Score*self.random_score_scale()

#5-Level Spell

class cloudkill(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 2 #Con
        self.spell_name = 'Cloudkill'
        super().__init__(player, spell_save_type, dmg_type='poison', aoe_area=1250) #No AOE
        self.spell_text = 'cloudkill'
        self.spell_level = 5
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.recast_damge = 0

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level != False: self.recast_damge = self.spell_dmg(cast_level) #set damage for later recast
        else: self.recast_damge = self.spell_dmg(self.spell_level) #level 5 spell
        #Empowered spell does not affect recast, so it checks out 
        super().cast(targets, cast_level, twinned) #Cast Spell as simple AOE once
        #Add Token for late recast
        CloudkillToken(self.TM, [], cast_level) #no links

    def recast(self, targets, cast_level=False, twinned=False):
        #Recast the spell laster, if still concentrated
        rules = [self.is_known,
                 self.player.is_concentrating,]
        errors = [self.player.name + ' tried to recast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to recast ' + self.spell_name + 'but is no longer concentrated']
        ifstatements(rules, errors, self.DM).check()
        #Recast for targets
        self.DM.say(self.player.name + 's cloud kill is still on the field', True)
        for target in targets:
            self.make_save_for(target, damage=self.recast_damge) #lets targets make saves and applies dmg
    
    def spell_dmg(self, cast_level):
        dmg = 22.5 + 4.5*(cast_level-5) #5d8 + 1d8 per lv over 5
        return dmg

    def score(self, fight, twinned_cast=False):
        #Modify super score function
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score*(random()*2 + 1) #expecting the spell to last for 1-3 Rounds
        return Score, SpellTargets, CastLevel



