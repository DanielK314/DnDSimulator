from Entity_class import *
from tkinter import *
import ttkbootstrap as ttk
from tkinter import messagebox
from functools import partial
import os
import json
import subprocess
from ttkbootstrap.constants import *
import platform #for figuring out windows/macOS

#Controlls the Pages
class Controller(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        #The Controller has the Entities in it
        self.Heros = []
        self.MonsterManuel = []
        self.Fighters = []
        self.DM = DungeonMaster()
        self.Load_Entities()  #Loads the Entities from the files
        self.Load_Archive_Entities() #Loads from Archive

        #This is used multiple times, so it always calls master Controller
        self.DMG_Types = ['acid', 'cold', 'fire', 'force' , 'lightning', 'thunder', 'necrotic', 'poison', 'psychic' ,'radiant' ,'bludgeoning', 'piercing', 'slashing']

        self.All_Spells = self.Heros[0].SpellNames #see Entity Class

        self.All_Abilities = ['UncannyDodge', 'CunningAction', 'WailsFromTheGrave', 'Rage', 'RecklessAttack', 'Frenzy', 'Smite', 'QuickenedSpell', 'EmpoweredSpell', 'TwinnedSpell', 'WildShape', 'CombatWildShape', 'Inspiration', 'AgonizingBlast', 'DragonsBreath', 'SpiderWeb']

        #Initialize the Pages, attention, Order matters
        self.ArchivePage = Archive(self)
        self.ArchivePage.grid(row=0, column=0, sticky='nsew')
        self.EntityPage = EntityPage_cl(self)
        self.EntityPage.grid(row=0, column=0, sticky='nsew')
        self.HomePage = HomePage_cl(self)
        self.HomePage.grid(row=0, column=0, sticky='nsew')
        self.DMPage = DM_page(self)
        self.DMPage.grid(row=0, column=0, sticky='nsew')
        self.LastPage = self.HomePage
        self.HomePage.tkraise() # show the Homepage first
 
    def Load_Entities(self): #Entities will be loaded as Objects in Controller
        Entities_File_List = os.listdir('./Entities') #list all files in Entities
        Entities_List = []
        for x in Entities_File_List:
            if '.json' in x:
                Entities_List.append(x)  #Use only .json files
        Entities_List.sort() #sort by name
        #Initiate the Entities and if they are Heros or Villains
        Entities = []
        for name in Entities_List:
            try: #try to initialize
                file = open('./Entities/' + name)
                Entities.append(entity(name[0:-5], int(json.load(file)['Hero_or_Villain']), self.DM))
            except Exception as e:
                print('json file ' + name + ' could not be opened')
                print(e)
        self.Heros = []
        self.MonsterManuel = []
        #Sort the Teams
        for x in Entities:
            if x.team == 0:
                self.Heros.append(x)
            elif x.team == 1:
                self.MonsterManuel.append(x)

        #fighters will later be filled with the enteties that take a part in the fight
        self.Fighters = []

    def Load_Archive_Entities(self): #Archive will be loaded as Objects in Controller (once at start up)
        Archive_File_List = os.listdir('./Archive') #list all files in Archive
        Archive_List = []
        for x in Archive_File_List:
            if '.json' in x:
                Archive_List.append(x)  #Use only .json files
        Archive_List.sort() #sort by name

        #Initiate the Entities and if they are Heros or Villains
        #If you use the entity function to load from archive, the archive parameter must be True
        Entities = []
        for name in Archive_List:
            try:
                file = open('./Archive/' + name)
                Entities.append(entity(name[0:-5], int(json.load(file)['Hero_or_Villain']), self.DM, archive=True))
            except Exception as e:
                print(e)

 
        self.Archive_Heros = []
        self.Archive_MonsterManuel = []
        #Sort the Teams
        for x in Entities:
            if x.team == 0:
                self.Archive_Heros.append(x)
            elif x.team == 1:
                self.Archive_MonsterManuel.append(x)

    def change_to_HomePage(self):
        if self.LastPage == self.DMPage:
            self.DMPage.tkraise()
            self.LastPage = self.HomePage
        else:
            self.HomePage.tkraise()
    
    def change_to_HomePage_saved(self):
        self.Load_Entities()
        #destroy everything in the frame 
        for widget in self.HomePage.winfo_children():
           widget.destroy()
        #and rebuild the page
        self.HomePage.Build_Page()
        self.root.update()
        self.HomePage.tkraise()

    def change_to_EntityPage(self):
        self.EntityPage.load_default_stats()
        self.EntityPage.tkraise()

    def change_to_DMPage(self):
        self.DMPage.build_page()
        self.root.update()
        self.DMPage.tkraise()

    def change_to_current_EntityPage(self):
        self.EntityPage.tkraise()

    def change_to_EntityPage_Character(self, Player, current_page):
        self.LastPage = current_page
        self.EntityPage.load_Entity_stats(Player)
        self.EntityPage.tkraise()

    def change_to_Archive(self):
        self.ArchivePage.tkraise()

class HomePage_cl(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.Build_Page() #build up the Page

    def Build_Page(self):
        HeroFrame = ttk.Labelframe(self, text='Add Hero', padding=10)
        MonsterFrame = ttk.Labelframe(self, text='Add Monster', padding=10)
        BottomFrame = Frame(self)
        #create buttons for heros
        self.buttons_heros = [ttk.Button(HeroFrame, text=player.name, width =12, bootstyle='success outline', command=partial(self.master.change_to_EntityPage_Character, player, self)) for player in self.master.Heros]
        self.add_buttons_heros = [ttk.Button(HeroFrame, text='+', width =1, bootstyle="success outline", command=partial(self.init_hero, i)) for i in self.master.Heros]

        #create a button for every monster in the Monster Manual
        self.buttons_monsters_value = [IntVar() for i in self.master.MonsterManuel]
        self.buttons_monsters = [ttk.Button(MonsterFrame, text=monster.name, width=12, bootstyle='danger outline', command=partial(self.master.change_to_EntityPage_Character, monster, self)) for monster in self.master.MonsterManuel]
        self.add_buttons_monsters = [ttk.Button(MonsterFrame, text='+', width =1, bootstyle="outline danger", command=partial(self.init_monster, i)) for i in self.master.MonsterManuel]

        #order Charcater/add Buttons
        for i in range(0,len(self.buttons_heros)):
            self.buttons_heros[i].grid(row=int(i/2), column=(i%2)*2, pady= 3, padx=2)
            self.add_buttons_heros[i].grid(row=int(i/2), column=(i%2)*2 +1, pady= 3, padx=2)
        for i in range(0,len(self.buttons_monsters)):
            self.buttons_monsters[i].grid(row=int(i/2), column=(i%2)*2, pady= 3, padx=2)
            self.add_buttons_monsters[i].grid(row=int(i/2), column=(i%2)*2+1, pady= 3, padx=2)
        HeroFrame.grid(row=0, column = 0, pady=10, sticky='wn')
        MonsterFrame.grid(row=0, column = 1, padx=20, pady=10, sticky='wn')

        #Iteration Label
        IterationFrame = Frame(BottomFrame)
        self.iterationlabel = Label(IterationFrame, text='Repetitions:', width=9)
        self.repetitions_entry = Entry(IterationFrame, bd=5, width=8)
        self.repetitions_entry.insert(0, '100')
        self.b_run_stat = ttk.Button(IterationFrame, width = 9, text='Run Analysis', bootstyle="outline", command=self.run_statistical_recap)
        #Create Buttons
        ButtonFrame = Frame(BottomFrame)
        self.b_create_new = ttk.Button(ButtonFrame, text='Create New', width=12, bootstyle="outline", command= self.master.change_to_EntityPage)
        self.b_print_value = IntVar()
        self.b_print = 0
        self.b_print = ttk.Checkbutton(ButtonFrame, width = 12, text='Enable Printing', bootstyle="outline-toolbutton", variable = self.b_print_value, onvalue=1, offvalue=0)
        self.b_DM = ttk.Button(ButtonFrame, text='DM Mode', width=12, bootstyle="outline", command= self.master.change_to_DMPage)

        self.iterationlabel.grid(row=0,column=0, pady=3, sticky='w')
        self.repetitions_entry.grid(row=0, column=1, pady=3, padx=5)
        self.b_run_stat.grid(row=0, column=2, pady=5)
        IterationFrame.grid(row=0, column=0, sticky='w')

        self.b_create_new.grid(row=2, column=0, padx=3)
        self.b_print.grid(row=2, column=1, padx=3)
        self.b_DM.grid(row=2, column=2, padx=3)
        ButtonFrame.grid(row=1, column=0)

        BottomFrame.grid(row=1, column=0, columnspan=2, pady=15, sticky='wn')
        
    def run_statistical_recap(self):
        #in the following all information about the simulation and the Entities that take part are written in the json file

        repetitions = int(self.repetitions_entry.get()) #read repetitions from input
        if self.b_print_value.get() == 0:
            simulation_parameters = {"printing_on": 0, "repetitions" : repetitions}
        else:
            simulation_parameters = {"printing_on": 1, "repetitions" : repetitions}

        Entities = [{"name" : player.name, "team" : player.team} for player in self.master.Fighters]
        with open("simulation_parameters.json", "w") as f:  #write to json file
            json.dump({"simulation_parameters": simulation_parameters, "Entities": Entities}, f, indent=4)

        infotext = str(repetitions) + ' repetitions were dones with: \n'
        for i in self.master.Fighters:
            infotext = infotext + i.name + '\n'

        #exec(open('run_full_stat_recap.py').read())  #run the external python script, which will load from json file
        #using subprocess functions to call script
        p = subprocess.run('python3 run_full_stat_recap.py', shell= True)

        text_result = open('simulation_result.txt').read()
        open('simulation_result.txt', 'w').write('')

        messagebox.showinfo('Simulation Info', infotext + '\n' + text_result)

    def init_hero(self, Player):
        if Player in self.master.Fighters:
            self.master.Fighters.remove(Player)
            self.buttons_heros[self.master.Heros.index(Player)].configure(bootstyle='success outline')
        else:
            self.master.Fighters.append(Player)
            self.buttons_heros[self.master.Heros.index(Player)].configure(bootstyle='success solid')

    def init_monster(self, Player):
        if Player in self.master.Fighters:
            self.master.Fighters.remove(Player)
            self.buttons_monsters[self.master.MonsterManuel.index(Player)].configure(bootstyle='danger outline')
        else:
            self.master.Fighters.append(Player)
            self.buttons_monsters[self.master.MonsterManuel.index(Player)].configure(bootstyle='danger solid')

class EntityPage_cl(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.name = 'New Character'

        #The System of this page is, that the current stats are saved in the stats dictionary and with the fetch functions new stats can be loaded, the page must then be updated

        #If you want to change something, you have to change 3 functions
        #build_page
        #update_page 
        #fetch_GUI_stats

        #fetch the basic stats in the dict 
        self.fetch_default_stats()

        #Initialize the Spellbook
        self.SpellBook = Frame(self)
        self.SpellBook.grid(row=0, column=0, sticky='nsew')
        self.build_spell_book()

        #Initialize the Other Abilies Page
        self.AbilityPage = Frame(self)
        self.AbilityPage.grid(row=0, column=0, sticky='nsew')
        self.build_ability_page()

        #Build the page, which is empty for now
        self.MainPage = Frame(self)
        self.MainPage.grid(row=0, column=0, sticky='nsew')
        self.build_page()

        #Main Page on top
        self.MainPage.tkraise()

    def build_page(self):
        #The Character Page is build with different Frames
        #Button Page
        self.ButtonPage = Frame(self.MainPage, width= 300, height=20)
        #Back Button
        self.bBack = ttk.Button(self.ButtonPage, text='Back', bootstyle="outline", command= self.master.change_to_HomePage)
        self.bBack.grid(row=0, column=0, padx = 3)
        #Load from Archive
        self.b_archive = ttk.Button(self.ButtonPage, text='Load from Archive', bootstyle="outline", command= self.master.change_to_Archive)
        self.b_archive.grid(row= 0, column=1, padx = 3)
        #Save Button
        self.b_save = ttk.Button(self.ButtonPage, text='Save Character', bootstyle="outline", command= self.save_Entity)
        self.b_save.grid(row= 0, column=2, padx = 3)
        #Delete Button
        self.b_delete = ttk.Button(self.ButtonPage, text='Delete Character', bootstyle="outline", command= self.delete_Entity)
        self.b_delete.grid(row= 0, column=3, padx = 3)
        self.ButtonPage.grid(row=0, column=0, sticky='w', pady=5, columnspan=3)

        #Style
        self.Entrybd = 2
        self.Entrywidth= 4
        self.AbilityScoreWidth = 2
        Framepadding = 6

        #Character Name
        self.NameLabel = Label(self.MainPage, text='Character Name', font='bold')
        self.NameLabel.grid(row=1, column=0, pady=5)
        self.NameEntry = Entry(self.MainPage, bd=2, width=12)
        self.NameEntry.grid(row=1, column=1, pady=5)

        #Left and Right Frame
        self.LeftFrame = Frame(self.MainPage, width=100)
        self.BasicFrame = ttk.Labelframe(self.LeftFrame, text='Basic Stats', padding=Framepadding)
        self.BasicFrame.grid(row=0, column=0, sticky='w')
        self.RightFrame = Frame(self.MainPage, width=200, padx=3)


        #############Left Frame
        #Basic Stats
        self.BasicStatsFrame = Frame(self.BasicFrame,width=100)
        #If you change this, u need to change also the update_Entity_stats function
        self.BasicStatNames = ['Armor Class (AC)', 'Health Points (HP)', 'Proficiency', 'Attack Modifier', 'Number of Attacks', 'Damage', 'Level', 'Hero(0) or Villain(1)']
        self.BasicStatLabels = [Label(self.BasicStatsFrame, text=labeltext, pady=3) for labeltext in self.BasicStatNames]
        self.BasicStatValues = [StringVar() for x in self.BasicStatNames]
        self.BasicStatEntries = [Entry(self.BasicStatsFrame, bd=self.Entrybd, width=self.Entrywidth, textvariable= self.BasicStatValues[i]) for i in range(0, len(self.BasicStatNames))]
        for i in range(0,len(self.BasicStatLabels)):
            self.BasicStatLabels[i].grid(row=i+1, column=0, sticky="w")
            self.BasicStatEntries[i].grid(row=i+1, column=1)
        self.BasicStatsFrame.grid(row=0, column=0, sticky='w')


        #Ability Scores
        self.AbilityScoreFrame = Frame(self.BasicFrame,width=100)
        self.AbilityScoreNames = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        Label(self.AbilityScoreFrame, text='Ability').grid(row=0, column=0)
        Label(self.AbilityScoreFrame, text='Score').grid(row=0, column=1)
        Label(self.AbilityScoreFrame, text='Mod').grid(row=0, column=2)
        Label(self.AbilityScoreFrame, text='Save Prof.').grid(row=0, column=3)
        self.AbilityScoreLabels = [Label(self.AbilityScoreFrame, text=labeltext, pady=3) for labeltext in self.AbilityScoreNames]
        self.AbilityScoreValues = [IntVar() for i in range(0,6)]
        self.AbilityScoreEntries = [Entry(self.AbilityScoreFrame, textvariable= self.AbilityScoreValues[i], bd=self.Entrybd, width=self.AbilityScoreWidth) for i in range(0,6)]
        self.AbilityScoreMod = [Label(self.AbilityScoreFrame, text='-') for labeltext in self.AbilityScoreNames]
        self.AbilityScoreProfList = [IntVar() for i in range(0,6)]
        self.AbilityScoreProfButton = [ttk.Checkbutton(self.AbilityScoreFrame, text='',variable=self.AbilityScoreProfList[i], onvalue=1, offvalue=0) for i in range(0, 6)]
        for i in range(0,6):
            self.AbilityScoreProfButton[i].grid(row=1 + i, column=3)
        for i in range(0,len(self.AbilityScoreLabels)):
            self.AbilityScoreLabels[i].grid(row=i+1, column=0, sticky="w")
            self.AbilityScoreEntries[i].grid(row=i+1, column=1)
            self.AbilityScoreMod[i].grid(row=i+1, column=2)
        for i in range(0,6): #this calles the update function is a ability score is changed
            self.AbilityScoreValues[i].trace('w', partial(self.update_ability_mod, i))
            self.AbilityScoreProfList[i].trace('w', partial(self.update_ability_mod, i))
        self.BasicStatValues[self.BasicStatNames.index('Proficiency')].trace('w', self.update_all_ability_mod)
        self.AbilityScoreFrame.grid(row=1, column=0, pady=5, sticky='w')


        #Spellcasting
        self.SpellFrame = ttk.Labelframe(self.LeftFrame, text= 'Spellcasting', padding =Framepadding, width=100)
        self.SpellTopFrame = Frame(self.SpellFrame, width=100)

        Label(self.SpellTopFrame, text='Spell Mod').grid(row=0, column=0, sticky="w")
        self.SpellModEntry = Entry(self.SpellTopFrame, bd=self.Entrybd, width=self.AbilityScoreWidth)
        self.SpellModEntry.grid(row=0, column=1)
        Label(self.SpellTopFrame, text='Spell DC').grid(row=0, column=2, sticky="w")
        self.SpellDCEntry = Entry(self.SpellTopFrame, bd=self.Entrybd, width=self.AbilityScoreWidth)
        self.SpellDCEntry.grid(row=0, column=3)
        self.SpellTopFrame.grid(row=0, column=0, columnspan=10, sticky='w')
        #Now Spell Level
        Label(self.SpellFrame, text='Level').grid(row=2, column=0, sticky='w')
        Label(self.SpellFrame, text='Slots').grid(row=3, column=0, sticky='w')
        self.SpellLevelLabel = [Label(self.SpellFrame, text=str(i), padx=3) for i in range(1, 10)]
        self.SpellLevelEntries = [Entry(self.SpellFrame, bd=self.Entrybd, width=1) for i in range(1, 10)]
        for i in range(0,9):
            self.SpellLevelLabel[i].grid(row=2, column=i+1)
            self.SpellLevelEntries[i].grid(row=3, column=i+1, pady=3, padx=1)
        #Spell List Display
        self.SpellDisplayList = StringVar(value=[])
        self.SpellDisplay = Listbox(self.SpellFrame, listvariable=self.SpellDisplayList, height=5)
        self.SpellDisplay.grid(row=4, column=0, columnspan=9, sticky="w")
        #Scrollbar
        self.SpellScrollbar = ttk.Scrollbar(self.SpellFrame, orient='vertical', command=self.SpellDisplay.yview)
        self.SpellDisplay['yscrollcommand'] = self.SpellScrollbar.set
        self.SpellScrollbar.grid(row=4, column=9, sticky='ns')
        #Spell Book
        ttk.Button(self.SpellFrame, text='Spell Book', bootstyle="outline", command= self.open_spell_book).grid(row=5, column=0, columnspan=6, sticky='w', pady=5)
        self.SpellFrame.grid(row=1, column=0, pady=10, sticky='ew')




        ##########Right Frame
        #Position Management
        #Speed
        self.PositionFrame = ttk.Labelframe(self.RightFrame, text='Movement', padding = Framepadding)
        Label(self.PositionFrame, text='Speed in ft').grid(row=0, column=0, sticky='w')
        self.SpeedEntry = Entry(self.PositionFrame, bd=self.Entrybd, width=self.Entrywidth)
        self.SpeedEntry.grid(row=0, column=1)
        #Range
        self.Range_Attack_Value = IntVar()
        ttk.Checkbutton(self.PositionFrame, text='Range Attacks',variable=self.Range_Attack_Value, onvalue=1, offvalue=0).grid(row=1,column=0, sticky='w', pady=5)
        #Position Type
        self.PositionButtonsFrame = Frame(self.PositionFrame)
        self.PositionValue = IntVar()
        ttk.Radiobutton(self.PositionButtonsFrame, text="Front Line", variable=self.PositionValue, value=0).grid(row=0, column=0)
        ttk.Radiobutton(self.PositionButtonsFrame, text="Middle", variable=self.PositionValue, value=1).grid(row=0, column=1, padx=15)
        ttk.Radiobutton(self.PositionButtonsFrame, text="Back Line", variable=self.PositionValue, value=2).grid(row=0, column=2)
        self.PositionButtonsFrame.grid(row=2,column=0, columnspan=3, sticky='w')
        self.PositionFrame.grid(row=0, column=0, sticky='ewn')



        #Damage Type
        self.DMGTypes = []
        self.DMGFrame = ttk.Labelframe(self.RightFrame, text='DMG', padding=Framepadding)
        self.DMGTypeEntry = ttk.Combobox(self.DMGFrame, values = self.master.DMG_Types, state='readonly')#Damage Type Entry
        self.DMGTypeEntry.set(self.stats['Damage_Type'])
        Label(self.DMGFrame, text='Damage Type').grid(row=0, column=0, sticky='w')
        self.DMGTypeEntry.grid(row=0,column=1)
        #Label for Res, Imm, Vul
        self.DMGListFrame = Frame(self.DMGFrame, width=200, height=100)
        Label(self.DMGListFrame, text='Resistances').grid(row=0, column=0, sticky='w')
        Label(self.DMGListFrame, text='Immunities').grid(row=0, column=1, sticky='w')
        Label(self.DMGListFrame, text='Vulnerabilities').grid(row=0, column=2, sticky='w')
        #Lists of Checkbutton
        #Res
        self.DMGResList = [IntVar() for i in self.master.DMG_Types]
        #ddca67
        self.ResCheckButton = [ttk.Checkbutton(self.DMGListFrame, text=self.master.DMG_Types[i],variable=self.DMGResList[i], onvalue=1, offvalue=0, bootstyle='warning') for i in range(0, len(self.master.DMG_Types))]
        for i in range(0,len(self.ResCheckButton)):
            self.ResCheckButton[i].grid(row=1 + i, column=0, padx=5, sticky='w')
        #Imm  
        #7de46e
        self.DMGImmList = [IntVar() for i in self.master.DMG_Types]
        self.ImmCheckButton = [ttk.Checkbutton(self.DMGListFrame, text=self.master.DMG_Types[i],variable=self.DMGImmList[i], onvalue=1, offvalue=0, bootstyle='danger') for i in range(0, len(self.master.DMG_Types))]
        for i in range(0,len(self.ImmCheckButton)):
            self.ImmCheckButton[i].grid(row=1 + i, column=1, padx=5, sticky='w')
        #Vul
        #e36e5e
        self.DMGVulList = [IntVar() for i in self.master.DMG_Types]
        self.VulCheckButton = [ttk.Checkbutton(self.DMGListFrame, text=self.master.DMG_Types[i],variable=self.DMGVulList[i], onvalue=1, offvalue=0, bootstyle='success') for i in range(0, len(self.master.DMG_Types))]
        for i in range(0,len(self.VulCheckButton)):
            self.VulCheckButton[i].grid(row=1 + i, column=2, padx=5, sticky='w')
        #Pack Frames
        self.DMGListFrame.grid(row=1, column=0, columnspan=2, sticky='w')
        self.DMGFrame.grid(row=1, column=0, pady=10, sticky='ew')

        #Other Stuff
        self.OtherFrame = ttk.Labelframe(self.RightFrame, text= 'Other', padding = Framepadding)
        #Other Abilites
        ttk.Button(self.OtherFrame, text='Other Abilites', bootstyle="outline", command= self.open_ability_page).grid(row=1, column=0, sticky = 'w')

        #Other Abilities List Display
        self.AbilityDisplayList = StringVar(value=[])
        self.AbilityDisplay = Listbox(self.OtherFrame, listvariable=self.AbilityDisplayList, height=5)
        self.AbilityDisplay.grid(row=0, column=0, columnspan=2, sticky="w", pady=4)
        #Scrollbar
        self.AbilityScrollbar = ttk.Scrollbar(self.OtherFrame, orient='vertical', command=self.AbilityDisplay.yview)
        self.AbilityDisplay['yscrollcommand'] = self.AbilityScrollbar.set
        self.AbilityScrollbar.grid(row=0, column=4, sticky='ns')
        #SneakAttackDmg
        Label(self.OtherFrame, text='Sneak Attack Dmg').grid(row=2, column=0, sticky="w")
        self.SneakAttackDmgEntry = Entry(self.OtherFrame, bd=self.Entrybd, width =self.AbilityScoreWidth)
        self.SneakAttackDmgEntry.grid(row=2, column=1, sticky="w", pady=3)
        #LayOnHands
        Label(self.OtherFrame, text='Lay on Hands Pool').grid(row=3, column=0, sticky="w")
        self.LayOnHandsEntry = Entry(self.OtherFrame, bd=self.Entrybd, width =self.AbilityScoreWidth)
        self.LayOnHandsEntry.grid(row=3, column=1, sticky="w", pady=3)
        #SorceryPoints
        Label(self.OtherFrame, text='Sorcery Points').grid(row=4, column=0, sticky="w")
        self.SorceryPointsEntry = Entry(self.OtherFrame, bd=self.Entrybd, width =self.AbilityScoreWidth)
        self.SorceryPointsEntry.grid(row=4, column=1, sticky="w")
        self.OtherFrame.grid(row=2, column=0,sticky='ew', pady=3)

        #Align Left and Right Frame
        self.LeftFrame.grid(row=2,column=0, columnspan=2, padx=5, sticky='n')
        self.RightFrame.grid(row=2, column=2, padx=10, sticky='n')

    def build_spell_book(self):
        self.SpellBookTopFrame = Frame(self.SpellBook)
        Label(self.SpellBookTopFrame, text='Spellbook').grid(row=0,column=1, padx=10)
        ttk.Button(self.SpellBookTopFrame, text='Back', bootstyle ='outline', command= self.close_spell_book).grid(row=0, column=0)
        self.SpellBookTopFrame.grid(row=0, column=0, pady=5)

        Spellframes = [ttk.Labelframe(self.SpellBook, text = 'Level ' + str(i)) for i in range(0,10)]

        self.SpellBookListFrame = Frame(self.SpellBook)
        self.SpellList = [IntVar() for i in self.master.All_Spells]
        self.SpellButton = []
        for i in range(0,len(self.SpellList)):
            level = self.master.Heros[0].SpellBook[self.master.All_Spells[i]].spell_level #Find the Level of the Spell
            button = ttk.Checkbutton(Spellframes[level], bootstyle= 'warning', text = self.master.All_Spells[i], variable=self.SpellList[i], onvalue=1, offvalue=0)
            self.SpellButton.append(button)
        #This ensures, that if a spell is clicked, the Spell list Display on the Main page updates, it is not the dict of the Page
        for i in range(0, len(self.SpellList)):
            self.SpellList[i].trace('w', self.UpdateKnownSpells)
        for i in range(0, len(self.SpellList)):
            self.SpellButton[i].grid(row=1 + i, column=0, sticky='w', pady=5, padx = 5)
        #Arrange all the Spell Level Frames 
        for i in range(0, 4):
            Spellframes[i].grid(row=i+1, column = 0, sticky='ew', pady=3) #ew ensures that they all have the same width
        self.SpellBookListFrame.grid(row=1, column=0, pady=10, sticky='w')

    def open_spell_book(self):
        self.SpellBook.tkraise()
    
    def close_spell_book(self):
        self.MainPage.tkraise()

    def build_ability_page(self):
        self.AbilityPageTopFrame = Frame(self.AbilityPage)
        Label(self.AbilityPageTopFrame, text='Other Abilites').grid(row=0,column=1)
        ttk.Button(self.AbilityPageTopFrame, text='Back', bootstyle = 'outline', command= self.close_ability_page).grid(row=0, column=0, pady=5)
        self.AbilityPageTopFrame.grid(row=0, column=0, pady=5)

        self.AbilitiesListFrame = Frame(self.AbilityPage)
        #Label Frames for the Abilities
        Class_names = ['Rogue', 'Barbarian', 'Paladin', 'Sorcerer', 'Druid', 'Bard', 'Warlock', 'Monsters']
        Class_Frames = [ttk.Labelframe(self.AbilitiesListFrame, text= Class_names[i]) for i in range(0, len(Class_names))]

        self.AbilitiesList = [IntVar() for i in self.master.All_Abilities]
        self.AbilitiesButton = []
        for i in range(0,len(self.AbilitiesList)):
            if i < 3:
                frame = Class_Frames[0]
            elif i < 6:
                frame = Class_Frames[1]
            elif i < 7:
                frame = Class_Frames[2]
            elif i < 10:
                frame = Class_Frames[3]
            elif i < 12:
                frame = Class_Frames[4]
            elif i < 13:
                frame = Class_Frames[5]
            elif i < 14:
                frame = Class_Frames[6]
            elif i < 16:
                frame = Class_Frames[7]
            self.AbilitiesButton.append(ttk.Checkbutton(frame, text=self.master.All_Abilities[i], variable=self.AbilitiesList[i], onvalue=1, offvalue=0))

        #This ensures, that if a ability is clicked, the Ability list Display on the Main page updates, it is not the dict of the Page
        for i in range(0, len(self.AbilitiesList)):
            self.AbilitiesList[i].trace('w', self.UpdateKnownAbilities)
        for i in range(0, len(self.AbilitiesList)):
            self.AbilitiesButton[i].grid(row=1 + i, column=0, sticky='w', pady = 3, padx=3)
        for i in range(0,len(Class_Frames)):
            Class_Frames[i].grid(row=i, column = 0, sticky='ew', pady=5)
        self.AbilitiesListFrame.grid(row=1, column=0, pady=10, sticky='w')

    def open_ability_page(self):
        self.AbilityPage.tkraise()
    
    def close_ability_page(self):
        self.MainPage.tkraise()

    def update_ability_mod(self, mod_number, *arg):
        #Updates the Mod Number displayed if the input changes
        modifier = round((self.AbilityScoreValues[mod_number].get()-10)/2 -0.1)#calc Mod
        if self.AbilityScoreProfList[mod_number].get() == 1:#if proficient
            Prof = self.BasicStatValues[self.BasicStatNames.index('Proficiency')].get()
            if Prof != '':
                modifier += float(Prof)
        self.AbilityScoreMod[mod_number].config(text = str(int(modifier)))

    def update_all_ability_mod(self, *arg):
        for i in range(0,6):
            self.update_ability_mod(i)

    def UpdateKnownSpells(self, *arg): #Only Updates the Pages Spell List Display
        KnownSpellList = []
        for i in range(0, len(self.master.All_Spells)):
            if self.SpellList[i].get() == 1:
                KnownSpellList.append(self.master.All_Spells[i])
        self.SpellDisplayList.set(KnownSpellList)

    def UpdateKnownAbilities(self, *arg): #Only Updates the Pages Ability List Display
        KnownAbilitiesList = []
        for i in range(0, len(self.master.All_Abilities)):
            if self.AbilitiesList[i].get() == 1:
                KnownAbilitiesList.append(self.master.All_Abilities[i])
        self.AbilityDisplayList.set(KnownAbilitiesList)

    def fetch_default_stats(self):
        #this loads the new character default stats in the page dictionary
        path = 'New Character.json'
        file = open(path)
        self.name = 'New Character'
        self.stats = json.load(file)
        file.close()

    def fetch_Entity_stats(self, Player): #loades the stats of a already initialized Player from Controller into the stats dictionary of the Entity page
        self.name = Player.name
        self.stats['AC'] = Player.base_AC
        self.stats['HP'] = Player.HP
        self.stats['Proficiency'] = Player.proficiency
        self.stats['To_Hit'] = Player.base_tohit
        self.stats['Attacks'] = Player.base_attacks
        self.stats['DMG'] = Player.base_dmg
        self.stats['Level'] = Player.level

        self.stats['Str'] = Player.Str
        self.stats['Dex'] = Player.Dex
        self.stats['Con'] = Player.Con
        self.stats['Int'] = Player.Int
        self.stats['Wis'] = Player.Wis
        self.stats['Cha'] = Player.Cha

        self.stats['Saves_Proficiency'] = Player.saves_prof
        self.stats['Hero_or_Villain'] = Player.team

        self.stats['Damage_Type'] = Player.damage_type
        self.stats['Damage_Resistance'] = Player.damage_resistances
        self.stats['Damage_Immunity'] = Player.damage_immunity
        self.stats['Damage_Vulnerabilities'] = Player.damage_vulnerability
        
        self.stats['Spell_DC'] = Player.spell_dc
        self.stats['Spell_Mod'] = Player.spell_mod
        self.stats['Spell_Slot_1'] = Player.spell_slots[0]
        self.stats['Spell_Slot_2'] = Player.spell_slots[1]
        self.stats['Spell_Slot_3'] = Player.spell_slots[2]
        self.stats['Spell_Slot_4'] = Player.spell_slots[3]
        self.stats['Spell_Slot_5'] = Player.spell_slots[4]
        self.stats['Spell_Slot_6'] = Player.spell_slots[5]
        self.stats['Spell_Slot_7'] = Player.spell_slots[6]
        self.stats['Spell_Slot_8'] = Player.spell_slots[7]
        self.stats['Spell_Slot_9'] = Player.spell_slots[8]
        self.stats['Spell_List'] = Player.spell_list

        self.stats['Other_Abilities'] = Player.other_abilities
        self.stats['Sneak_Attack_Dmg'] = Player.sneak_attack_dmg
        self.stats['Lay_on_Hands_Pool'] = Player.lay_on_hands
        self.stats['Sorcery_Points'] = Player.sorcery_points

        self.stats['Position'] = Player.position_txt
        self.stats['Speed'] = Player.speed
        self.stats['Range_Attack'] = Player.range_attack
        
    def fetch_GUI_stats(self):
        #This function fetches the data that is currently in the GUI Entries to the dictionary

        #Name
        self.name = self.NameEntry.get()

        #Basic Stuff
        BasicStuffNames = ['AC', 'HP', 'Proficiency', 'To_Hit', 'Attacks', 'DMG', 'Level', 'Hero_or_Villain']
        for i in range(0,len(BasicStuffNames)):
            if BasicStuffNames[i] == 'DMG':
                self.stats[BasicStuffNames[i]] = float(self.BasicStatValues[i].get()) #fetch all these Entries
            else:
                self.stats[BasicStuffNames[i]] = int(self.BasicStatValues[i].get())

        #Ability Scores
        AbilityScoreNames = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        for i in range(0,6):
            self.stats[AbilityScoreNames[i]] = self.AbilityScoreValues[i].get() #fetch all Abl Score Entries
        #Check all Buttons and add Proficiencies
        ProfText = ''
        for i in range(0,6):
            if self.AbilityScoreProfList[i].get() == 1:
                ProfText += AbilityScoreNames[i] + ' '
        if ProfText == '':
            ProfText = 'none'
        self.stats['Saves_Proficiency'] = ProfText

        self.stats['Damage_Type'] = self.DMGTypeEntry.get()
        ResText = ''
        ImmText = ''
        VulText = ''
        for i in range(0,len(self.master.DMG_Types)):
            if self.DMGResList[i].get() == 1:
                ResText += self.master.DMG_Types[i] + ' '
            if self.DMGImmList[i].get() == 1:
                ImmText += self.master.DMG_Types[i] + ' '
            if self.DMGVulList[i].get() == 1:
                VulText += self.master.DMG_Types[i] + ' ' 
        #if no Resistance then none
        if ResText == '':
            ResText = 'none'
        if ImmText == '':
            ImmText = 'none'
        if VulText == '':
            VulText = 'none'
        self.stats['Damage_Resistance'] = ResText
        self.stats['Damage_Immunity'] = ImmText
        self.stats['Damage_Vulnerabilities'] = VulText

        #Spellcasting
        self.stats['Spell_Mod'] = int(self.SpellModEntry.get())
        self.stats['Spell_DC'] = int(self.SpellDCEntry.get())
        for i in range(0,9):
            self.stats['Spell_Slot_' + str(i+1)] = int(self.SpellLevelEntries[i].get())
        SpellText = ''
        #check all spell checkbuttons
        for i in range(0, len(self.SpellList)):
            if self.SpellList[i].get() == 1:
                SpellText += self.master.All_Spells[i] + ' '
        if SpellText == '':
            SpellText = 'none'
        self.stats['Spell_List'] = SpellText

        #Position
        self.stats['Speed'] = int(self.SpeedEntry.get())
        self.stats['Range_Attack'] = int(self.Range_Attack_Value.get())
        self.stats['Position'] = 'front'
        if self.PositionValue.get() == 1:
            self.stats['Position'] = 'middle'
        elif self.PositionValue.get() == 2:
            self.stats['Position'] = 'back'
        

        #Other Stuff
        AbilitiesText = ''
        #check all other abilites
        for i in range(0, len(self.AbilitiesList)):
            if self.AbilitiesList[i].get() == 1:
                AbilitiesText += self.master.All_Abilities[i] + ' '
        if AbilitiesText == '':
            AbilitiesText = 'none'
        self.stats['Other_Abilities'] = AbilitiesText
        self.stats['Sneak_Attack_Dmg'] = float(self.SneakAttackDmgEntry.get())
        self.stats['Lay_on_Hands_Pool'] = int(self.LayOnHandsEntry.get())
        self.stats['Sorcery_Points'] = int(self.SorceryPointsEntry.get())

    def load_default_stats(self):
        #This is called when the #new character button is pressed, restore default stats 
        self.fetch_default_stats() #fetch default stats into dict 
        self.update_page() #update the Entries of page

    def load_Entity_stats(self, Player):
        #This is called when an Entity button is pressed, fetches and loads the Charatcer stats 
        self.fetch_Entity_stats(Player) #fetch default stats into dict 
        self.update_page() #update the Entries of page

    def save_stats_to_file(self):#Entity_stats is now a dict and saved to json
        with open('./Entities/'+  self.name + '.json', "w") as f:  #write to json file
            json.dump(self.stats, f, indent=4)

    def update_Entry(self, Entry, NewText):
        Entry.delete(0, 'end')
        Entry.insert(0, str(NewText))

    def update_page(self):
        #This Function just filles the Page with the Information from the current dictionary
        
        #Name
        self.update_Entry(self.NameEntry, self.name)

        #Basic Stuff
        BasicStuffNames = ['AC', 'HP', 'Proficiency', 'To_Hit', 'Attacks', 'DMG', 'Level', 'Hero_or_Villain']
        for i in range(0,len(BasicStuffNames)):
            self.BasicStatValues[i].set(self.stats[BasicStuffNames[i]]) #update all these Entries
        
        #Ability Scores
        AbilityScoreNames = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        for i in range(0,6):
            self.AbilityScoreValues[i].set(self.stats[AbilityScoreNames[i]]) #update all Abl Score Entries
        for i in range(0,6):
            if AbilityScoreNames[i] in self.stats['Saves_Proficiency']:
                self.AbilityScoreProfList[i].set(1)
            else:
                self.AbilityScoreProfList[i].set(0)

        #Damage Types
        self.DMGTypeEntry.set(self.stats['Damage_Type'])
        for i in range(0,len(self.master.DMG_Types)):
            if self.master.DMG_Types[i] in self.stats['Damage_Resistance']:
                self.DMGResList[i].set(1)
            else: 
                self.DMGResList[i].set(0)
            
            if self.master.DMG_Types[i] in self.stats['Damage_Immunity']:
                self.DMGImmList[i].set(1)
            else: 
                self.DMGImmList[i].set(0)
            
            if self.master.DMG_Types[i] in self.stats['Damage_Vulnerabilities']:
                self.DMGVulList[i].set(1)
            else: 
                self.DMGVulList[i].set(0)
        
        #Spellcasting
        self.update_Entry(self.SpellModEntry, self.stats['Spell_Mod'])
        self.update_Entry(self.SpellDCEntry, self.stats['Spell_DC'])
        for i in range(0,9):
            self.update_Entry(self.SpellLevelEntries[i], self.stats['Spell_Slot_' + str(i+1)])
        for i in range(0, len(self.SpellList)):
            if self.master.All_Spells[i] in self.stats['Spell_List']:
                self.SpellList[i].set(1)
            else:
                self.SpellList[i].set(0)
        self.UpdateKnownSpells()

        #Position
        self.update_Entry(self.SpeedEntry, self.stats['Speed'])
        self.Range_Attack_Value.set(int(self.stats['Range_Attack']))
        self.PositionValue.set(0)
        if 'middle' in self.stats['Position']:
            self.PositionValue.set(1)
        elif 'back' in self.stats['Position']:
            self.PositionValue.set(2)

        #Other Stuff
        for i in range(0, len(self.AbilitiesList)):
            if self.master.All_Abilities[i] in self.stats['Other_Abilities']:
                self.AbilitiesList[i].set(1)
            else:
                self.AbilitiesList[i].set(0)
        self.update_Entry(self.SneakAttackDmgEntry, self.stats['Sneak_Attack_Dmg'])
        self.update_Entry(self.LayOnHandsEntry, self.stats['Lay_on_Hands_Pool'])
        self.update_Entry(self.SorceryPointsEntry, self.stats['Sorcery_Points'])

        #update the Modifier Labels
        self.update_all_ability_mod()

        #save the Entity changes
    def save_Entity(self):
        self.fetch_GUI_stats() #fetch current data im GUI into stats dict
        self.save_stats_to_file() #write the data from dict to json file
        self.master.change_to_HomePage_saved() #return to homepage and reload

    def delete_Entity(self):
        #Are you sure?
        RUSure = ttk.Toplevel()
        RUSure.geometry("320x120")
        RUSure.title('Delete Character?')
        ttk.Button(RUSure, text='hi', bootstyle='outline').pack
        Label(RUSure, text= "Are you sure you want to delete " + self.name + '?').pack(pady=10)
        #Yes, No, Buttons
        ttk.Button(RUSure, text='Yeah, kill it!', bootstyle='outline', command= partial(self.delete_Entity_and_go_back, RUSure)).pack()
        ttk.Button(RUSure, text='Hell no, go Back! Go Back!', bootstyle="outline", command= partial(self.abbort_delete, RUSure)).pack(pady=5)
        #Make the window jump above all
        RUSure.attributes('-topmost',True)
        RUSure.mainloop()

    def delete_Entity_and_go_back(self, Open_Window):
        Open_Window.destroy()
        if os.path.isfile('./Entities/' + self.name + '.json'):
            os.remove('./Entities/' + self.name + '.json')
        else:    ## Show an error ##
            print("Error: Entity not found: " + self.name)
        self.master.change_to_HomePage_saved()

    def abbort_delete(self, Open_Window):
        Open_Window.destroy()

class Archive(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.Build_Archive() #build up the Page

    def Build_Archive(self):
        #Search
        self.search_label = Label(self, text='Search Archive:')
        self.search_entry = Entry(self, bd=5, width=12)
        self.search_entry.insert(0, 'test')

        #create buttons for heros
        self.buttons_heros = [ttk.Button(self, text=str(i.name), width =11, bootstyle="outline success", command=partial(self.master.change_to_EntityPage_Character, i, self)) for i in self.master.Archive_Heros]

        #create a button for every monster in the Monster Manual
        self.buttons_monsters = [ttk.Button(self, text=str(i.name), width =11, bootstyle='outline danger', command=partial(partial(self.master.change_to_EntityPage_Character, i, self))) for i in self.master.Archive_MonsterManuel]

        Label(self, text='Heros:').grid(row=1, column=0, columnspan=2, pady =5)
        Label(self, text='Monster Manuel:').grid(row=1, column=3, columnspan=4, pady =5)
        Label(self, text='', width= 6).grid(row=1, column=2)

        #Back Button
        ttk.Button(self, text='Back', bootstyle = 'outline', command=self.master.change_to_current_EntityPage).grid(row=0, column=0, pady = 10)

        #order Charcater/add Buttons
        for i in range(0,len(self.buttons_heros)):
            self.buttons_heros[i].grid(row=int(i/2)+2, column=(i%2), pady =2, padx=2)
        for i in range(0,len(self.buttons_monsters)):
            self.buttons_monsters[i].grid(row=int(i/3)+2, column=(i%3)+3, pady =2, padx=2)

class DM_page(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        self.current_Fighter = False   #will later be changed
        self.build_page()
        
    def build_page(self):
        for widgets in self.winfo_children():
            widgets.destroy()

        pady=3
        padx=3
        #Back Button
        self.b_Back = ttk.Button(self, text='Back',bootstyle='outline' , command= self.back_home)
        self.b_Back.grid(row=0, column=0, pady=pady)

        #create buttons for Fighters
        self.buttons_Fighters = []
        for player in self.master.Fighters:
            if player.team == 0:
                style = 'success outline'
            else:
                style = 'danger outline'
            self.buttons_Fighters.append(ttk.Button(self, text=str(player.name), width =12, bootstyle=style, command=partial(self.master.change_to_EntityPage_Character, player, self)))
        self.Entry_Fighters = [Entry(self, width =5) for i in self.master.Fighters]
        
        #Init Entries
        self.Entry_Init = [Entry(self, text='', width=4) for i in self.master.Fighters]
        self.b_Init = ttk.Button(self, text= 'Init Sort', bootstyle='outline success', command=self.Init_sort)
        self.b_Init.grid(row=0, column=1, pady=pady)

        #Concentration Buttons
        self.b_concentration = [ttk.Button(self, text='C', bootstyle='outline warning', width =1, command=partial(self.set_concentration, i)) for i in self.master.Fighters]  #apply

        #Damgage Entries
        self.Entry_dmg = [Entry(self, text='', width=3) for i in self.master.Fighters]    #how much dmg
        self.Entry_dmg_type = [ttk.Combobox(self, values=self.master.DMG_Types, width= 10, state='readonly') for i in self.master.Fighters]   #what kind of dmg
        for dmg_type in self.Entry_dmg_type:
            dmg_type.set('slashing')
        self.b_dmg = [ttk.Button(self, text='apply', width =4, bootstyle='outline', command=partial(self.apply_dmg, i)) for i in self.master.Fighters]  #apply

        #create Label
        self.label_Player_Init = Label(self, text='Init')
        self.label_Player_Init.grid(row=1, column=0, padx=padx, pady=pady)
        self.label_Player = Label(self, text='Players')
        self.label_Player.grid(row=1, column=1, padx=padx, pady=pady)
        self.label_Player_HP = Label(self, text='Hit Points')
        self.label_Player_HP.grid(row=1, column=2, columnspan=2, padx=padx, pady=pady)
        Label(self, text='C').grid(row=1, column=4, padx=padx, pady=pady)
        Label(self, text='Dmg').grid(row=1, column=5, padx=padx, pady=pady)
        Label(self, text='Dmg type').grid(row=1, column=6, padx=padx, pady=pady)
        

        #order Charcater/add Buttons
        for i in range(0,len(self.buttons_Fighters)):
            self.buttons_Fighters[i].grid(row=i+2, column=1, padx=padx, pady=pady)
            self.Entry_Fighters[i].grid(row=i+2, column=2, padx=padx, pady=pady)
            self.Entry_Fighters[i].delete(0, 'end')
            self.Entry_Fighters[i].insert(0, str(self.master.Fighters[i].CHP))
            self.Entry_Init[i].grid(row=i+2, column=0, padx=padx, pady=pady)
            self.Entry_Init[i].insert(0, str(self.master.Fighters[i].initiative))
            Label(self, width =5, anchor="w", text='/' + str(self.master.Fighters[i].HP)).grid(row=i+2, column=3, padx=padx, pady=pady)
            self.b_concentration[i].grid(row=i+2, column=4, padx=padx, pady=pady)
            if self.master.Fighters[i].concentration == 1:
                self.b_concentration[i].configure(bootstyle = 'warning solid')
            self.Entry_dmg[i].grid(row=i+2, column=5, padx=padx, pady=pady)
            self.Entry_dmg_type[i].grid(row=i+2, column=6, padx=padx, pady=pady)
            self.b_dmg[i].grid(row=i+2, column=7, padx=padx, pady=pady)
            

        ttk.Button(self, width=9, text = 'Previous', bootstyle='outline', command=self.previous_Fighter).grid(row= len(self.buttons_Fighters)+2, column=1)
        ttk.Button(self, width=9, text = 'Next', bootstyle='outline', command=self.next_Fighter).grid(row= len(self.buttons_Fighters)+2, column=2, columnspan=2)

        if self.current_Fighter in self.master.Fighters:
            self.change_to_Fighter(self.current_Fighter)
        
    def back_home(self):
        for i in range(len(self.master.Fighters)):
            self.master.Fighters[i].CHP = int(self.Entry_Fighters[i].get())
        self.master.change_to_HomePage()

    def Init_sort(self):
        for i in range(len(self.master.Fighters)):
            self.master.Fighters[i].CHP = int(self.Entry_Fighters[i].get())
        for i in range(len(self.Entry_Init)):
            self.master.Fighters[i].initiative = int(self.Entry_Init[i].get())
        self.master.Fighters = sorted(self.master.Fighters, reverse = True, key=lambda x: x.initiative)
        self.build_page()
        self.root.update()
        self.change_to_Fighter(self.master.Fighters[0])

    def next_Fighter(self):
        index = self.master.Fighters.index(self.current_Fighter)
        if index == len(self.master.Fighters)-1:
            index = -1
        self.change_to_Fighter(self.master.Fighters[index + 1])

    def previous_Fighter(self):
        index = self.master.Fighters.index(self.current_Fighter)
        if index == 0:
            index = len(self.master.Fighters)
        self.change_to_Fighter(self.master.Fighters[index - 1])

    def change_to_Fighter(self, Fighter):
        self.current_Fighter = Fighter
        Fighters = self.master.Fighters
        for i in range(0,len(Fighters)):
            if Fighters[i].team == 0:
                if Fighters[i] == self.current_Fighter:
                    self.buttons_Fighters[i].configure(bootstyle='success solid')
                else:
                    self.buttons_Fighters[i].configure(bootstyle='success outline')
            else:
                if Fighters[i] == self.current_Fighter:
                    self.buttons_Fighters[i].configure(bootstyle='danger solid')
                else:
                    self.buttons_Fighters[i].configure(bootstyle='danger outline')

    def apply_dmg(self,Fighter):
        index = self.master.Fighters.index(Fighter)
        dmg = int(self.Entry_dmg[index].get())
        #DMG Types
        if dmg > 0:
            dmg_type = self.Entry_dmg_type[index].get()
            print(dmg_type)
            if dmg_type == '':
                dmg_type = 'true'
            if dmg_type in Fighter.damage_resistances:
                print(Fighter.name + ' is resistant against ' + dmg_type)
                dmg = dmg/2
            if dmg_type in Fighter.damage_immunity:
                print(Fighter.name + ' is immune against ' + dmg_type)
                dmg = 0
            if dmg_type in Fighter.damage_vulnerability:
                print(Fighter.name + ' is vulnerable against ' + dmg_type)
                dmg = dmg*2
        Fighter.CHP -= int(dmg)
        if Fighter.concentration == 1 and dmg > 0:
            DC = 10
            if dmg/2 > 10:
                DC = int(dmg/2 + 0.5)
            messagebox.showinfo('Concentration Check',Fighter.name + ' must make concentration check DC: ' + str(DC))
        #delete the Entriess
        self.Entry_dmg[index].delete(0, 'end')
        self.Entry_dmg_type[index].delete(0, 'end')
        self.Entry_Fighters[index].delete(0, 'end')
        self.Entry_Fighters[index].insert(0, str(self.master.Fighters[index].CHP))
    
    def set_concentration(self,Player):
        if Player.concentration == 0:
            Player.concentration = 1
            self.b_concentration[self.master.Fighters.index(Player)].configure(bootstyle = 'warning solid')
        else:
            Player.concentration = 0
            self.b_concentration[self.master.Fighters.index(Player)].configure(bootstyle = 'warning outline')

def StartGUI():
    root = ttk.Window(themename="cyborg")
    root.title("DND Encounter Simulator")
    root.geometry('790x760')
    if platform.system() == 'Windows':
        root.geometry('850x880')
    # Create A Main frame
    MainFrame = Frame(root)
    MainFrame.pack(fill=BOTH,expand=1)
    # Create Frame for X Scrollbar
    XFrame = Frame(MainFrame)
    XFrame.pack(fill=X,side=BOTTOM)
    # Create A Canvas
    MainCanvas = Canvas(MainFrame)
    MainCanvas.pack(side=LEFT,fill=BOTH,expand=1)
    # Add A Scrollbars to Canvas
    XScrollbar = ttk.Scrollbar(XFrame,orient=HORIZONTAL,command=MainCanvas.xview)
    XScrollbar.pack(side=BOTTOM,fill=X)
    YScrollbar = ttk.Scrollbar(MainFrame,orient=VERTICAL,command=MainCanvas.yview)
    YScrollbar.pack(side=RIGHT,fill=Y)
    #Mouse Weel
    def _on_mousewheel(event):
        MainCanvas.yview_scroll(-1*(event.delta), "units")
    MainCanvas.bind_all("<MouseWheel>", _on_mousewheel)
    # Configure the canvas
    MainCanvas.configure(xscrollcommand=XScrollbar.set)
    MainCanvas.configure(yscrollcommand=XScrollbar.set)
    MainCanvas.bind("<Configure>",lambda e: MainCanvas.config(scrollregion= MainCanvas.bbox(ALL))) 
    # Create Another Frame INSIDE the Canvas
    GUIFrame = Frame(MainCanvas)
    # Add that New Frame a Window In The Canvas
    MainCanvas.create_window((0,0),window=GUIFrame, anchor="nw")
    app = Controller(GUIFrame)
    app.pack(expand=True, fill=BOTH, padx=10)

    root.mainloop()