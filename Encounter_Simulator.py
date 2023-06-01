import numpy as np
from random import *
from numpy import argmin
from copy import copy

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
    rounds_number = 1
    DM = fighters_unsorted[0].DM

    DM.say('Runde ' + str(rounds_number) + ' - Heros Teamhealth: ' + str(teamhealth(fight, 0)))

    while fight_ongoing_check(fight) == True:
        player = fight[Init_counter]
        if player.state == 1:                            #player is alive
            teamtag = player.team                        #which team        
            enemies_left_list = enemies_left_sort(fight, teamtag)

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
            rounds_number += 1
            DM.say('')
            DM.say('Runde ' + str(rounds_number) + ' - Heros Teamhealth: ' + str(teamhealth(fight, 0)))


    #Only one Team is left alive
    DM.say('')
    DM.say("Fight over")
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
    
    return winner_team, rounds_number

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

def run_simulation(repetition, fighters):
    damage_statistic = []
    winner = []
    rounds_number = []
    deaths = []

    for i in range(0,repetition):
        simulation_results = do_the_fighting(fighters)
        winner.append(simulation_results[0])         # do the fight and get the winner, list of 0 (heros) or 1 (enemies)
        rounds_number.append(simulation_results[1])         # do the fight and get the rounds number
        damage_statistic.append([k.dmg_dealed for k in fighters])  #get dmg statistic

        for j in fighters:
            if j.state == -1:
                deaths.append(j.name)
        
        for l in fighters:
            l.long_rest()           #rest by doing a long Rest
    damage_statistic_sorted = []
    for j in range(0, len(fighters)):          #sort dmg statistic
        damage_statistic_sorted.append([damage_statistic[i][j] for i in range(0,repetition)])
    names = [i.name for i in fighters]         #get names 

    return names, damage_statistic_sorted, winner, rounds_number, deaths

def most_valuable_player(repetition, fighters):
    DM = fighters[0].DM
    fighters_without_one_hero = copy(fighters)
    player_name = []
    win_probability_without_player = []
    for i in range(0, len(fighters_without_one_hero)):
        if fighters_without_one_hero[i].team == 0:
            fighters_without_one_hero.remove(fighters[i])
            player_name.append(fighters[i].name) 
            names, damage_statistic_sorted, winner, rounds_number, deaths = run_simulation(repetition, fighters_without_one_hero)
            
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
    for i in fighters:
        if i.fire_bolt_cast > 0:
            text_result += str(i.name) + ' cast fire bolt: ' + str((i.fire_bolt_cast)/repetition) + '\n'
            i.fire_bolt_cast = 0
        if i.entangle_cast > 0:
            text_result += str(i.name) + ' cast entangle: ' + str(i.entangle_cast/repetition) + '\n'     
            i.entangle_cast = 0
        if i.burning_hands_cast > 0:
            text_result += str(i.name) + ' cast burning hand: ' + str(i.burning_hands_cast/repetition) + '\n'
            i.burning_hands_cast = 0
        if i.cure_wounds_cast > 0:
            text_result += str(i.name) + ' cast cure wounds: ' + str(i.cure_wounds_cast/repetition) + '\n'
            i.cure_wounds_cast = 0
        if i.healing_word_cast > 0:
            text_result += str(i.name) + ' cast healing word: ' + str(i.healing_word_cast/repetition) + '\n'
            i.healing_word_cast = 0
        if i.magic_missile_cast > 0:
            text_result += str(i.name) + ' cast magic missile: ' + str(i.magic_missile_cast/repetition) + '\n'
            i.magic_missile_cast = 0
        if i.aganazzars_sorcher_cast > 0:
            text_result += str(i.name) + ' cast aganazzarssorcher: ' + str(i.aganazzars_sorcher_cast/repetition) + '\n'
            i.aganazzars_sorcher_cast = 0
        if i.scorching_ray_cast > 0:
            text_result += str(i.name) + ' cast scorching ray: ' + str(i.scorching_ray_cast/repetition) + '\n'
            i.scorching_ray_cast = 0
        if i.fireball_cast > 0:
            text_result += str(i.name) + ' cast fireball: ' + str(i.fireball_cast/repetition) + '\n'
            i.fireball_cast = 0
        if i.haste_cast > 0:
            text_result += str(i.name) + ' cast haste: ' + str(i.haste_cast/repetition) + '\n'
            i.haste_cast = 0
        if i.shield_cast > 0:
            text_result += str(i.name) + ' cast shield: ' + str(i.shield_cast/repetition) + '\n'
            i.shield_cast = 0
        if i.eldritch_blast_cast > 0:
            text_result += str(i.name) + ' cast eldritch blast: ' + str(i.eldritch_blast_cast/repetition) + '\n'
            i.eldritch_blast_cast = 0
    return text_result

