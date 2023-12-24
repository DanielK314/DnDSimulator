import numpy as np
from random import random

if __name__ == '__main__':
    from Entity_class import entity

class choice:
    def __init__(self, player):
        self.player = player
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)
  
class do_attack(choice):
    def __init__(self, player):
        super().__init__(player)
        self.is_offhand = False
    
    def score(self, fight):
        #This function return a damage equal value, that should represent the dmg that could be expected form this player if it just attacks
        player = self.player
        Score = 0
        #No attack possible return 0
        #Action Attack:
        if self.is_offhand == False:
            if player.action == 0: return 0
            elif player.attack_counter < 1: return 0
            dmg = player.dmg
            attacks = player.attacks
            if (player.knows_rage and player.bonus_action == 1) or player.raged == 1:
                dmg += player.rage_dmg
            if player.knows_frenzy:
                attacks += 1
            if player.is_hasted:
                attacks += 1

        #Offhand Attack
        else:
            if player.is_attacking == False: return 0 #didnt attack in action
            dmg = player.offhand_dmg
            attacks = 1
            if dmg == 0: return 0  #no offhand attack if dmg = 0
        
        if player.knows_reckless_attack:
            dmg = dmg*1.2 #improved chance to hit
        if player.restrained or player.is_blinded or player.is_poisoned:
            dmg = dmg*0.8
        if player.is_hexing:
            dmg += 3.5

        #dmg score is about dmg times the attacks
        #This represents vs a test AC
        TestACs = [x.AC for x in fight if x.team != player.team and x.state != -1]
        if len(TestACs) > 0:
            TestAC = np.mean(TestACs)
        else: TestAC = 16
        if TestAC > 20: TestAC = 20 #if one has rediculous high armor
        Score = dmg*(20 - TestAC + player.tohit)/20*attacks

        #Only on one Attack 
        if player.sneak_attack_counter == 1:
            Score += player.sneak_attack_dmg
        if player.wailsfromthegrave_counter > 0:
            Score += player.sneak_attack_dmg/2
        if player.knows_great_weapon_master and self.is_offhand == False:
            Score += 5  #+10 dmg, but no great hit prop
        if player.knows_archery: Score += dmg*0.1 #better hit chance
        if player.knows_great_weapon_fighting: dmg += dmg*0.1 #more dmg
        if player.knows_improved_critical: dmg += dmg*0.1 #better crit
        if player.knows_smite:
            for i in range(0,5):
                if player.spell_slot_counter[4-i] > 0:
                    Score += (4-i)*4.5  #Smite Dmg once
                    break

        #Other Stuff
        if player.dash_target != False: #Do you have a dash target?
            if player.dash_target.state == 1: Score*1.5 #Encourage a Dash target attack
        if player.has_range_attack == False:
            Score = Score*np.sqrt(player.AC/(13 + player.level/3.5)) #Encourage player with high AC
        if Score < 0: Score = 0
        return Score

    def execute(self, fight):
        player = self.player
        #This function then actually does the attack<<
        if player.action == 1: #if nothing else, attack
            if player.knows_reckless_attack:
                player.rackless_attack()
            if player.knows_rage and player.bonus_action == 1 and player.raged == 0:
                player.rage() #includes frenzy
            if player.is_in_frenzy and player.bonus_action == 1:
                player.use_frenzy_attack()
            while player.attack_counter > 0 and player.state == 1:  #attack enemies as long as attacks are free and alive (attack of opportunity might change that)
                target = player.AI.choose_att_target(fight) #choose a target
                if target == False: #there might be no target
                    return
                else:
                    player.make_normal_attack_on(target, fight)  #attack that target

class do_offhand_attack(do_attack):
    def __init__(self, player):
        super().__init__(player)
        self.is_offhand = True
    
    def score(self, fight):
        return super().score(fight)

    def execute(self, fight):
        player = self.player
        #This function does a offhand attack as BA
        if player.bonus_action == 1:
            if player.knows_reckless_attack:
                player.rackless_attack()
            target = player.AI.choose_att_target(fight) #choose a target
            if target == False: #there might be no target
                return
            else:
                player.make_normal_attack_on(target, fight, is_off_hand=True)  #attack that target

