if __name__ == '__main__':
    from Entity_class import entity

from Dmg_class import *
#Types:
#con - concentration
#l - Link

#subtypes that change an attribute
    #r - restrained
    #st - stunned
    #ic - incapacitated
    #pl - paralysed
    #bl - blinded
    #ps - poisoned
    #iv - invisible

    #h - haste
    #hex - is hexed
    #hexn - is hexing
    #hm - is hunters marked
    #hmg - is hunters marking
    #ck - is cloud killing
    #sr - sickening radiance
    #pm -polymorph
    #cl - call lightning

#Subtypes that do not change an attribute
    #ca - conjured Animals
    #aop - is in aura of protection
    #gb - guiding Bolt
    #prc - primal compantion
    #gw - great weapon master dock
    #gwa - great weapon attack token 
    #fav - favored foeing
    #fm - fav foe marked
    #wf - Wall of Fire

#All Token of a Entity are handled by its TM Token Manager
#It has a list with all Token
#If a Token uses .resolve() it is resolved with all its connections and removed from the list
#If a Token is generated with a Creatures TM it is automatically added to that creatures List
#The update function is called whenever a Token is removed or added

class TokenManager():
    #This Class handles all the Tokens a player might have
    #The Tokens realate Player with each other and and checks for state changes
    #If a Token is added, the Token Manager updates possible changes

    def __init__(self, player):
        self.player = player

        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)
        self.TokenList = []

        #This dict contains all the subtypes and
        #what attribute of the player they set to True
        #if such a Token is in the TM
        self.subtype_dict = {'r' : ['restrained'],
                            'bl' : ['is_blinded'],
                            'st' : ['is_stunned', 'is_incapacitated'],
                            'pl' : ['is_paralyzed', 'is_incapacitated'],
                            'ps' : ['is_poisoned'],
                            'iv' : ['is_invisible'],
                            'h' : ['is_hasted'],
                            'hex' : ['is_hexed'],
                            'hexn' : ['is_hexing'],
                            'hm' : ['is_hunters_marked'],
                            'hmg' : ['is_hunters_marking'],
                            'ck' : ['is_cloud_killing'],
                            'sr' : ['is_using_sickening_radiance']
                            }
    
    def add(self, Token):
        self.TokenList.append(Token)
        self.update()
    
    def resolve(self, Token):
        if Token in self.TokenList:
            self.TokenList.remove(Token)
        self.update()
    
    def resolveAll(self):
        while len(self.TokenList) > 0:
            self.TokenList[0].resolve()

    def listAll(self):
        for x in self.TokenList:
            x.identify()
    
    def update(self):
        player = self.player
        #This is important for effects that could come from multiple sources
        #That is why this can not be handled via the tokens, because they would not know, if the effect come from more then one token
        #Concentration on the other hand is handled via the con token class

        #Got a new Token, Update Player Stats, like Concentration
        #First all attributes are set to false
        #Then all tokens are looped and if they have a key the corresponding attribute is set to true
        #Conditions
        player.restrained = False
        player.is_stunned = False
        player.is_incapacitated = False
        player.is_paralyzed = False
        player.is_blinded = False
        player.is_poisoned = False
        player.is_invisible = False

        player.is_hasted = False #preset to false
        player.is_hexed = False
        player.is_hexing = False
        player.is_hunters_marked = False
        player.is_hunters_marking = False
        player.is_cloud_killing = False
        player.is_using_sickening_radiance = False


        for x in self.TokenList: #Loop the List of all Tokens
            for key in list(self.subtype_dict.keys()): #Loop the List of Subtype keys for each token
                if x.subtype == key: #If the subtype of that token is the key
                    for player_att in self.subtype_dict[key]: #Set all the corresponding Attributes to true
                        setattr(player, player_att, True)
        
    def checkFor(self, subtype):
        #This Function tests for a Subtype String tag
        #Returns Boolean
        for x in self.TokenList:
            if x.subtype == subtype: return True
        return False

