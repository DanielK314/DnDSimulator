import numpy as np
from numpy import argmin
from copy import copy
from datetime import datetime

from Entity_class import *

def fight_ongoing_check(fight): #this function takes the fighters and checks if more then one team is still alive
    fighter_tag_list = []
    for i in range(0, len(fight)):
        if fight[i].CHP > 0 and fight[i].team not in fighter_tag_list:
            fighter_tag_list.append(fight[i].team)
    if len(fighter_tag_list) > 1:
        return True
    else:
        return False

def do_the_fighting(fighters_unsorted): #here a list of fighters from different teams
    fight = roll_for_initiative(fighters_unsorted)     #roll all inits and return sorted list
    Init_counter = 0
    DM = fighters_unsorted[0].DM
    DM.reset() #resets the DM at start of fighting

    DM.say('Runde ' + str(DM.rounds_number) + ' - Heros Teamhealth: ' + str(teamhealth(fight, 0)))

    while fight_ongoing_check(fight) == True:
        player = fight[Init_counter]

        if player.state != -1:
            print_text = '_____________'
            DM.say(print_text)
        if player.state == 1:                            #player is alive
            enemies_left_list = [x for x in fight if x.team != player.team and x.state == 1]

            player.start_of_turn()

            if enemies_left_list != []:   #if enemies left, call an AI for the turn    
                player.AI.do_your_turn(fight)

        #if player is dead, make death save
        if player.state == 0 and player.team == 0 and player.NPC == 0:
            player.make_death_save()

        #End of the Turn
        player.end_of_turn()   #after turn, reset counter, haste, stuff, all that happends at end of turn

        Init_counter += 1                                #set Init counter, reset round counter if ness.
        if Init_counter >= len(fight):
            Init_counter = 0
            DM.rounds_number += 1
            DM.say('')
            DM.say('Runde ' + str(DM.rounds_number) + ' - Heros Teamhealth: ' + str(teamhealth(fight, 0)))


    #Only one Team is left alive
    DM.say('')
    DM.say("Fight over")
    for x in fighters_unsorted:
        if x.CHP == 0:
            x.state = -1 #Everone who is unconscious in the loser Team is practically Dead now
        if x.is_summoned:  #let summend characters vanish after dead
            fight.remove(x)
    DM.say('HP left:')
    for i in fighters_unsorted:
        DM.say(str(i.name) + " " + str(i.CHP))
    DM.say('')
    DM.say('Damage dealed:')
    for i in fighters_unsorted:
        DM.say(str(i.name) + " " + str(i.dmg_dealed))
    DM.say('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    DM.say('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    DM.say('')
    DM.say('')
    
    winner_team = 0
    for i in fighters_unsorted:
        if i.CHP > 0:
            winner_team = i.team
            break
    
    return winner_team, DM.rounds_number

#all statistical functions call this one and this one calls the 'do the fighting'
#for multiple fightings, change here

def roll_for_initiative(fighters_unsorted): #takes list of fighters and return init order
    for i in fighters_unsorted:
        i.initiative = i.make_check(1)   #make Dex roll
    initiative = sorted(fighters_unsorted, reverse = True, key=lambda x: x.initiative)
            #roll all inits and return sorted list
    return initiative

def enemies_left_sort(fight, TeamTag):
    enemies_left_list = [x for x in fight if x.team != TeamTag and x.state == 1]
    return enemies_left_list

def run_simulation(repetition, fighters, progress = False):
    damage_statistic = []
    winner = []
    rounds_number = []
    deaths = []
    unconscious = []
    DeathNumber = np.zeros(repetition)#Counts the absolute Deaths per Repetition (only for team 0)
    TeamHealth = [] #List with how much of the absolute Team Health is left
    TeamHP = 0
    for fighter in fighters:
        if fighter.team == 0:
            TeamHP += fighter.HP

    for i in range(0,repetition):
        percent = str(round(i/repetition*100, 1))
        if progress == True:
            print('Progress : ' + percent +'%')
        simulation_results = do_the_fighting(fighters)
        winner.append(simulation_results[0])         # do the fight and get the winner, list of 0 (heros) or 1 (enemies)
        rounds_number.append(simulation_results[1])         # do the fight and get the rounds number
        damage_statistic.append([k.dmg_dealed for k in fighters])  #get dmg statistic

        for j in fighters:
            if j.state == -1:
                deaths.append(j.name)
                if j.team == 0:
                    DeathNumber[i] += 1 #Counts the absolute Deaths per Repetition
        
        TeamCHP = 0
        for fighter in fighters:
            if fighter.team == 0:
                TeamCHP += fighter.CHP
        TeamHealth.append(TeamCHP/TeamHP) #how much Team health is left

        UnconsciousSum = 0
        for j in fighters:
            if j.team == 0:
                UnconsciousSum += j.unconscious_counter
        unconscious.append(UnconsciousSum)
        
        for l in fighters:
            l.long_rest()           #rest by doing a long Rest
    damage_statistic_sorted = []
    for j in range(0, len(fighters)):          #sort dmg statistic
        damage_statistic_sorted.append([damage_statistic[i][j] for i in range(0,repetition)])
    names = [i.name for i in fighters]         #get names 

    return names, damage_statistic_sorted, winner, rounds_number, deaths, unconscious, DeathNumber, TeamHealth

def most_valuable_player(repetition, fighters):
    DM = fighters[0].DM
    Heros_List = [fighter for fighter in fighters if fighter.team == 0]
    if len(Heros_List) == 1: # if only one Heros is in the team
        return [[Heros_List[0].name], [0], Heros_List[0].name]
    fighters_without_one_hero = copy(fighters)
    player_name = []
    win_probability_without_player = []
    for i in range(0, len(fighters_without_one_hero)):
        if fighters_without_one_hero[i].team == 0:
            fighters_without_one_hero.remove(fighters[i])
            player_name.append(fighters[i].name) 
            names, damage_statistic_sorted, winner, rounds_number, deaths, unconscious, DeathNumber, TeamHealth = run_simulation(repetition, fighters_without_one_hero)
            
            #calc win prob.
            wins = 0
            defeats = 0
            for i in winner:
                if i == 0:
                    wins += 1
                else:
                    defeats += 1
            win_probability = wins/(wins + defeats)
            win_probability_without_player.append(win_probability)

            DM.say('Win Probability = ' + str(win_probability) + '\n')
            fighters_without_one_hero = copy(fighters)
    
    mvp_index = argmin(win_probability_without_player)
    DM.say('Most valuable player: ' + str(player_name[mvp_index]))
    return player_name, win_probability_without_player, player_name[mvp_index]

def spell_cast_recap(repetition, fighters, text_result):  #only calls the objects data, simulation must be run beforehand
    for fighter in fighters:
        for spell_name, spell in fighter.SpellBook:
            if spell.was_cast > 0:
                text_result += str(fighter.name) + ' cast ' + spell.spell_text + str(round(spell.was_cast/repetition,3)) + '\n'
    return text_result

def full_statistical_recap(repetition, fighters):
    DM = fighters[0].DM
    DM.start_time = datetime.now()

    #generate a str that will be returned
    text_result = 'Simulation estimates:\n'

    #run simulation
    names, damage_statistic_sorted, winner, rounds_number, deaths, unconscious, DeathNumber, TeamHealth = run_simulation(repetition, fighters, progress=True)
    wins = 0
    defeats = 0
    for i in winner:
        if i == 0:
            wins += 1
        else:
            defeats += 1
    win_probability = wins/(wins + defeats)

    # run the most valuable player function with less repetitions
    #This section was removed due to high performance impact
    if False:
        DM.block_print()
        mvp_repetitions = int(repetition/10) +1
        if mvp_repetitions > 100:
            mvp_repetitions = 100
        player_name, win_probability_without_player, mvp = most_valuable_player(mvp_repetitions, fighters)
        DM.enable_print()


    # Calaculate death rates  (if they loose, they all die obviously)
    DeathProbabilities = []
    Deaths_text_result = ''
    for i in fighters:
        if i.team != 1:
            fighter_has_died_counter = 0   #death counter
            for j in deaths:
                if i.name == j:   #if name is in deaths from simulation
                    fighter_has_died_counter += 1
            if fighter_has_died_counter > 0:
                death_probability = fighter_has_died_counter/repetition
                Deaths_text_result += str(i.name) + ' dies: ' + str(round(death_probability*100,2)) + ' %\n'
            else:
                death_probability = 0
            DeathProbabilities.append(death_probability) # for late calc difficulty

    #Calculate the Difficulty
    Difficulty = calculate_difficulty(1-win_probability, np.mean(rounds_number), DeathProbabilities, unconscious, DeathNumber, TeamHealth)
    Difficulty_Text = ['0',
    'Insignificant', 'Easy', 'Medium', 'Challenging', 'Hard',
    'Brutal', 'Insane', 'Death', 'Hell', 'How Dare You?']

    Difficulty_Meaning = ['0',
    'No chance of failure and the heroes will still have most of their recources',
    'A low risk fight, that will leave but a scratch.',
    'This might take some efford. Death will only come to those who take it lightly.',
    'Finally, a worthy fight that will force the heroes to show what they are made of.',
    'Death is a real danger now, fatal for those how are not prepared.',
    'Some might not survive this fight, it is deadly and unforgiving.',
    'This is madness and could bring death to all. Be cautious.',
    'A total annihilation is likely. If some survive, at what cost?',
    'Burn them all. The gods must have forsaken these poor heroes.',
    'What are you thinking? You must hate them...'
    ]

    damage_player = [np.mean(damage_statistic_sorted[i]) for i in range(0, len(damage_statistic_sorted))]

    text_result += '_____________________\n'
    text_result += 'Difficulty: ' + Difficulty_Text[Difficulty] + '\n'
    text_result += 'Win Probability: ' + str(round(win_probability*100, 3)) + ' %\n'
    text_result += 'Fight Length: ' + str(round(np.mean(rounds_number),1)) + ' +/- ' + str(round(np.std(rounds_number),1)) + '\n'
    text_result += 'Team Health: ' + str(round(np.mean(TeamHealth)*100,1)) + ' %\n'
    text_result += 'Total Party Kill: ' + str(round((1-win_probability)*100, 3)) + ' %\n\n'
    text_result += Difficulty_Meaning[Difficulty] + '\n\n'
    text_result += '----DEATHS----\n'
    text_result += Deaths_text_result
    text_result += '\n'
    if win_probability > 0.01:
        text_result += '----PLAYER PERFORMANCE----\n'

    #calculating the performance of the Players
        #Perfprmance as the part of Dmg done:
        player = [x for x in fighters if x.team == 0]
        damage_list = []
        for i in range(0, len(fighters)):
            if fighters[i].team == 0:
                damage_list.append(damage_player[i])
        performance_damage = np.zeros(len(damage_list))
        for i in range(0, len(performance_damage)):
            performance_damage[i] = damage_list[i]/np.max(damage_list)
        for i in range(0,len(player)):
            text_result += str(player[i].name) + ' : ' + str(int(100*performance_damage[i])) + '/100 \n'

    text_result += '\n'
    text_result += '----DAMAGE DONE----\n'
    for i in range(0,len(fighters)):
        text_result += fighters[i].name + ' : ' + str(int(damage_player[i])) + '\n'
    text_result += '\n'
    text_result += '----SPELLS CAST----\n'
    text_result = spell_cast_recap(repetition, fighters, text_result)


    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    f = open(application_path + '/simulation_result.txt', 'w')
    f.write(text_result)

    return text_result

def calculate_difficulty(TPKChance, Length, DeathProbabilities, Unconscious, DeathNumber, TeamHealth):
    #TPK Chance = 1 - Winchance 
    #Length of fight
    #Deathprob List of Death chances 
    #Unconscious Counters List
    #Death Number is absolute Deaths per Simulation
    #TeamHealth is list with how much of the total team CHP was left per run
    #This function tries to estimate how difficult the encounter would be
    #1 - Insignificant, no chance of fail
    #2 - Easy, no death chance, easy fight    
    #3 - Medium, will take some efford, minimal death chance
    #4 - Challenging, some fight, chane of fail, flee maybe
    #5 - Hard, will take efford, chance of death
    #6 - Brutal, will propably lead to some deaths, maybe TPK
    #7 - Insane, real chance of TPK
    #8 - Death, a TPK is likely
    #9 - Hell, a TPK is highly likely
    #10 - How Dare You, just what were you thinking?
    DeathPerPlayer = sum(DeathProbabilities)/len(DeathProbabilities)
    MinDeaths = np.mean(np.sort(DeathNumber)[0:int(len(DeathNumber)/20+1)]) #lowest 5%
    MinUnconscious = np.mean(np.sort(Unconscious)[0:int(len(Unconscious)/20+1)]) #lowest 5%
    MeanTeamHealth = np.mean(TeamHealth)

    #HowDareYou
    if TPKChance > 0.9 and MinDeaths > 1:
        return 10 #This is a 90% TPK
    #Hell
    elif TPKChance > 0.75 and DeathPerPlayer > 0.85 and MinDeaths > 1:
        return 9 #This is likely TPK and at least 2 player die in any run
    #Death
    elif TPKChance > 0.5 and DeathPerPlayer > 0.6:
        return 8 #50% TPK, at least one Player dies in any run
    else:
        #TPKChance>, Length>, >DeathPerPlayer MinDeath>, MinUncon>, MeanTeamHealth<
        lv1 = [0.005, 3, 0.01, 0, 0.5, 0.8]
        lv2 = [0.01, 5, 0.03, 0.1, 2, 0.7]
        lv3 = [0.02, 7, 0.15, 0.5, 4, 0.5]
        lv4 = [0.05, 10, 0.25, 1, 5, 0.3]
        lv5 = [0.2, 15, 0.33, 2, 10, 0.1]
        lv6 = [0.3, 20, 0.4, 2.5, 20, 0.05]
        Level = [lv1,lv2, lv3, lv4, lv5, lv6]
        Diff = 0
        while Diff < 6: #Is right, because Diff starts at 0
            #This Loop iterates the Boundries of the Level
            #If one Value is higher then the Boundry, the Difficulty Level is risen
            #else the current Diff is returned
            if TPKChance > Level[Diff][0]:
                Diff +=1
            elif Length > Level[Diff][1]:
                Diff +=1
            elif DeathPerPlayer > Level[Diff][2]:
                Diff +=1
            elif MinDeaths > Level[Diff][3]:
                Diff +=1
            elif MinUnconscious > Level[Diff][4]:
                Diff +=1
            elif MeanTeamHealth < Level[Diff][5]:
                Diff +=1
            else:
                return Diff + 1 #Diff starts with 0, but is 1
        return 7
        
def teamhealth(fight, teamtag):
    healthlist = []
    for i in range(0, len(fight)):                  #sort team
        if fight[i].team == teamtag and fight[i].CHP > 0:
            healthlist.append(fight[i].CHP)
    return sum(healthlist)