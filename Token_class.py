if __name__ == '__main__':
    from Entity_class import entity

#Types:
#con - concentration
#l - Link

#subtypes
#h - haste
#r - restrained
#hex - is hexed
#hexn - is hexing
#ca - conjured Animals
#aop - is in aura of protection
#gb - guiding Bolt

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
        #Got a new Token, Update Player Stats, like Concentration
        is_concentrating = False
        self.player.is_hasted = False #preset to false
        self.player.is_hexed = False
        self.player.is_hexing = False
        for x in self.TokenList:
            #---------------Concentration------------
            if x.type == 'con': #check for Concentration Tokens
                if is_concentrating: #was already concentrated
                    print(self.player.name + ' is double concentrated')
                    quit()
                else:
                    is_concentrating = True #Is concentrating
            #--------------restrained----------------
            if x.subtype == 'r':
                self.player.restrained = True #set player restrained
            #--------------haste------------
            if x.subtype == 'h':
                self.player.is_hasted = True #set player haste
            #--------------hex
            if x.subtype == 'hex':
                self.player.is_hexed = True #set player hexed

            if x.subtype == 'hexn':
                self.player.is_hexing = True
        

        #----------Update Player Stats
        if self.player.is_concentrating: #was concentrating before
            if is_concentrating == False: #but not anymore
                self.player.DM.say(self.player.name + ' no longer concentrated')

        self.player.is_concentrating = is_concentrating #set player concentration

    def checkFor(self, subtype):
        #This Function tests for a Subtype String tag
        #Returns Boolean
        for x in self.TokenList:
            if x.subtype == subtype: return True
        return False

#-----------Trigger Conditions
    def break_concentration(self):
        for x in self.TokenList:
            if x.type == 'con': #break concentration
                x.resolve()
#                self.player.DM.say(self.player.name + ' lost concentration, ', end='')
                #I think I dont need this, as in all cases the links are resolved first
                self.player.is_concentrating = False
                return

    def unconscious(self):
        for x in self.TokenList:
            if x.resolveWhenUnconcious: x.resolve()

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

    def startOfTurn(self):
        #Attention, is called in entity class and this is calles in do_the_fighting
        #ONLY called if player.state == 1
        for x in self.TokenList:
            if x.resolveAtTurnStart: x.resolve()

    def death(self):
        for x in self.TokenList:
            if x.resolveWhenUnconcious or x.resolveWhenDead:
                x.resolve()

    def isAttacked(self):
        for x in self.TokenList:
            if x.resolveIfAttacked:
                x.resolve()        

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
        self.resolveIfAttacked = False
        self.hasATimer = False
        self.timer = 0
        self.TM.add(self) #add and update the Token to TM
    
    def resolve(self):
        #Is the Way to resolve a Token
        #Is then removed from TM list
        #Should be run last
        self.TM.resolve(self)
    
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
        #If you resolve Dock Tag, resolve all links to this concentration
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
        self.type = 'con'
        super().__init__(TM, links)
        #is a Dock Token, all linked Tokens are resolved, if this Token is resolved            

class EntangledToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' breaks Entangle, ', end='')
        return super().resolve()

class HastedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.hasATimer = True
        self.timer = 10 #10 Rounds 
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' Haste wares of, ', end='')
        LostHaseToken(self.TM)
        #This Token will resolve at start of players Turn
        #Will take away action and bonus action
        return super().resolve()

class LostHaseToken(Token):
    #Give this Token to a player that just lost hase
    def __init__(self, TM):
        super().__init__(TM)
        self.resolveAtTurnStart = True
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' is tiered from Haste')
        self.TM.player.action = 0
        self.TM.player.attack_counter = 0
        self.TM.player.bonus_action = 0
        return super().resolve()

class HexedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
    
    def resolve(self):
        self.TM.player.DM.say('hex of ' + self.TM.player.name + ' is unbound, ', end='')
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
        return super().resolve()

class GuidingBoltedToken(LinkToken):
    #Is a Link Token, will unlink if resolved, then the GuidingBolt Token will also resolved
    def __init__(self, TM):
        subtype = 'gb'
        super().__init__(TM, subtype)
        self.resolveIfAttacked = True  #Guiding Bolt gives Advantage if attacked

    def resolve(self):
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
        
        summon.DM.say(' ' + summon.name + ' vanishes ', end='')
        summon.CHP = 0
        summon.state = -1
        return super().resolve()

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