#-----------Resolve and Trigger Conditions
    def break_concentration(self):
        for x in self.TokenList:
            if x.type == 'con': #break concentration
                x.resolve()
                return

    def unconscious(self):
        for x in self.TokenList:
            if x.resolveWhenUnconcious: x.resolve()
            if x.triggersWhenUnconscious: x.getUnconsciousTrigger()

    def endOfTurn(self):
        #This Function is called at the end of entities Turn and resolves timers
        for x in self.TokenList:
            #Timer
            if x.hasATimer:
                x.timer -= 1  #another Round is over
                if x.timer < 1: #Timer is over
                    x.resolve() #Timer based Token is resolved
            #End of Turn
            if x.resolveAtTurnEnd: x.resolve()
            if x.triggersWhenEndOfTurn: x.endOfTurnTrigger()

    def startOfTurn(self):
        #Attention, is called in entity class and this is calles in do_the_fighting
        #ONLY called if player.state == 1
        for x in self.TokenList:
            if x.resolveAtTurnStart: x.resolve()
            if x.triggersWhenStartOfTurn: x.startOfTurnTrigger()

    def hasHitWithAttack(self, target, Dmg, is_ranged, is_spell):
        #This function triggers all Tokens with the Trigger
        #Is called from the attack function if player hit with an attack
        for x in self.TokenList:
            if x.triggersWhenAttackHasHits: x.hasHitWithAttackTrigger(target, Dmg, is_ranged, is_spell)

    def washitWithAttack(self, attacker, Dmg, is_ranged, is_spell):
        #This function triggers all Tokens with the Trigger
        #Is called from the attack function of player was hit with an attack
        for x in self.TokenList:
            if x.triggersWhenHitWithAttack: x.wasHitWithAttackTrigger(attacker, Dmg, is_ranged, is_spell)

    def death(self):
        for x in self.TokenList:
            if x.resolveWhenUnconcious or x.resolveWhenDead:
                x.resolve()
            if x.triggersWhenUnconscious: x.getUnconsciousTrigger()

    def isAttacked(self, attacker, is_ranged, is_spell):
        for x in self.TokenList:
            if x.triggersWhenAttacked: x.wasAttackedTrigger(attacker, is_ranged, is_spell)

    def hasDroppedShape(self):
        #called in drop_shape Entity function
        for x in self.TokenList:
            if x.triggersWhenShapeIsDropped: x.dropShapeTrigger()

class Token():
    def __init__(self, TM):
        self.TM = TM
        #Only Initiate these Vars if they are not already given by a subclass:
        if hasattr(self, 'type') == False:
            self.type = ''
        if hasattr(self, 'subtype') == False:
            self.subtype = ''
        self.resolveWhenUnconcious = False
        self.resolveWhenDead = False
        self.resolveAtTurnStart = False
        self.resolveAtTurnEnd = False
        self.hasATimer = False
        self.timer = 0

        self.triggersWhenAttackHasHits = False
        self.triggersWhenHitWithAttack = False
        self.triggersWhenUnconscious = False
        self.triggersWhenEndOfTurn = False
        self.triggersWhenStartOfTurn = False
        self.triggersWhenAttacked = False
        self.triggersWhenShapeIsDropped = False

        self.TM.add(self) #add and update the Token to TM
    
    def resolve(self):
        #Is the Way to resolve a Token
        #Is then removed from TM list
        #Should be run last
        self.TM.resolve(self)

    def wasAttackedTrigger(self, attacker, is_ranged, is_spell):
        #This is a function of a Token
        #It is called if the Character at start of beeing attacked, before hit or miss check
        #It is a function, that not automatically resolves the token
        return

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        #This is a function of a Token
        #It is called if the Character was hit with an attack
        #It is a function, that not automatically resolves the token
        return

    def hasHitWithAttackTrigger(self, target, Dmg, is_ranged, is_spell):
        #This is a function of a Token
        #It is called if the Character has hit with an attack
        #It is a function, that not automatically resolves the token
        return 

    def getUnconsciousTrigger(self):
        #this function is called if the target gets unconscious and has teh trigger
        return

    def endOfTurnTrigger(self):
        return

    def startOfTurnTrigger(self):
        return

    def dropShapeTrigger(self):
        return

    def identify(self):
        print(str(self))

