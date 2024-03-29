from random import random, shuffle
import numpy as np
import Choice_class as ch
from functools import partial
from Spell_class import spell

if __name__ == '__main__':
    from Entity_class import entity
              
class AI:
    def __init__(self, player):
    #this class is initialized in the Entity class to controll all the moves and decisions
        self.player = player
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)

        #this is later filled in do_your_turn()
        self.allies = [] #only Allies left alive
        self.dying_allies = []

        #---------TEST---------
        self.Choices = [
            ch.do_attack(player),
            ch.do_offhand_attack(player),
            ch.do_monster_ability(player),
            ch.do_heal(player),
            ch.do_dodge(player)
        ]
        if len(self.player.SpellBook) > 0:
            self.Choices.append(ch.do_spellcasting(player))#if any Spell is known, add this choice option
        if self.player.knows_inspiration:
            self.Choices.append(ch.do_inspire(player))
        if self.player.knows_action_surge:
            self.Choices.append(ch.use_action_surge(player))
        if self.player.knows_turn_undead:
            self.Choices.append(ch.do_turn_undead(player))
        if self.player.knows_wild_shape:
            self.Choices.append(ch.go_wildshape(player))

        #Conditional Choices        
        self.spiritualWeaponChoice = ch.do_spiritual_weapon(player) #This will be later added to the Choices list, if a Character casts spiritual weapon
        self.primalCompanionChoice = ch.attack_with_primal_companion(player) #This Choice is added if a primal companion is summoned
        self.callLightningChoice = ch.do_call_lightning(player) #This Choice is added (and removed later) by the call lightning spell token
        self.dodgeChoice = ch.do_dodge(player) #Is needed as choice for primal companion

        self.conditionalChoicesList = [self.callLightningChoice]

    def do_your_turn(self,fight):
        player = self.player
        self.allies = [x for x in fight if x.team == player.team and x.state != -1]       #which allies
        self.dying_allies = [i for i in self.allies if i.state == 0]     #who is dying

        #stand up if prone
        if player.prone == 1 and not (player.restrained or player.is_stunned or player.is_paralyzed):
            player.stand_up()
        
        #Summon Primal Companion if you have
        if player.knows_primal_companion:
            if player.used_primal_companion == False:
                player.summon_primal_companion(fight)

        #Choosing Aura of Protection Targets:
        if player.knows_aura_of_protection: player.use_aura_of_protection(self.allies)

        #Choose new Hex
        if player.can_choose_new_hex: self.choose_new_hex(fight)
        if player.can_choose_new_hunters_mark: self.choose_new_hunters_mark(fight)

        #Concentration Spells
        if player.is_concentrating:
            self.do_concentration_spells(fight)

        #Use Second Wind
        if player.knows_second_wind and player.has_used_second_wind == False:
            if player.bonus_action == 1:
                if player.CHP/player.HP < 0.3: player.use_second_wind()

        #Interception
        if player.knows_interception:
            self.allies[int(random()*len(self.allies))].interception_amount = 5.5 + player.proficiency

        #------------Not in alternate Shape
        if player.is_shape_changed == False:
        #--------Evaluate Choices
            while (player.action == 1 or player.bonus_action == 1) and player.state == 1:
                EnemiesConscious = [x for x in fight if x.state == 1 and x.team != player.team]
                if len(EnemiesConscious) == 0:
                    player.DM.say('All enemies defeated', True)
                    return #nothing left to do
                
                ChoiceScores = [choice.score(fight) for choice in self.Choices] #get Scores
