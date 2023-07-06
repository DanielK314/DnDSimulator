# The DnD Simulator

This is a private project of mine. The Simulator can help to test end balance DnD 5E encounter or be used in a session to keep track of HP, initiative and concentration. Just add your characters and run the simulation or go into to DM mode.

I am still working to improve the simulation and to add more abilities to the system. If you have any ideas how to improve this or you observed any weird behaviours in the simulation, please let me know. Thanks and have fun with your DnD adventure.

# Quick Install
The easiest way to install is to go to the releases and download the DNDSimulator.zip for either Windows10 or MacOS. Unpack the .zip and click on the StartSimulator.exe. After a moment the interface should pop up. Have fun.

https://github.com/DanielK314/DnDSimulator/releases/tag/v1.2.1

# Using Python to run

The project is done with python only, so download or clone the repository, install the required modules and then run StartSimulator.py with python in your console.

If you want more detailed instructions, there are step by step instructions down below.

# How to use?

## The Main Page
<img src="/Documentation/MainPage.png" width=80% height=80%>

This is the starting Page. Here are all characters and monsters listed that are currently in the Entities folder. Click on any of them to see their stats and to edit them. With the plus button you can add them to the fight. **Add heros and monsters** and start the simulation to see how well the encounter is balanced. The program will simulate the fight multiple times and do a little statistics on the results. Change how many repetitions will be done as you want, but keep in mind, that for large fights or many repetitions the simulation might take a while.

Using the **'Enable Printing'** button you can let the program print out every move of the fight into the console. This might impact the performance of the program. I especially had this problem on windows, so maybe just print 10 fights or so. 

<img src="/Documentation/Printing.png" width=50% height=50%>

## Simulation Results
<img src="/Documentation/Result1.png" width=30% height=30%>
<img src="/Documentation/Result2.png" width=30% height=30%>

This is the statistical summary that is given after the simulation. It gives an estimate for how long the fight lasts, meaning until one side has no concious player left. It gives the **win probability** for the heros and if any character might die. It also gives a recap what **spells** were cast and who did what **damage on average**. The **performance review** factors in the done dmg, heal and how the win probability changes if that character is not fighting. 

For balancing encounters keep in mind, that a loose for the heros means, that the monsters have reduced all of them to 0 HP, effectively resulting in a total party kill. So therefore a 80% win chance means that in 1 out of 5 cases your campaign has come to a sudden end. I usually aim for the upper 90%-ish win chances and 4-6 rounds of combat. The dmg done by the monsters is also a good indicator.

## The DM Page
<img src="/Documentation/DMPage.png" width=80% height=80%>

The DM Page is a nice little tool I implemented to make it easier for the Dungeon Master to keep track on whats happening. I use it in my own games and think it works well. You can initiate the fight as usual and go into DM mode. All the characters are listed and you can visit their **stat block**. The tool keeps track of the **HP** and also considers and calculate DMG type **resistances/vulnerabilities**. At the start of the fight type in the initiative and with the click of a button the **Init order** is sorted. I find this very useful. You can also add new characters to the fight later without loosing the data. With the C button you can keep track of **concentration** and if you apply dmg to a concentrated character, a window will remind you of the Con save and what the DC will be. If you have other ideas what the DM page could use, let me know.

<img src="/Documentation/ConSave.png" width=60% height=60%>

## The Character Page
<img src="/Documentation/Character.png" width=60% height=60%>

This is a overview of all the stats and abilities that are currently supported by system. You can edit and create character and monster here. I will give a more detailed information on what each does below. Use the **Archive** to load default character and monster or create your own. With the Hero or Villain entry you can decide in which team they fight. Beware, if you change the name of a character and save, a new character with that name will be created and the old remains. This can be useful to quickly duplicate monsters.

# Character Stats and Abilities

## Basic Stats
<img src="/Documentation/BasicStats.png" width=30% height=30%>

Most of this explains itself. Simply insert the AC, HP, proficiency and level of your character. The Hero and Villain can be set to 0 for hero and 1 for villain. Character type is relevant for undead and the clecrics destroy undead. You can then add the stats and if they have save prof.

## Attacks
You can add the damage, the to hit and the number of attacks the character does with one action. The damage is supposed to be the mean value that attack does. The dmg type is assumed to be the type selectable in the DMG section. If you add a offhand damage that is not 0, the character is assumed to have a offhand attack for the bonus action

Range Attacks:
If you enable this the charakter has a range attack and will use the range attack for all normal attacks. Keep this in mind for abilities like smite or great weapon master


## Spells
<img src="/Documentation/Spell1.png" width=40% height=40%>

Here you just enter what **spell Mod**, **spell DC** and **spell slots** the player has. The system keeps track of all this and will automatically use and choose the spells in combat. If you, for some reason dont want a character to cast or if a character usually already has some spell slots used at the start of an encounter, just adjust here.

<img src="/Documentation/Spell2.png" width=40% height=40%>

In the **Spell Book** page you can choose from the spells that are currently implemented. More will hopefully come. I might add how the spells are used and chosen to this documentation, or you can always try to decipher my code :D.

