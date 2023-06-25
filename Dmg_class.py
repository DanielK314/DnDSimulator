class dmg:
    def __init__(self, amount = 0, type = 'slashing'):
        #List with float dmg amounts
        self.dmg_amount_list = []
        #List with dmg_type strings
        self.dmg_type_list = []
        self.types = ['acid', 'cold', 'fire', 'force' , 'lightning',
        'thunder', 'necrotic', 'poison', 'psychic' ,'radiant', 
        'bludgeoning', 'piercing', 'slashing', 'true', 'heal']
        self.DMGSubstract = 0
        #If a first dmg is passed:
        if amount != 0:
            self.add(amount, type)
    
    def add(self, amount, type):
        for x in self.types:
            if x in type:
                #Check if maybe alredy in
                for i in range(0,len(self.dmg_type_list)):
                    if x == self.dmg_type_list[i]:
                        self.dmg_amount_list[i] += amount
                        return
                #else
                self.dmg_amount_list.append(amount)
                self.dmg_type_list.append(x)
                return
        print('Unknown Dmg Type: ' + type)
        quit()

    def multiply(self, factor):
        #All dmg entries are multiplied
        self.dmg_amount_list = [x*factor for x in self.dmg_amount_list]

    def substract(self, amount):
        #should be positive
        self.DMGSubstract += amount

    def abs_amount(self):
        return sum(self.dmg_amount_list) - self.DMGSubstract
    
    def calculate_for(self, player):
            DMGTotal = 0
            for i in range(0, len(self.dmg_amount_list)):
                DMGType  = self.dmg_type_list[i]
                if DMGType in player.damage_resistances or DMGType in player.additional_resistances:
                    player.DM.say(str(player.name) + ' is resistant against ' + DMGType, True)
                    self.dmg_amount_list[i] = self.dmg_amount_list[i]/2
                    DMGTotal += self.dmg_amount_list[i]
                elif DMGType in player.damage_immunity:
                    player.DM.say(str(player.name) + ' is immune against ' + DMGType, True)
                    self.dmg_amount_list[i] = 0
                    DMGTotal += 0
                elif DMGType in player.damage_vulnerability:
                    player.DM.say(str(player.name) + ' is vulnarable against ' + DMGType, True)
                    self.dmg_amount_list[i] = self.dmg_amount_list[i]*2
                    DMGTotal += self.dmg_amount_list[i]
                else:
                    DMGTotal += self.dmg_amount_list[i]
            if DMGTotal < 0: return DMGTotal  #It is heal, so return, do not substract from heal

            #If dmg was substracted from this amount, do it now, if < 0, do not heal
            if self.DMGSubstract > DMGTotal: return 0
            else:
                DMGTotal -= self.DMGSubstract
                return DMGTotal
        
    def damage_type(self):
        #Return type of first
        return self.dmg_type_list[0]
    
    def text(self):
        string = ''
        for i in range(0,len(self.dmg_amount_list)):
            if self.dmg_amount_list[i] != 0:
                string += str(round(self.dmg_amount_list[i],2))
                string += ' ' + self.dmg_type_list[i] + ' '
        if self.DMGSubstract > 0:
            string += ' - ' + str(round(self.DMGSubstract,2))  #substracted
        return string

    def print(self):
        print(self.dmg_amount_list)
        print(self.dmg_type_list)        