#                print(ChoiceScores)
#                print(self.Choices)
                ActionToDo = self.Choices[np.argmax(ChoiceScores)]
                if np.max(ChoiceScores) > 0:
                    ActionToDo.execute(fight) #Do the best Choice
                #First Round Action and Attacks
                #Secound Round Bonus Action
                #Check if still smth to do, else return
                if sum(ChoiceScores) == 0:
                    rules = [player.bonus_action == 1 and player.action == 1,
                        player.attack_counter > 0,
                        len([x for x in fight if x.team != player.team and x.state == 1]) == 0]
                    if all(rules):
                        player.DM.say(player.name + ' count not decide what to do!', True)
                        quit()
                    return

        #------------Still in Wild Shape
        elif player.is_in_wild_shape: self.smart_in_wildshape(fight) #Do wild shape stuff
        else: self.smart_in_changed_shape(fight) #Just use your shapes attacks

    def do_concentration_spells(self, fight):
        #This function is called at start of turn if the player has a concentration Spell up
        player = self.player

        #Cloud Kill
        if player.is_cloud_killing:
            #Choose new targets
            targets = self.area_of_effect_chooser(fight, area=1250)
            #What Spell Slot
            for token in self.player.TM.TokenList:
                if token.subtype == 'ck': #cloud kill
                    castLevel = token.castLevel #find cast level
                    break
            #recast cloud kill
            player.SpellBook['Cloudkill'].recast(targets, castLevel)

        #Sickening Radiance
        if player.is_using_sickening_radiance:
            #Choose new targets
            targets = self.area_of_effect_chooser(fight, area=2800)
            #recast cloud kill
            player.SpellBook['SickeningRadiance'].recast(targets)

    def add_choice(self, newChoice):
        #This function is intended to add choices, which are conditional
        #This can happen for spells that enable a choice, via their token mybe
        #It checks for a list of Choices that are expected to be added and removed, does not work for others
        if newChoice not in self.conditionalChoicesList:
            print(self.player + ' tried to add a choice (' + str(newChoice) + ') from AI that is not conditional')
            quit()
        if newChoice in self.Choices:
            print(self.player + ' tried to add a choice (' + str(newChoice) + ') to AI that is already in Choices')
            quit()
        self.Choices.append(newChoice)

    def remove_choice(self, oldChoice):
        #This function is intended to remove choices, which are no longer needed
        #This can happen for spells that enable a choice, if their token is resolved
        #It checks for a list of Choices that are expected to be added and removed, does not work for others
        if oldChoice not in self.conditionalChoicesList:
            print(self.player + ' tried to remove a choice (' + str(oldChoice) + ') from AI that is not conditional')
            quit()
        if oldChoice not in self.Choices:
            print(self.player + ' tried to remove a choice (' + str(oldChoice) + ') from AI that is not in Choices')
            quit()
        self.Choices.remove(oldChoice)

#-----------Smart Actions
    def smart_in_wildshape(self, fight):
        player = self.player
        #This function is called in do_your_turn if the player is still in wild shape
        if self.dying_allies != []:
        #is someone dying
            dying_allies_deathcounter = np.array([i.death_counter for i in self.dying_allies])
            if np.max(dying_allies_deathcounter) > 1:
                if 'CureWounds' in player.SpellBook and sum(player.spell_slot_counter) > 0 and player.bonus_action == 1 and player.raged == False:
                    player.wild_reshape()
                    target = self.dying_allies[np.argmax(dying_allies_deathcounter)]
                    for i in range(0,9):
                        if player.spell_slot_counter[i]>0:
                            player.SpellBook['CureWounds'].cast(target, cast_level=i+1)
                            break  
                    self.do_your_turn(fight) #this then starts the healing part again

        #Heal in combat wild shape
        self.try_wild_shape_heal()
        if player.action == 1:
            ch.do_attack(player).execute(fight)
    
    def try_wild_shape_heal(self):
        player = self.player
        if player.knows_combat_wild_shape and player.bonus_action == 1:
            #if wild shape is low < 1/4
            if player.is_in_wild_shape and player.shape_HP < 10:
                #Still have spell slots?
                MaxSlot = self.choose_highest_slot(1,9)
                if MaxSlot == False: return
                SpellSlot = self.choose_highest_slot(1, MaxSlot - 2) #Dont use high spell slots
                if SpellSlot == False: return #no low slots left
                player.use_combat_wild_shape_heal(spell_level=SpellSlot)

    def smart_in_changed_shape(self, fight):
        player = self.player
        #This function is called in do_your_turn if the player is still in alternate shape
        if player.action == 1:
            ch.do_attack(player).execute(fight)

