from Ifstatement_class import ifstatements
from Dmg_class import dmg
from random import *
import numpy as np

if __name__ == '__main__':
    from Entity_class import entity

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
