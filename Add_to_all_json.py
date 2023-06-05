import json
import os

#This script can be used to add to all json files in the Entity folder and Archive folder

if __name__ == '__main__':
    Entities_File_List = os.listdir('./Entities') #list all files in Entities
    File_List = []
    for x in Entities_File_List:
        if '.json' in x:
            File_List.append('./Entities/' + x)  #Use only .json files

    Archive_File_List = os.listdir('./Archive') #list all files in Archive
    for x in Archive_File_List:
        if '.json' in x:
            File_List.append('./Archive/' + x)  #Use only .json files
    
    File_List.append('./New Character.json')


    for path in File_List:
        file = open(path)#load new file
        data = json.load(file)
        file.close()
        data['RageDmg'] = "0"  #This to add a line
#        data.pop('test') #this to remove the line
        with open(path, "w") as f:  #write to json file
            json.dump(data, f, indent=4)