
import os as os
import pandas as pd 

n = 'Experiment_1.csv'

Experiment_Num = n[:-4]

Experiment_Num = Experiment_Num[11:]

Translation = {'1':'12'}

# Translation = pd.read_csv('Translation.csv') 

# Tramslation = Translation.set_index('Intitial')

New_Number = Translation[Experiment_Num]

os.rename('Experiment_'+Experiment_Num +'.csv', 'Experiment_' + New_Number + '.csv')





