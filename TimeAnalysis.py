import cProfile
from run_time_benchmark import *

cProfile.run('run_time_benchmark()', 'profile_results')
#This function runs the full stat recap with a profile for time management
#It takes the simulation parameters currently in the json file 

import pstats
file = open('formatted_profile.txt', 'w')
profile = pstats.Stats('profile_results', stream=file)
profile.sort_stats('cumulative') # Sorts the result according to the supplied criteria
profile.print_stats(200) # Prints the first 15 lines of the sorted report
file.close()