#---------Reaction and choices
    def do_opportunity_attack(self,target):
        #this function is called when the player can do an attack of opportunity
        if target.knows_cunning_action and target.bonus_action == 1:
            target.use_disengage() #use cunning action to disengage
            return
        else:
            if self.player.has_range_attack: is_ranged = True
            else: is_ranged = False
            self.player.attack(target, is_ranged, is_opportunity_attack = True, is_spell=False)

    def want_to_cast_shield(self, attacker, damage):
        #This function is called in the attack function as a reaction, if Shild spell is known
        if all([self.player.CHP < damage.abs_amount(), self.player.raged == False, self.player.is_shape_changed == False]):
            for i in range(9):
                if self.player.spell_slot_counter[i] > 0:
                    self.player.SpellBook['Shield'].cast(target=False, cast_level=i+1)   #spell level is i + 1
                    break

    def want_to_use_great_weapon_master(self, target, advantage_disadvantage):
        #Is called from the attack function if you can use the great weapon feat
        #take -5 to attack and +10 to dmg
        #advantage_disadvanteage > 0 - advantage, < 0 disadv.

        hitPropability = (20 - target.AC + self.player.tohit)/20
        hitPropabilityGWM = (20 - target.AC + self.player.tohit - 5)/20

        def hitPropabilityAdvantage(hitProp, advantage):
            if advantage > 0: #has to get it once out of two
                return 1 - (1-hitProp)**2
            if advantage < 0:  #disadvantage, has to succ twice
                return hitProp**2
            else: return hitProp

        #Calcualte the expectation value for the dmg
        dmgNoGWM = self.player.dmg*hitPropabilityAdvantage(hitPropability, advantage_disadvantage)
        dmgWithGWM = (self.player.dmg + 10)*hitPropabilityAdvantage(hitPropabilityGWM, advantage_disadvantage)
        if dmgWithGWM >= dmgNoGWM : return True
        else: return False

    def want_to_use_smite(self, target):
        #This function is called if an attack hit
        #It should return False or a spell slot to use smite

        if self.player.dmg > target.CHP: return False #is enough
        if 'radiant' in target.damage_immunity: return False
        return self.choose_highest_slot(1,4) #over lv4 slot does not increase dmg

    def want_to_use_favored_foe(self, target):
        #more here pls
        return True

    def want_to_use_deflect_missiles(self, target, Dmg):
        #determines if player wants to reduce dmg with reaction
        #and if so, if it also wants to return attack if possible
        #Must return two boolean in that order
        wants_to_reduce_dmg = True
        wants_to_return_attack = False

        Score = 5 + self.player.modifier[1] + self.player.ki_points_base #Baseline is the amount of reduction dmg
        x = self.player.CHP / self.player.HP
        Score = Score * (3/(np.exp((x - 0.2)*10) + 1) + 1) #This factor starts at 1, at about 0.4 to 0 CHP/HP it goes steeply to about 3.5
        #We are scaling the likelihood of using reaction based on current HP vs max, making much more likely below 50% hp[add graph of function to docs]
        if Score > self.player.dmg: #compare score to player.dmg as dmg would be dealed at opp.attack
            wants_to_return_attack = True
        if Dmg.abs_amount() >= self.player.CHP:
            wants_to_return_attack = True #If you would die, always use the feature
        return wants_to_reduce_dmg, wants_to_return_attack #return two boolean

