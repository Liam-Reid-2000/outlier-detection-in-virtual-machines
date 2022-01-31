#Import the required modules
import numpy as np
import pandas as pd
 
data = pd.read_csv('resources/speed_7578.csv')
 
#Plotting Boxplot of Age column
boxplot = data.boxplot(column=['Age'])