class LinkToken(Token):
    #This is a token to give as a Token for a effect of any kind that is linked to another Token
    #Link Tokens have an origin
    #If the resolve, they unlink from origin
    def __init__(self, TM, subtype):
        self.subtype = subtype
        self.type = 'l' #Concentration Link
        super().__init__(TM)
        self.origin = False  #Will be linked by the Origin Token

    def resolve(self):
        self.origin.unlink(self) #unlink from Origin
        return super().resolve()

class DockToken(Token):
    #this Kind of Token can accept Link Tokens
    #It will resolve
    #It Accepts a List of Links
    def __init__(self, TM, links):
        super().__init__(TM)

        if type(links) != list: self.links = [links]
        else: self.links = links

        #Now link this Spell as origin to thier links
        for x in self.links:
            x.origin = self
        #Any Lined Tokens will be resolved if Dock token is resolved

    def addLink(self, Token):
        #Add a Link and set this Dock as origin
        self.links.append(Token)
        Token.origin = self

    def resolve(self):
        #If you resolve Dock Token, resolve all links to this Token
        while len(self.links) > 0:
            self.links[0].resolve()#resolve all
        super().resolve()

    def unlink(self, CLToken):
        #This function takes a Link Token out of the link list
        self.links.remove(CLToken)
        CLToken.origin = False #No origin anymore
        #Check if this was last link
        if len(self.links) == 0:
            self.resolve() #resolve if no links left

class ConcentrationToken(DockToken):
    #This is a token to give to a player when concentrating
    def __init__(self, TM, links):
        #is a Dock Token, all linked Tokens are resolved, if this Token is resolved
        self.type = 'con'

        #Check for concentration before initiating
        if TM.player.is_concentrating:
            print(TM.player.name + ' tried to initiate concentration while concentrated')
            quit()
        TM.player.is_concentrating = True #set concentration

        super().__init__(TM, links)

    def resolve(self):
        super().resolve()
        #After the super().resolve from the dock token all link token are resolved aswell
        if self.TM.player.is_concentrating:
            #The if statement is here, because, the resolve function might be called twice
            #If the dock token is resolved, it resolves all links, which in turn resolve the dock token
            self.TM.player.is_concentrating = False #No longer concentrated
            self.TM.player.DM.say(self.TM.player.name + ' no longer concentrated')

#-------------Spell Tokens----------
class EntangledToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' breaks Entangle, ', True)
        return super().resolve()

class HastedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.hasATimer = True
        self.resolveWhenDead = True
        self.resolveWhenUnconcious = True
        self.timer = 10 #10 Rounds
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' Haste wares of, ', True)
        LostHaseToken(self.TM)
        #This Token will resolve at start of players Turn
        #Will take away action and bonus action
        return super().resolve()

class LostHaseToken(Token):
    #Give this Token to a player that just lost haste
    def __init__(self, TM):
        super().__init__(TM)
        self.resolveAtTurnStart = True
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' is tiered from Haste', True)
        self.TM.player.action = 0
        self.TM.player.attack_counter = 0
        self.TM.player.bonus_action = 0
        return super().resolve()

class HexedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
        self.triggersWhenHitWithAttack = True #add hex dmg

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        if attacker.TM == self.origin.TM: #Attacker is hexing you
            Dmg.add(3.5, 'necrotic')
            self.TM.player.DM.say(self.TM.player.name + ' was cursed with a hex: ', True)
            return

    def resolve(self):
        self.TM.player.DM.say(', hex of ' + self.TM.player.name + ' is unbound ')
        if self.origin.TM.player.CurrentHexToken != False:
            #Only set new hex, is orgin still concentrated on hex
            self.origin.TM.player.can_choose_new_hex = True
        super().resolve()

class HexingToken(ConcentrationToken):
    def __init__(self, TM, links):
        self.subtype = 'hexn' #Is hexing token
        super().__init__(TM, links)
    
    def unlink(self, CLToken):
        #This function takes a Concentration Link Token out of the link list
        self.links.remove(CLToken)
        #Usually a Concentration Token is resolved if all links are unlinked
        #But Hex can switch Tokens multiple times
        #The Spell Function creates a new link, the old link is unlinked but the Hex Token not resolved

    def resolve(self):
        #If concentration breaks, before plyer choose a new hex, then can_choose_new_hex might still be True
        self.TM.player.can_choose_new_hex = False
        self.TM.player.CurrentHexToken = False
        self.TM.player.is_hexing = False
        return super().resolve()

class HuntersMarkedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
        self.triggersWhenHitWithAttack = True #add HM dmg

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        if attacker.TM == self.origin.TM and is_spell == False: #Attacker is hexing you
            Dmg.add(3.5, self.origin.TM.player.damage_type)
            self.TM.player.DM.say(self.TM.player.name + ' was hunters marked: ', True)
            return

    def resolve(self):
        self.TM.player.DM.say(', hunters mark of ' + self.TM.player.name + ' is unbound ')
        if self.origin.TM.player.CurrentHuntersMarkToken != False:
            #Only set new hunters Mark, if orgin still concentrated on HM
            self.origin.TM.player.can_choose_new_hunters_mark = True
        super().resolve()

class HuntersMarkingToken(ConcentrationToken):
    def __init__(self, TM, links):
        self.subtype = 'hmg' #Is hunters marking token
        super().__init__(TM, links)
    
    def unlink(self, CLToken):
        #This function takes a Concentration Link Token out of the link list
        self.links.remove(CLToken)
        #Usually a Concentration Token is resolved if all links are unlinked
        #But hunters mark can switch Tokens multiple times
        #The Spell Function creates a new link, the old link is unlinked but the hunters mark Token not resolved

    def resolve(self):
        #If concentration breaks, before plyer choose a new hunters mark, then can_choose_new_hunters_mark might still be True
        self.TM.player.can_choose_new_hunters_mark = False
        self.TM.player.CurrentHuntersMarkToken = False
        return super().resolve()

class GuidingBoltedToken(LinkToken):
    #Is a Link Token, will unlink if resolved, then the GuidingBolt Token will also resolved
    def __init__(self, TM):
        subtype = 'gb'
        super().__init__(TM, subtype)
        self.triggersWhenAttacked = True  #Guiding Bolt gives Advantage if attacked

    def wasAttackedTrigger(self, attacker, is_ranged, is_spell):
        self.TM.player.is_guiding_bolted = True
        #This is reset in the make_attack_roll function
        return super().resolve()

class GuidingBoltToken(DockToken):
    #Is a Dock Token with a Timer, if resolved will also resolve the Linked Token
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.hasATimer = True
        self.timer = 2        #Till End of next Turn

class SummonerToken(ConcentrationToken):
    def __init__(self, TM, links):
        TM.player.has_summons = True #is now summoning
        super().__init__(TM, links)
    
    def resolve(self):
        self.TM.player.has_summons = False
        return super().resolve()
    
class SummenedToken(LinkToken):
    #This Sumclass is a token to give a summoned Creature
    #It will Vanish after it dies
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenDead = True
        self.resolveWhenUnconcious = True
        self.TM.player.is_summoned = True #Will be removed from fight if dead
    
    def resolve(self):
        summon = self.TM.player
        if summon.is_summoned == False:
            print('This is not a summon')
            quit()
        if summon.summoner == False:
            print('Should have a summoner')
            quit()
        
        summon.DM.say(summon.name + ' vanishes ', True)
        summon.CHP = 0
        summon.state = -1
        return super().resolve()

