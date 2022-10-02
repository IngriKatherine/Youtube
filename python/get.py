### Program to get Youtube API data
### @ IQ
#====================================================================================================================#
# Preliminaries
#====================================================================================================================#
#-------------------------------------------------------------------------------------------------------------------#
# Libraries
#-------------------------------------------------------------------------------------------------------------------#
from timeit import default_timer as timer
import pandas as pd
import os
from pathlib import Path

#====================================================================================================================#
# Path
#====================================================================================================================#

__file__ = 'get.py'
codefile_directory=Path(__file__).absolute().parent
print(codefile_directory)
myroot=codefile_directory.parent
print(myroot)

output_folder=str(myroot)+"\\"
logs_folder = str(myroot)+"\\"+'master_programs\\comtrade\\logs'
# Check whether the logs directory path exists or not
isExist = os.path.exists(logs_folder)
if not isExist:
  # Create directory because it does not exist 
  os.makedirs(logs_folder)
  print("The logs directory is created!")

data_folder=str(myroot)+"\\"+'Master_Dataset\\Tariffs_Trade\\data\\comtrade'
# Check whether the data directory path exists or not
isExist = os.path.exists(data_folder)
if not isExist:
  # Create directory because it does not exist 
  os.makedirs(data_folder)
  print("The logs directory is created!")


#====================================================================================================================#
# Parameters
#====================================================================================================================#

apikey = "AIzaSyDt29H6_4ZRFulkdEbeb-FC5tO3Hoh3zHQ"

#====================================================================================================================#
# Functions
#====================================================================================================================#

#--------------------------------------------------------------------------------------------------------------------#
# PART A. Functions that download the Comtrade Bulk data 
#--------------------------------------------------------------------------------------------------------------------#