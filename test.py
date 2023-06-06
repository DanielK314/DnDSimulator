class test():
    def __init__(self, text):
        self.text = text
    
    def print(self):
        print(self.text)

a = test
b = a('hello World')
b.print()