class WallOfFireProtectedToken(LinkToken):
    def __init__(self, TM, subtype, damage):
        super().__init__(TM, subtype)
        self.damage = damage
        self.triggersWhenAttacked = True #protect one player from attacks
        self.last_target = None #Will not trigger on same player in a row
        self.hit_counter = 3 #will only trigger 3 times

    def wasAttackedTrigger(self, attacker, is_ranged, is_spell):
        #The protected player was attacked
        #Only trigger a limited number of times
        if self.hit_counter < 1: return
        #check if it was the same attacker as last time
        if attacker == self.last_target: return
        #dmg the attacker
        self.TM.player.DM.say(attacker.name + ' must go trough the wall of fire ', True)
        dmg_to_apply = dmg(self.damage, 'fire')
        original_caster = self.origin.TM.player #caster of wall of fire
        attacker.last_attacker = original_caster
        #apply dmg to the attacker
        attacker.changeCHP(dmg_to_apply, original_caster, True)

        #Now handle the walls own logic:
        #Remember the last hit target, that went in the wall
        self.last_target = attacker
        #lower the hit counter by one
        self.hit_counter -= 1
        if self.hit_counter < 1:
            #Wall got useless
            self.TM.player.DM.say(self.TM.player.name + 's wall of fire got strategically useless and was dropped, ', True)
            self.resolve()
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + 's wall of fire vanishes ')
        return super().resolve()

class CloudkillToken(ConcentrationToken):
    #Is Concentration Token, lets the caster recast spell
    def __init__(self, TM, links, castLevel):
        self.subtype = 'ck' #cloud kill (sets the self.is_cloud_killing = True)
        super().__init__(TM, links)
        self.castLevel = castLevel

    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + 's cloudkill vanishes ')
        super().resolve()

class SickeningRadianceToken(ConcentrationToken):
    #Is Concentration Token, lets the caster recast spell
    def __init__(self, TM, links, castLevel):
        self.subtype = 'sr' #sickening radiance (sets the self.is_using_sickening_radiance = True)
        super().__init__(TM, links)
        self.castLevel = castLevel
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + 's sickening radiance vanishes ')
        super().resolve()

class PolymorphedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.triggersWhenShapeIsDropped = True #To resolve when shape drops
        #It does not handle the reshaping if drop to 0, because this is handled for all alternate shapes in ChangeCHP function of entity

    def dropShapeTrigger(self):
        super().dropShapeTrigger()
        #Shape was dropped, now resolve Token
        self.resolve()

    def resolve(self):
        if self.TM.player.is_shape_changed: #only drop shape if still shape changed
            self.TM.player.drop_shape() #this drops the polymorph shape
            self.TM.player.DM.say(self.TM.player.name + ' no longer polymorphed ', True)
        if self.origin != False:
            super().resolve()

class CallLightningToken(ConcentrationToken):
    #Is Concentration Token, lets the caster recast spell
    def __init__(self, TM, links, castLevel):
        self.subtype = 'cl' #cloud kill (sets the self.is_cloud_killing = True)
        super().__init__(TM, links)
        self.castLevel = castLevel
        playerAI = self.TM.player.AI
        #Add the call lightning choice to player AI
        playerAI.add_choice(playerAI.callLightningChoice)

    def resolve(self):
        playerAI = self.TM.player.AI
        #When this token resolves it removes the call lightning choice from Choices again
        playerAI.remove_choice(playerAI.callLightningChoice)
        self.TM.player.DM.say(self.TM.player.name + 's called lightning vanishes ')
        super().resolve()