class do_dodge(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        if self.player.action == 0: return 0
        else: return 1  #For now
    
    def execute(self, fight):
        self.player.use_dodge()

class do_inspire(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        Score = 0
        if self.player.inspiration_counter == 0: return 0
        if self.player.knows_inspiration == False: return 0
        if self.player.bonus_action != 1: return 0
        if random() > 0.2: Score = self.player.level*2
        if self.player.knows_cutting_words and self.player.inspiration_counter == 1:
            Score = Score/2 #keep last inspiration
        return Score
    
    def execute(self, fight):
        rules = [self.player.knows_inspiration, 
                self.player.inspiration_counter > 0,
                self.player.bonus_action == 1]
        if all(rules):
            allies = [x for x in fight if x.team == self.player.team]
            self.player.inspire(allies[int(random()*len(allies))])

class go_wildshape(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        player = self.player
        if player.knows_wild_shape == False: return 0
        if player.is_shape_changed: return 0
        if player.wild_shape_uses < 1: return 0
        if player.action == 1 or (player.bonus_action == 1 and player.knows_combat_wild_shape):
            Score = player.DruidCR*6*(2 + random()) #CR * about 6 dmg/CR * 2-3 Rounds
            Score += player.HP/(player.CHP + player.HP/4)*Score   #if low on HP go wild shape
            #Up to 4 times the score if very low
            if player.knows_combat_wild_shape:
                Score = Score*1.2  #if you know combat wild shape freaking go
            if player.is_concentrating: Score = Score*1.3 #is really good to go into wild shape with a con spell
            return Score
        else: return 0
    
    def execute(self, fight):
        player =self.player 
        rules = [player.knows_wild_shape,
                player.wild_shape_uses > 0,
                player.is_shape_changed == False,
                player.action == 1 or (player.bonus_action == 1 and player.knows_combat_wild_shape)]
        if all(rules):
            #Check smaller and smaller Margins until you find a suitable but still High Creature
            ChoiceIndex = False
            for i in range(1,5):
                Choices = self.find_forms(1 - i/5)
                if Choices != []:
                    Index = int(random()*len(Choices)) #Random Choice of those available
                    ChoiceIndex = Choices[Index] #Thats the Form Choosen
                    break
            self.player.wild_shape(ChoiceIndex)

    def find_forms(self, Margin):
        #This function returns an Index List for the Beast Forms
        #The returned forms are smaller then Cr but highter then Margin*CR
        #Marget like 80% from CRmax: 0.8
        BeastForms = self.player.BeastForms
        FormList = [i for i in BeastForms if BeastForms[i]['Level'] <= self.player.DruidCR and BeastForms[i]['Level'] >= self.player.DruidCR*Margin]
        return FormList        

class use_action_surge(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        if self.player.knows_action_surge == False: return 0
        if self.player.action_surge_counter == 0: return 0
        if self.player.action_surge_used: return 0
        if self.player.action == 1: return 0 #no use if action is 1
        if self.player.CHP/self.player.HP < 0.6:
            return self.player.dps() #action surge is good and cost nothing
        return 0
    
    def execute(self, fight):
        self.player.use_action_surge()
        self.player.AI.do_your_turn(fight) #use action surge and start turn again

class do_spiritual_weapon(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        if self.player.has_spiritual_weapon == False: return 0
        if self.player.bonus_action == 0: return 0
        return self.player.SpiritualWeaponDmg
    
    def execute(self, fight):
        player = self.player
        target = player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=player.SpiritualWeaponDmg, other_dmg_type='force', is_silent=True)
        if target != False:
            player.SpellBook['SpiritualWeapon'].use_spiritual_weapon(target)
        else: player.bonus_action = 0

class do_turn_undead(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self,fight):
        if self.player.knows_turn_undead == False: return 0
        if self.player.channel_divinity_counter < 1: return 0
        if self.player.action == 0: return 0

        Score = sum([x.dps() for x in fight if x.type == 'undead' and x.state == 1])
        if 'undead' in [x.type for x in fight if x.team == self.player.team]:
            #dont use if teammates undead
            Score = 0
        return Score

    def execute(self,fight):
        targets = self.player.AI.area_of_effect_chooser(fight, 2500)
        self.player.use_turn_undead(targets)

class do_spellcasting(choice):
    def __init__(self, player):
        super().__init__(player)
        self.SpellScore = 0
        self.ChoosenSpell = False
    
    def score(self, fight):
        player = self.player
        self.SpellScore = 0
        self.ChoosenSpell = False

        if len(player.SpellBook) > 0:# check if player knows any spells
            if player.bonus_action == 1 or player.action == 1: #if you have still action left 
                #print(self.choose_spell(fight))
                self.ChoosenSpell, self.SpellScore = player.AI.choose_spell(fight)
        return self.SpellScore
    
    def execute(self, fight):
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
            Score = Score*(random()/2 + 0.75)
            if Score > 10:
                player.use_empowered_spell()
        if self.ChoosenSpell != False:
            self.ChoosenSpell() #cast choosen Spell

class use_ki(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        player = self.player
        if player.ki_points == 0: return 0
        Score = 0

        # if player.

    def execute(self, fight):
        player = self.player

    #ki point priority in descending order of score/priority: stunning strike (prioritize strong enemy), flurry of blows (if have open hand technique, ++score, prob always before stunning strike), deflect missiles (conditional, see entity class), step of the wind, patient defense

class do_monster_ability(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        player = self.player
        if player.action == 0: return 0
        Score = 0

        if player.dragons_breath_is_charged:
            Score += (20 + int(player.level*3.1))*3   #damn strong ability, at least 2-3 Targets
        if player.recharge_aoe_is_charged:
            Score += player.aoe_recharge_dmg*2 #might hit 2-3 targts
        if player.spider_web_is_charged:
            Score += player.dmg*player.attacks*1.5   #good Ability, better then simple attack
        return Score
    
    def execute(self, fight):
        player = self.player
        if player.knows_recharge_aoe and player.action == 1:
            if player.recharge_aoe_is_charged:
                self.recharge_aoe(fight)
        #Dragon Breath
        if player.knows_dragons_breath and player.action == 1:
            if player.dragons_breath_is_charged:
                self.dragons_breath(fight)
        #Spider Web
        if player.knows_spider_web and player.action == 1:
            if player.spider_web_is_charged:
                self.spider_web(fight)

    def recharge_aoe(self, fight):
        player = self.player
        targets = player.AI.area_of_effect_chooser(fight, player.aoe_recharge_area)
        if len(targets) == len([x for x in fight if x.team != player.team]) and len(targets) > 1:
            max = int(len(targets)*0.5 + 0.5) #some should be able to get out, even for high area of effect
            targets = targets[0:-1*max]
        player.use_recharge_aoe(targets)

    def dragons_breath(self, fight):
        player = self.player
        if player.level < 10: area = 250
        elif player.level < 15: area = 450 
        elif player.level < 20: area = 1800 #60-ft-cone
        else: area = 4000 #90-ft-cone
        targets = player.AI.area_of_effect_chooser(fight, area)
        if len(targets) == len([x for x in fight if x.team != player.team]) and len(targets) > 1:
            max = int(len(targets)*0.5 + 0.5) #some should be able to get out, even for high are of effect
            targets = targets[0:-1*max]
        player.use_dragons_breath(targets)
    
    def spider_web(self, fight):
        player = self.player
        enemies_left = [x for x in fight if x.team != player.team and x.state == 1]
        #Random Target
        if len(enemies_left) > 0:
            player.use_spider_web(enemies_left[int(random()*len(enemies_left))])
        else:
            #No enemies left
            player.action = 0 #use acrion, nothing left to attack

class attack_with_primal_companion(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        if self.player.primal_companion == False: return 0
        companion = self.player.primal_companion
        if companion.state != 1: return 0
        if self.player.bonus_action == 0: return 0
        if self.player.primal_companion.action == 0: return 0
        if self.player.primal_companion.attack_counter <= 0: return 0
        return (companion.dmg + companion.value())/2*companion.attacks
    
    def execute(self, fight):
        companion = self.player.primal_companion
        rules = [
            companion != False,
            companion.attack_counter > 0,
            companion.action == 1,
            companion.state == 1,
            self.player.bonus_action == 1
        ]
        if all(rules):
            while companion.attack_counter > 0 and companion.state == 1:  #attack enemies as long as attacks are free and alive (attack of opportunity might change that)
                target = companion.AI.choose_att_target(fight) #choose a target
                if target == False: #there might be no target
                    return
                else:
                    companion.make_normal_attack_on(target, fight)  #attack that target
            self.player.bonus_action = 0

class do_heal(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        player = self.player
        self.has_heal = False
        self.HealTarget = False

        #Check for heal
        if player.lay_on_hands_counter > 0 and player.action == 1:
            self.has_heal = True
        if 'CureWounds' in player.SpellBook:
            if player.AI.spell_cast_check(player.SpellBook['CureWounds']) != False:
                self.has_heal = True
        if 'HealingWord' in player.SpellBook:
            if player.AI.spell_cast_check(player.SpellBook['HealingWord']) != False:
                self.has_heal = True

        if self.has_heal == False: return 0
        else:
            #if the player has heal, check what target would be good
            self.HealTarget, HealScore = self.choose_heal_target(fight)
            if player.CHP < player.HP/4: HealScore += player.value()/3 #encourage if low
            if self.HealTarget != False: return HealScore
            else: return 0

    def choose_heal_target(self, fight):
        #This function is called if the player has heal
        #It returns the best Target for a heal and gives the Heal a Score
        #If False is returned, Heal will not be added as a Choice for this turn
        player = self.player
        self.allies = [x for x in fight if x.team == player.team and x.state != -1]
        self.dying_allies = [x for x in self.allies if x.state == 0]
        if self.dying_allies != []:      #someone is dying
            DyingScore = []
            for ally in self.dying_allies:
                Score = ally.dps()*ally.death_counter #High Score for a high death_counter
                Score += ally.value()
                Score = Score*0.7*(0.8+random()*0.4) #little random power
                if ally.chill_touched: Score = 0 #can not be healed
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

    def execute(self, fight):
        #This function is called as an AI Coice
        #If it is is called there should be a heal option aviable for the player
        #Also the Choose Heal Target function should already assigned a heal target
        #The only thing to choose now is what king of Healing and how much, which SpellSlot 
        player = self.player
        target = self.HealTarget

        #self is low, heal yourself instead if target
        if player.CHP < int(player.HP/4) and player.lay_on_hands_counter > player.lay_on_hands/2 and player.action == 1:
            player.use_lay_on_hands(player, player.lay_on_hands_counter - int(player.lay_on_hands_counter/5))
            return

        #Choose Heal
        HealingWordValue = 0
        CureWoundsValue = 0
        if 'HealingWord' in player.SpellBook:
            HealingWordValue = player.AI.spell_cast_check(player.SpellBook['HealingWord'])
        if 'CureWounds' in player.SpellBook:
            CureWoundsValue = player.AI.spell_cast_check(player.SpellBook['CureWounds'])
        level = self.player.AI.choose_heal_spellslot(MinLevel=1)
        if HealingWordValue == 1: #HealingWord is castable
            player.SpellBook['HealingWord'].cast(target, cast_level=level)
        elif player.lay_on_hands_counter > 0 and player.action ==1:
            player.use_lay_on_hands(target, 5)
        elif CureWoundsValue == 1: #HealingWord is castable
            player.SpellBook['CureWounds'].cast(target, cast_level=level)
        elif HealingWordValue == 2: #HealingWord via Quickened Spell
            player.SpellBook['HealingWord'].quickened_cast(target, cast_level=level)
        elif CureWoundsValue == 2: #HealingWord via Quickened Spell
            player.SpellBook['CureWounds'].quickened_cast(target, cast_level=level)
        else:
            #This should not happen
            print('This is stupid, no Heal in AI, check do_heal class')
            quit() 

#Still work to do:
class do_call_lightning(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        #This Score only apllies to the re-casting of the Spell, not the initial cast
        #Tis is the reason why this score is rather generously calculated, to encourage using this
        if self.player.action == 0: return 0
        recastDmg = self.player.SpellBook['CallLightning'].recast_damge  #recast dmg saved in spell at the last cast
        Score = 0
        Score = recastDmg*(1.5+random()) #dmg*1.5-2.5 targets
        Score += 10 #a little bonus to encourage recasting this, because it does not cost extra cast
        return Score
    
    def execute(self, fight):
        #Use action to recast spell
        player = self.player
        area = self.player.SpellBook['CallLightning'].aoe_area
        #Choose Targets
        targets = self.player.AI.area_of_effect_chooser(fight, area=area)

        self.player.SpellBook['CallLightning'].recast(targets) #recast, sets action = 0