def full_statistical_recap(repetition, fighters):
    DM = fighters[0].DM
    DM.start_time = datetime.now()

    #generate a str that will be returned
    text_result = 'Simulation estimates:\n'

    #run simulation
    names, damage_statistic_sorted, winner, rounds_number, deaths = run_simulation(repetition, fighters)
    wins = 0
    defeats = 0
    for i in winner:
        if i == 0:
            wins += 1
        else:
            defeats += 1
    win_probability = wins/(wins + defeats)

    # run the most valuable player function with less repetitions
    DM.block_print()
    mvp_repetitions = int(repetition/10) +1
    if mvp_repetitions > 100:
        mvp_repetitions = 100
    player_name, win_probability_without_player, mvp = most_valuable_player(mvp_repetitions, fighters)
    DM.enable_print()

    text_result += '_____________________\n'
    text_result += 'Win Probability: ' + str(round(win_probability*100, 3)) + ' %\n'
    text_result += 'Fight Length: ' + str(round(np.mean(rounds_number),1)) + ' +/- ' + str(round(np.std(rounds_number),1)) + '\n'
    text_result += 'DEATHS: \n'

    # Calaculate death rates  (If they win, if they loose, they all die obviously)
    for i in fighters:
        fighter_has_died_counter = 0   #death counter
        for j in deaths:
            if i.name == j:   #if name is in deaths from simulation
                fighter_has_died_counter += 1
        if fighter_has_died_counter > 0:
            death_probability = fighter_has_died_counter/repetition
            text_result += str(i.name) + ' dies: ' + str(round(death_probability*100,2)) + ' % Chance\n'


    damage_player = [np.mean(damage_statistic_sorted[i]) for i in range(0, len(damage_statistic_sorted))]


    text_result += '\n'
    text_result += 'SPELLS CAST:\n'
    text_result = spell_cast_recap(repetition, fighters, text_result)
    text_result += '\n'
    if win_probability > 0.01:
        text_result += 'PLAYER PERFORMANCE: \n'

    #calculating the performance of the Players
        #Performance evaluated as the win probability without them as a Player
        performance_winrate = [(1 - i/win_probability) for i in win_probability_without_player]
        #Perfprmance as the part of Dmg done:
        performance_damage = []
        for i in range(0, len(damage_player)):
            if fighters[i].team == 0:
                performance_damage.append(damage_player[i])
        for i in range(0, len(performance_damage)):
            performance_damage[i] = performance_damage[i]/sum(performance_damage)

        for i in range(0,len(player_name)):
            text_result += str(player_name[i]) + ' : ' + str(int(100*(performance_winrate[i] + performance_damage[i])/2)) + '/100 \n'

    text_result += '\n'
    text_result += 'DAMAGE DONE: \n'
    for i in range(0,len(fighters)):
        text_result += fighters[i].name + ' : ' + str(int(damage_player[i])) + '\n'


    f = open('simulation_result.txt', 'w')
    f.write(text_result)
    return text_result

def teamhealth(fight, teamtag):
    healthlist = []
    for i in range(0, len(fight)):                  #sort team
        if fight[i].team == teamtag and fight[i].CHP > 0:
            healthlist.append(fight[i].CHP)
    return sum(healthlist)