#--------------Other Ability Tokens-----------------
class EmittingProtectionAuraToken(DockToken):
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.resolveWhenUnconcious = True
        self.resolveAtTurnStart = True
        #every Round other protected

class ProtectionAuraToken(LinkToken):
    def __init__(self, TM, auraBonus):
        subtype = 'aop'  #aura of protection
        super().__init__(TM, subtype)
        self.auraBonus = auraBonus #Wisdom Mod of origin player
        if self.auraBonus < 1: self.auraBonus = 1

class PrimalBeastMasterToken(DockToken):
    def __init__(self, TM, links):
        #This is a Dock Token, it will resolve all links if resolved
        #It resolves if the link is resolved
        super().__init__(TM, links)
        self.resolveWhenDead = True
    
    def resolve(self):
        return super().resolve()

class PrimalCompanionToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenDead = True
        self.TM.player.is_summoned = True
    
    def resolve(self):
        summon = self.TM.player
        summon.DM.say(summon.name + ' vanishes ', True)
        summon.CHP = 0
        summon.state = -1

        return super().resolve()

class DodgeToken(Token):
    def __init__(self, TM):
        super().__init__(TM)
        self.resolveAtTurnStart = True
        self.resolveWhenDead = True
        self.resolveWhenUnconcious = True
        self.TM.player.is_dodged = True
    
    def resolve(self):
        self.TM.player.is_dodged = False
        return super().resolve()

class GreatWeaponToken(DockToken):
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.subtype = 'gw'
        self.resolveAtTurnEnd = True #after this turn, all tokens that were given for attacks are resolved
        self.resolveWhenUnconcious = True #maybe unconcious before end of turn

class GreatWeaponAttackToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.subtype = 'gwa'
        self.triggersWhenUnconscious = True #if you are hit by an attack from a great weapon master, and go unconscious, this tokens triggers
        #it also resolves at the end of the origins turn

    def getUnconsciousTrigger(self):
        #This function is called if a player is reduced to 0 HP or lower and has a great weapon attack token
        #This means it was attacked by a great weapon master in this turn
        if self.origin.TM.player.bonus_action == 1:
            self.origin.TM.player.attack_counter += 1 #player gets another attack
            self.origin.TM.player.bonus_action = 0
            self.TM.player.DM.say(', ' + self.origin.TM.player.name + ' gains extra attack')

class FavFoeMarkToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
        self.triggersWhenHitWithAttack = True #add hex dmg
        self.triggersWhenEndOfTurn = True #regain one use at end of turn
        self.has_triggered_this_round = False

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        if self.has_triggered_this_round == False: #no double hit
            if attacker.TM == self.origin.TM: #Attacker is hexing you
                Dmg.add(self.origin.TM.player.favored_foe_dmg, self.origin.TM.player.damage_type)
                self.has_triggered_this_round = True
                self.TM.player.DM.say(self.TM.player.name + ' was marked as favored foe: ', True)
                return

    def endOfTurnTrigger(self):
        self.has_triggered_this_round = False

    def resolve(self):
        self.TM.player.DM.say(', favored foe mark of ' + self.TM.player.name + ' is unbound ')
        super().resolve()

class FavFoeToken(ConcentrationToken):
    def __init__(self, TM, links):
        self.subtype = 'fav' #Is hexing token
        super().__init__(TM, links)
        self.TM.player.has_favored_foe = True
    
    def resolve(self):
        self.TM.player.is_hexing = False
        self.TM.player.has_favored_foe = False
        return super().resolve()

class StunningStrikedToken(LinkToken): #give this to target, Dock token will be done automatically
    def __init__(self, TM):
        super().__init__(TM, "st")
        self.resolveWhenUnconcious = True

    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' is no longer Stunned, ', True)
        return super().resolve()

class StunningStrikeActive(DockToken):
    # Is a Dock Token with a Timer, if resolved will also resolve the Linked Token
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.hasATimer = True
        self.timer = 2  # Till End of next Turn