## Movement
<img src="/Documentation/Movement.png" width=50% height=50%>

Interesting is the **Number of Attacks** which just means, that if a character chooses to use the action for an attack, they will do this many with the same dmg. The system also supports **off hand attacks** with a bonus action. Also keep in mind, that the dmg of all attacks and spells used is the expectation value of the dice roll. Okay, so the positioning is a little bit more complicated. **Short version**: If you are a spell caster with low AC, go in the **Back Line**. If you can tank a bit more and want to attack melee, go **Middle**. **Front** is for the heavy hitters with high AC, like Barbarian or Paladin.

**Long Version**: I wanted to include movement, speed and positioning into the simulation, but I felt like an actual system for position, maps and movement over 5ft squares was over the top. Additionally I assumed that most of the movement would average out over many fights anyway and no simulation will capture the actual maps an movement of a real DnD session. So I decided to do a different approach. The line system is supposed to mimic the basic play and positioning style of the characters and implement speed and opportunity attacks without a grid system.

Front player can attack front and middle. They will focus on the front and will draw most of the attacks. If they want to attack players in the back they will need to dash and provoke attacks of opportunity.

Middle player can attack the front. If they want to attack middle they need to dash and provoke attack of opportunity. They may only reach into the back if their speed suffices. (Same for back liners)

Back players will attack with range attacks (which can always attack any line regardless where the player is). They will usually not be attacked by melee as long as the front and middle stand. Only if a creature in the front decides to dash or if an range attack comes in.

Im also thinking about implementing a line for flying player, but we will see. Much of this is coded in the 'will_provoke_Attack' and 'need_dash' functions and the attack decisions in combat are done by the 'do_your_turn' and 'choose_att_target' functions, if you want to check how it is done in detail.

## Damage Type

Not so much to say here. The dmg type system of DnD is fully implemented. Any creature has resistances, vulnerabilities and immunities and any dmg comes with a dmg type. The dmg type you can choose here relates to the dmg done by a simple attack. Currently only one dmg type can be assigned to a singe attack or spell, so if a paladin uses smite on its attack all the dmg will be 'radiant'.

<img src="/Documentation/DMG.png" width=40% height=40%>

## Other Abilities
<img src="/Documentation/Other1.png" width=40% height=40%>

Now it gets really interesting. In the following I will discuss the different special abilities and how they are implemented in the code (for me and maybe you to better understand the code). These are class features but also monster abilities:

**Action Surge** Set how many Action Surges a Character has. A Character with action surge will use it if HP lower then 60%

**Improved Critical** Critical Hit at 19

**Second Wind** A Character will use this if HP lower then 30%

**Sneak Attack Dmg** If this is not zero it will just be added to the first attack hit of every turn, implemented directly in the attack function. I realize that not every attack is a sneak attack, but I figured a rogue will get mostly sneak attack.

**Lay on Hands Pool** Is a feature of the paladin and will be used to heal others and the player if needed. It is implemented via the 'use_lay_on_hands' function of the Entity class. This is also useful if monster has self healing powers. I used it for the Vampire for example as I have not implemented another heal for monsters to use.

**Sorcery Points** Is just how many sorcery points a player has. Keep in mind, that the meta magic options are in the other abilities and must be activated as well.

**UncannyDodge** This feature works automatically and is used in the 'changeCHP' function. On the first time a player takes dmg, it will use it to half the dmg. 

**CunningAction** Player can use dash as BA or avoid opportunity attack. This is used in combination with my movement system. Much of this is coded in the 'will_provoke_Attack' and 'need_dash' functions.

**WailsFromTheGrave** Subclass for rogues and works automatically in combination with sneak attacks

**Rage** Is used via thw 'rage' function and will be activated directly when a player attacks and can rage, it will. 

**RecklessAttack** Is used via the 'rackless_attack' function and will be used for every attack, if activated.

**Frenzy** If player goes in rage and knows franzy, this will be activated in the 'rage' function. If a player attacks it will do an additional franzy attack. 

**Totems** This is a Barbarian feature

**Smite** Smite uses spell slots. If a player knows smite and hits a target, the player.AI.want_to_cast_smite is called and the smite dmg is added in the 'attack' function. The player will use its highest slot from 1-4.

**Aura of Protection** Some of the allies are randomly choosen every round. They will revieve the bonus.

**Lay on hands** Set how much Lay on hands a character has, if this is not 0 a Character will use it to heal themself or allies

**Meta Magic** There are 3 options to use the meta magic of sorcerers. Set how much sorcery points a character has. If it is more then 0 and a character has meta magic options to cast a spell, they might use it.

**WildShape** A druid can go into wild shape. It will drop it, if the an ally needs heal desperately. Currently a few Options are available for the character to select from randomly, according to the players level respectfully. These are: Wolf,Brown Bear, Crocodile,Ape,Giant Eagle,Giant Boar,Polar Bear,Boar

**CombatWildShape** Allows the player to go into wild shape with a BA and heal using spell slots.