#---------Support
    def area_of_effect_chooser(self, fight, area):   #area in square feet
    #The chooser takes all enemies and chooses amoung those to hit with the area of effect
    #every target can only be hit once, regardless if it is alive or dead 
    #how many targets wil be hit depends on the area and the density in that area from the Battlefield.txt
        enemies = [x for x in fight if x.team != self.player.team and x.state != -1]
        DensityFaktor = 2
        if self.player.DM.density == 0: DensityFaktor = 1
        elif self.player.DM.density == 2: DensityFaktor = 3
        target_pool = (area/190)**(1/3)*DensityFaktor - 0.7   #how many enemies should be in that area
        #0 is wide space
        #1 is normal
        #2 is crowded


        if target_pool < 1: target_pool = 1     #at least one will be hit 
        if target_pool < 2 and area > 100 and len(enemies) > 3: 
            if random() > 0.6 - area/500:
                target_pool = 2 #usually easy to hit 2
        elif target_pool == 2 and area > 300 and len(enemies) > 6: target_pool = 3

        if target_pool > len(enemies)*0.8 and len(enemies) > 2: #will rarely hit all
            target_pool = target_pool*0.7
        
        target_pool = target_pool*(random()*0.64 + 0.63) + 0.5 #a little random power 
        target_pool += len(enemies)/12*(0.15 + random()*0.55)

        target_pool = int(target_pool)
        shuffle(enemies)
        if len(enemies) < target_pool:
            targets = enemies
        else:
            targets = enemies[0:target_pool]

        #This returns: 
        # 3 ebemies
        #    115: [1000.    0.    0.    0.    0.    0.    0.    0.    0.    0.]
        #    300: [366. 634.   0.   0.   0.   0.   0.   0.   0.   0.]
        #    450: [145. 767.  88.   0.   0.   0.   0.   0.   0.   0.]
        #    800: [254. 746.   0.   0.   0.   0.   0.   0.   0.   0.]
        #    1250: [ 40. 717. 243.   0.   0.   0.   0.   0.   0.   0.]
        #    4000: [  0. 133. 867.   0.   0.   0.   0.   0.   0.   0.]
        # 4 enemies
        #    115: [521. 393.  86.   0.   0.   0.   0.   0.   0.   0.]
        #    300: [161. 719. 120.   0.   0.   0.   0.   0.   0.   0.]
        #    450: [ 83. 769. 148.   0.   0.   0.   0.   0.   0.   0.]
        #    800: [  0. 463. 537.   0.   0.   0.   0.   0.   0.   0.]
        #    1250: [  0. 213. 512. 275.   0.   0.   0.   0.   0.   0.]
        #    4000: [  0. 125. 472. 403.   0.   0.   0.   0.   0.   0.]


        return targets

    def player_attack_score(self, fight, is_offhand=False):
        #This function return a damage equal value, that should represent the dmg that could be expected form this player if it just attacks
        player = self.player
        Score = 0
        if is_offhand:
            dmg = player.offhand_dmg
            attacks = 1
        else:
            dmg = player.dmg
            attacks = player.attacks

        if is_offhand == False:
            if (player.knows_rage and player.bonus_action == 1) or player.raged == 1:
                dmg += player.rage_dmg
            if player.knows_frenzy:
                attacks += 1
            if player.is_hasted:
                attacks += 1

        if player.knows_reckless_attack:
            dmg = dmg*1.2 #improved chance to hit
        if player.restrained or player.is_blinded or player.is_poisoned: #decreases Chance to hit
            dmg = dmg*0.8
        if player.is_hexing:
            dmg += 2+player.attacks
        if player.is_hunters_marking:
            dmg += 2+player.attacks

        #dmg score is about dmg times the attacks
        #This represents vs a test AC
        TestACs = [x.AC for x in fight if x.team != player.team and x.state != -1]
        if len(TestACs) > 0:
            TestAC = np.mean(TestACs)
        else: TestAC = 16
        Score = dmg*(20 - TestAC + player.tohit)/20*attacks

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

    def choose_att_target(self, fight, AttackIsRanged = False, other_dmg = False, other_dmg_type = False, is_silent = False):
        player = self.player
        if other_dmg == False:
            dmg = player.dmg
        else:
            dmg = other_dmg
        if other_dmg_type == False:
            dmg_type = player.damage_type
        else:
            dmg_type = other_dmg_type
        #function returns False if no target in reach
        #this function takes all targets that are possible in reach and choosed which one is best to attack
        #the AttackIsRanged is to manually tell the function that the Attack is ranged, even if the player might not have ranged attacks, for Spells for example
        EnemiesInReach = player.enemies_reachable_sort(fight, AttackIsRanged)

        if player.dash_target != False:
            if player.dash_target.state == 1:
                #If the Dash Target from last turn is still alive, attack
                return player.dash_target

        if len(EnemiesInReach) == 0:
            if is_silent == False:
                player.DM.say('There are no Enemies in reach for ' + player.name + ' to attack', True)
                player.move_position() #if no target in range, move a line forward
                player.attack_counter = 0
            return False  #return, there is no target
        else:
            target_list = EnemiesInReach
            if self.player.strategy_level < 3:
                return target_list[int(random()*len(target_list))] #if low strategy, attack random
            #This function is the intelligence behind choosing the best target to hit from a List of given Targets. It chooses reguarding lowest Enemy and AC and so on
            ThreatScore = np.zeros(len(target_list))
            for i in range(0, len(target_list)):
                ThreatScore[i] = self.target_attack_score(fight, target_list[i], dmg_type, dmg)
            return target_list[np.argmax(ThreatScore)]

    def target_attack_score(self, fight, target, dmg_type, dmg):
        #This functions helps in decision on a att taget by assining a score
        player = self.player
        Score = 0
        RandomWeight = player.random_weight
        #random factor between 1 and the RandomWeight
        #Random Weight of 0 is no random, should not be 
        #Random Weight around 2 is average 
        
        TargetDPS = target.dps()
        PlayerDPS = player.dps()

        #Immunity
        if dmg_type in target.damage_immunity:
            return 0      #makes no sense to attack an immune target
        #Dmg done by the creature
        Score += TargetDPS*(random()*RandomWeight + 1) #Damage done per round so far
        #How Low the Enemy is
        Score += TargetDPS*(target.HP - target.CHP)/target.HP*(random()*RandomWeight + 1)
        #Heal given
        Score += target.heal_given/player.DM.rounds_number*(random()*RandomWeight + 1)

        #Target is unconscious or can be One Shot
        if player.strategy_level > 5:
            if target.state == 0: #encourage only if strategic
                Score += TargetDPS*2*(random()*RandomWeight + 1)
        elif target.CHP <= dmg: #kill is good, oneshot is better
            Score += TargetDPS*4*(random()*RandomWeight + 1)
        elif dmg > target.HP*2: #Can Instakill
            Score += TargetDPS*5*(random()*RandomWeight + 1)

        #Hit low ACs
        if (target.AC - player.tohit)/20 < 0.2:
            Score += TargetDPS*(random()*RandomWeight + 1)
        elif (target.AC - player.tohit)/20 < 0.35:
            Score += TargetDPS/2*(random()*RandomWeight + 1) #Good to hit 
        #Dont Attack high AC
        if (target.AC - player.tohit)/20 > 0.8: #90% no hit prop
            Score -= TargetDPS*(random()*RandomWeight + 1)

        if player.strategy_level > 4:
            #Attack player with your Vulnerability as dmg
            if target.last_used_DMG_Type in player.damage_vulnerability:
                Score += TargetDPS*(random()*RandomWeight + 1)
            if dmg_type in target.damage_vulnerability:
                Score += TargetDPS*(random()*RandomWeight + 1)
            elif dmg_type in target.damage_resistances:
                Score -= TargetDPS*2*(random()*RandomWeight + 1)

            #Spells
            if player.restrained:
                for x in player.TM.TokenList:
                    if x.type == 'r' and x.origin == target:
                        Score += PlayerDPS*2*(random()*RandomWeight + 1) #This player is entangling you 
            if player.is_hexing: #Check for hexing
                for HexedToken in player.CurrentHexToken.links:
                    if HexedToken.TM.player == target:
                        Score += (TargetDPS + 3.5)*(random()*RandomWeight + 1) #Youre hexing this player
            if player.is_hunters_marking: #Check for hunters Mark
                for Token in player.CurrentHuntersMarkToken.links:
                    if Token.TM.player == target:
                        Score += (TargetDPS + 3.5)*(random()*RandomWeight + 1) #Youre hexing this player

        if target.is_concentrating: Score += TargetDPS/3*(random()*RandomWeight + 1)
        if target.has_summons: Score += TargetDPS/2*(random()*RandomWeight + 1)
        if target.has_armor_of_agathys: Score -= PlayerDPS/3*(random()*RandomWeight + 1)

        if target.restrained or target.prone or target.is_blinded or target.is_stunned or target.is_paralyzed: #Attack with advantage
            Score += TargetDPS/4*(random()*RandomWeight + 1)
        if target.is_dodged: Score -= dmg/5*(random()*RandomWeight + 1)

        #Wild shape, it is less useful to attack wildshape forms
        if target.is_shape_changed and target.knows_combat_wild_shape == False:
            Score = Score*0.8*(random()*RandomWeight + 1)
        if target.shape_HP <= dmg:
            Score = Score*1.4*(random()*RandomWeight + 1)

        #this whole part took too long in performance
        # NeedDash = player.need_dash(target, fight)
        # if NeedDash == 1 and player.knows_cunning_action == False:
        #     Score -= PlayerDPS/1.3*(random()*RandomWeight + 1)
        #     #Player cant attack this turn if dashed
        # elif NeedDash == 1 and player.knows_cunning_action:
        #     Score -= dmg/2*(random()*RandomWeight + 1)
        # elif NeedDash == 1 and player.knows_eagle_totem:
        #     Score -= dmg/2*(random()*RandomWeight + 1)
        #     #With cunning action/eagle totem less of a Problem
        # if player.will_provoke_Attack(target, fight):
        #     if player.knows_eagle_totem:
        #         Score -= PlayerDPS/6*(random()*RandomWeight + 1)
        #     elif player.CHP > player.HP/3: 
        #         Score -= PlayerDPS/4*(random()*RandomWeight + 1)
        #     else: 
        #         Score -= PlayerDPS/2*(random()*RandomWeight + 1)

        #Line Score, Frontliner will go for front and mid mainly
        if player.position == 0: #front
            if target.position == 0: Score = Score*1.4
            elif target.position == 1: Score = Score*1.2
            elif target.position == 2: Score = Score*0.8
        elif player.position == 1: #Mid
            if target.position == 0: Score = Score*1.4
            elif target.position == 1: Score = Score*1.3
            elif target.position == 2: Score = Score*1.1
            elif target.position == 3: Score = Score*1.1
        elif player.position == 2: #Back
            if target.position == 2: Score = Score*1.3
            elif target.position == 3: Score = Score*1.4
        elif player.position == 3: #Airborn
            if target.position == 2: Score = Score*1.3
        
        if target.is_a_turned_undead:
            Score = Score/4 #almost no threat at the moment
        return Score

    def spell_cast_check(self, spell):
        player = self.player
        #This function checks if a given Spell is castable for the player by any means, even with quickened Spell
        #False - not castable
        #1 - castable
        #2 - only Castable via QuickenedSpell
        if spell.is_known == False:
            return False
        #Check if Player has spellslots
        if spell.spell_level > 0:
            good_slots = sum([1 for i in range(spell.spell_level - 1,9) if player.spell_slot_counter[i] > 0])
            if good_slots == 0:
                return False
        
        if player.raged:
            return False
        if player.is_in_wild_shape:
            return False
        elif spell.is_concentration_spell and player.is_concentrating:
            return False
        elif spell.is_reaction_spell:
            return False   #reaction Spell in own turn makes no sense
        elif spell.is_cantrip == False and player.has_cast_left == False:
            return False


        #Action Check
        if spell.is_bonus_action_spell and player.bonus_action == 1:
            if spell.is_cantrip:
                return 1         #have BA, is cantrip -> cast 
            elif player.has_cast_left:
                return 1        #have BA, is spell, have caste left? -> cast
            else:
                return False    #cant cast, have already casted
        elif spell.is_bonus_action_spell == False:
            if player.action == 1:
                if spell.is_cantrip:
                    return 1 #have action and is cantrip? -> cast
                elif player.has_cast_left:
                    return 1 #have action and cast left? -> cast
                else:
                    return False
            elif player.bonus_action == 1 and player.knows_quickened_spell and player.sorcery_points >= 2:
                if spell.is_cantrip:
                    return 2  #Cast only with Quickened Spell
                elif player.has_cast_left:
                    return 2  #have cast left?
                else:
                    return False
            else:
                return False
        else:
            return False

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

    def choose_player_to_protect(self, fight):
        #Chooses one other allies, that is not self, which might be unconsious
        player = self.player
        allies = [x for x in fight if x.team == player.team and x.state != -1 and x != player]       #which allies left alive
        if len(allies) == 0: return False #no allies

        AllyScore = []
        for ally in allies:
            AllyScore.append(self.ally_score(ally)) #get score

        #Return Ally with lowest SCore        
        return allies[np.argmin(AllyScore)]

    def ally_score(self, fight, ally):
        #The higher the score, the less likely this player needs protection
        Score = 0
        Score += ally.AC #Low AC?
        Score += ally.AC*ally.CHP/ally.HP #Low on HP?
        Score += ally.HP/10
        if ally.state == 0: Score = Score*0.5
        conditions = [
            ally.is_blinded, ally.is_stunned, ally.is_incapacitated, ally.is_paralyzed
        ]
        if any(conditions): Score*0.5
        if ally.is_shape_changed: Score = Score*3
        if ally.is_concentrating: Score = (Score- 5)/2
        Score = Score*(1 + random()*(10/self.player.strategy_level - 1)/3) #randomness from strategy
        return Score

