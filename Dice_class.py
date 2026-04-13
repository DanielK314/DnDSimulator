import random
class dice:
    def roll_dice(self, amount, size):
        rolltotal = 0
        for i in range(amount):
            rolltotal =+ random.randint(1, size)
        return rolltotal

    def roll_dice_at_advantage(self, amount, size, rerolls):
        if not rerolls:
           rerolls = 2
        rolls = []
        for _ in range(rerolls):
            rolltotal = 0
            for i in range(amount):
                rolltotal =+ random.randint(1, size)
            rolls.append(rolltotal)
        return max(rolls)

    def roll_dice_at_disadvantage(self, amount, size, rerolls):
        if not rerolls:
            rerolls = 2
        rolls = []
        for _ in range(rerolls):
            rolltotal = 0
            for i in range(amount):
                rolltotal = + random.randint(1, size)
            rolls.append(rolltotal)
        return min(rolls)