**Inspiration** If this is activated a player might use the BA to inspire random allies. Choose a inspiration die below

**Cutting Words** Might use a inspiration die to cutting words an attack

**Primal Companion** The Character will summon one companion at the start of the fight, according to the ranger subclass rules. If it makes sense the Ranger will use its bonus action to make the companion attack, otherwise the companion will use the dodge action.

**Aganizing Blast** Warlock invocation

**Turn Undead** Choose if a character can Turn Undead, how often and at what CR (level) they destroy undead

**Great Wapon Master** The can take a -5 to hit for +10 dmg on melee attacks. Make sure, that the character is not set on ranged attacks, or this feat is useless. The 'AI' calculates the expections value of the attack to hit with and without Great Weapon Master according to the characters to hit mod and the targets AC. The character will use the option that will result in the best damage average, also taking advantage into consideration

**Polearm Master** If player try to attack this character melee, they trigger an attack of opportunity

**Monster Abilities**
<img src="/Documentation/Monster.png" width=40% height=40%>

**DragonsBreath** This ability is charged at the start of a turn with a 5 or 6 on a d6 roll. If charged the monster will breath fire on multiple random targets via the 'use_drongs_breath' Entity function. Its dmg scales with the Con mod und level of the player using it (Save DC = 12 + int((Level-10)/3) , DMG = 20 + int(level*3.1). This corresponds pretty accurately to red dragons (young to ancient) but works in principle for all characters.

**SpiderWeb** This ability is charged at the start of a turn with a 5 or 6 on a d6 roll. If charged the monster will shoot a spider web to restrain a target. The DC scales with Dex mod (9 + Dex). Works in principle for all characters.

**Heal at start of turn** As long as this monster is conscious, it heals the amount at the start of the turn

**Legendary Resistances** The monster can choose to succeed on a failed save. It will use the feature if it can.

**Monster AEO** This feature allows you to cosumize a specific AEO effect. Choose the dmg type, the dmg amount, how often it recharged (propability at start of turn) and the save DC/Type. The Area correlates to how many characters are hit, for example, fireball, 20ft radius -> pi*20^2 = 1250ft^2. Remember to also check the button to activate this ability.

## Strategy
<img src="/Documentation/Strategy.png" width=40% height=40%>

You can use the Strategy Setting to adjust how strategic the character behaves. This mainly affects the way a character chooses targets for attacks and spells. A player character should have a Strategy Level of 5, maybe 6 if they are more strategic. Use higher levels for evil necromancers or stuff like that, because a higher level results in focusing attacks and killing unconscious player if they can. Lower level are good for beasts, because then the attacks get more random. At strategy level 1-2 they basically attack a random enemy. If you do not want to deal with this, just let it set on 5, it is a fine setting for any character.

# Spellcasting

The following spells are currently implemented into the system, but more shall follow. In the Init of the entity class a dict with all spells (SpellBook) is created. The entries of the SpellBook are objects of the spell class. Every spell is an object of that class with a name, spell_level, if it is a Action or Bonus Action spell and so on. It then gets a 'cast' function depending on which spell it is. These then usually call the 'attack' function or the 'change_CHP' function for the spell effects. For a player to cast the spell use self.SpellBook.['Spellname'].cast()

FireBolt

EldritchBlast

Entangle 

BurningHands

CureWounds

HealingWord

MagicMissile

Hex

Guiding Bolt

Shield

False Life

AganazzarsSorcher

ScorchingRay

Shatter

Spiritual Weapon

Fireball

Haste

Conjure Animals 

When implementing a new Spell, it must be written in the spell class and list of all spells in the entity class

# How to Install?

The hole thing is written in python, so all you really need is python installed and some modules I used.

## Install Python

First install python, if you have not yet. To install python is fairly simple, just go to www.python.org and follow the instructions for your operating system.

## Download

If you worked with git before, you can just clone this repository. But you can also klick on the 'code' button on the top right and download it as a zip file and then unpack it where you want.

## Install the modules

You might need to install some python modules I used for this project. To do so, just use pip. It most likely is already installed. If not, you might want to get it. Pip can be used to install the modules required. To do so, open a terminal and navigate to the folder of this project via:

```
cd ThePathToTheProject
```

Now use pip to install the modules listed in the requirements.txt:

```
pip -r requirements.txt
```

Now you can run the start program with python:

```
python StartSimulator.py
```

If you get a message that a module is missing, install it via:

```
pip install NameOfTheModule
```

I hope this helps to get it started, if there is still a problem, don't hesitate to send me a message.

# Using the System yourself

If you want to use the system via the GUI you can just use StartSimulator.py it will start the GUI and that does the rest.

If you want to work with the system yourself, you can use it without the GUI. The Encounter_Simulator.py holds all the function to do Simulations yourself. The 'run_simulation' function takes a list of fighters and a repetition number and returns the simulation results. 

To initiate the characters import the Entity_class.py and initiate the character via the entity class. Just use: Character = entity('Name', 0, DM) where the name is the name of the json file. For an example look at playground.py. Have fun.