#---------Spells
    def choose_quickened_cast(self):
        #This function is called once per trun to determine if player wants to use quickned cast this round
        player = self.player
        QuickScore = 100
        QuickScore = QuickScore*(1.5 - 0.5*(player.CHP/player.HP)) #encourage quickend cast if youre low, if CHP -> 0, Score -> 150
        if player.has_cast_left: QuickScore = QuickScore*1.4    #encourage if you havend cast yet
        if player.sorcery_points < player.sorcery_points_base/2: QuickScore = QuickScore*0.9 #disencourage for low SP
        elif player.sorcery_points < player.sorcery_points_base/3: QuickScore = QuickScore*0.8
        elif player.sorcery_points < player.sorcery_points_base/5: QuickScore = QuickScore*0.7
        if player.restrained: QuickScore = QuickScore*1.1  #Do something against restrained
        #Random Power for quickened Spell
        QuickScore = QuickScore*(0.65 + random()*0.7) #+/- 35%
        if QuickScore > 100:
            return True
        else:
            return False

    def choose_spell(self, fight):
        #This function chooses a spell for the spell choice
        #If this function return False, spellcasting is not an option for this choice
        player = self.player
        SpellChoice = False

        #Check the absolute Basics
        if player.action == 0 and player.bonus_action == 0:
            return False, 0
        if player.raged == 1:
            return False, 0   #cant cast while raging

        Choices = []

        #Check Spells
        for x, spell in player.SpellBook.items():
            Checkvalue = self.spell_cast_check(spell) #check if castable
            if Checkvalue == 1: #Check, Spell is castable
                Choices.append(spell.cast)
                #Check if Twin cast is an option
            if all([Checkvalue == 1, spell.is_twin_castable, player.knows_twinned_spell, player.sorcery_points > spell.spell_level, player.sorcery_points > 1]):
                Choices.append(spell.twin_cast)
            elif Checkvalue == 2: #Spell is only castable via quickened spell
                Choices.append(spell.quickened_cast)

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

        #In the following all Options will get a score, that roughly resembles their dmg or equal dmg value
        #This Score is assigned by a function of the spellcasting class 
        #This function also evalues if it is good to use a quickened or twin cast
        #The evaluation of quickened Cast is currently not handled by these functions
            for x, spell in player.SpellBook.items():
                if Choice == spell.cast:
                    Score, SpellTargets, CastLevel = spell.score(fight)
                elif Choice == spell.quickened_cast:
                    if cast_quickened_this_round == True:
                        Score, SpellTargets, CastLevel = spell.score(fight)
                    else:
                        #Basically dont cast quickened this round
                        Score = 0
                        SpellTargets = [player]
                        CastLevel = 0
                elif Choice == spell.twin_cast:
                    Score, SpellTargets, CastLevel = spell.score(fight, twinned_cast=True)
            ChoiceScores[i] = Score
            TargetList[i] = SpellTargets
            LevelList[i] = CastLevel
        #Now find best value and cast that
        ChoiceIndex = np.argmax(ChoiceScores)

        #Before returning the Value check if it is even sensable to cast instaed of doing something else
        #This part gives a Value of the possible alternatives and assignes a dmg equal value to compare with
        #This is the Score that will be compared for the action Spell, so assume an action is left
        if player.action == 1:
            #If the player has still its action, compete with this alternative score of just attacking
            if np.max(ChoiceScores) > player.dmg/4:
                SpellChoice = partial(Choices[ChoiceIndex],TargetList[ChoiceIndex],LevelList[ChoiceIndex])
                return SpellChoice, ChoiceScores[ChoiceIndex]
            else:
                return False, 0 #If you have action and cant beat this Score, dont cast spell
        elif player.bonus_action == 1:
            if np.max(ChoiceScores) > player.dmg/5 + 1:    #just a small threshold
                    SpellChoice = partial(Choices[ChoiceIndex],TargetList[ChoiceIndex],LevelList[ChoiceIndex])
                    return SpellChoice, ChoiceScores[ChoiceIndex]
            else:
                return False, 0
        else: return False, 0

    def choose_heal_target(self, fight):
        #This function is called if the player has heal
        #It returns the best Target for a heal and gives the Heal a Score
        #If False is returned, Heal will not be added as a Choice for this turn
        player = self.player
        if self.dying_allies != []:      #someone is dying
            DyingScore = []
            for ally in self.dying_allies:
                Score = ally.dps()*ally.death_counter #High Score for a high death_counter
                Score += ally.value()
                Score = Score*0.7*(0.8+random()*0.4) #little random power
                #The Score will be returned as a Score for the Choices in do_your_turn too
                DyingScore.append(Score)
            MaxIndex = np.argmax(DyingScore)
            Target = self.dying_allies[MaxIndex]
            return Target, DyingScore[MaxIndex]
        #No One is currently dying
        else:
            TeamHP = sum([x.HP for x in self.allies])
            TeamCHP = sum([x.CHP for x in self.allies])
            if TeamCHP/TeamHP < 0.7:
                HealScores = []
                for ally in self.allies:
                    Score = ally.value()*2/3 #Player is not dead, might still do another round
                    Score = Score*(1 - ally.CHP/ally.HP) #Score Scales with CHP left
                    Score = Score*(0.8+random()*0.4)
                    if ally.CHP/ally.HP > 0.6:
                        Score = 0
                    HealScores.append(Score)
                MaxIndex = np.argmax(HealScores)
                if HealScores[MaxIndex] > player.value()/3: #Minimum Boundry for reasonable heal
                    return self.allies[MaxIndex], HealScores[MaxIndex]
                else:
                    return False, 0
            else:
                return False, 0

    def choose_heal_spellslot(self, MinLevel = 1):
        player = self.player
        SpellPower = sum([player.spell_slot_counter[i]*np.sqrt((i + 1)) for i in range(0,9)])
        MaxSlot = 0 # Which is the max spell slot left
        for i in reversed(range(0,9)):
            if player.spell_slot_counter[i] > 0:
                MaxSlot = i + 1
                break

        TestLevel = int(SpellPower/5 + 1.5)
        if TestLevel == MaxSlot:
            #Never use best slot to heal
            TestLevel -= 1
        
        #Use the TestLevel Slot or the next best lower then it
        LowLevel = self.choose_highest_slot(1,TestLevel)
        if LowLevel != False:
            return LowLevel
        #if no low level left, try higher
        HighLevel = self.choose_smallest_slot(TestLevel+1,9)
        if HighLevel != False:
            return HighLevel
        return False

    def choose_new_hex(self, fight):
        HexChoices = [x for x in fight if x.team != self.player.team and x.state == 1]
        HexTarget = self.choose_att_target(HexChoices, AttackIsRanged=True, other_dmg=3.5, is_silent=True)
        if HexTarget != False and self.player.bonus_action == 1:
            self.player.SpellBook['Hex'].change_hex(HexTarget)

    def choose_new_hunters_mark(self, fight):
        HuntersMarkChoices = [x for x in fight if x.team != self.player.team and x.state == 1]
        Target = self.choose_att_target(HuntersMarkChoices, AttackIsRanged=True, other_dmg=3.5, is_silent=True)
        if Target != False:
            self.player.SpellBook['HuntersMark'].change_hunters_mark(Target)