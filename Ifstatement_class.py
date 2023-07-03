class ifstatements:
    def __init__(self, rules, errors, DM):
        self.rules = rules
        self.errors = errors
        self.DM = DM
    
    def check(self):
        if all(self.rules):
            return
        else:
            for i in range(0,len(self.rules)):
                if self.rules[i] == False:
                    print(self.errors[i])
                    quit()
