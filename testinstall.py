import sys
import os

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

with open(application_path + '/test.txt', 'w+') as file:
    print(file.read())
    file.write('test write')
print('run done')