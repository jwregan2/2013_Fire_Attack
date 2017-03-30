import numpy as np
import pandas as pd
import scipy

O2per = 14.4
CO2per = 14.1
COppm = 11105.3
time_step = 2

CO2_corr = np.exp(CO2per/5)

FED = (3.317e-5*(COppm**1.036)*(25*CO2_corr)*time_step)/30

t_io2 = np.exp(8.13-0.54*(20.9-O2per))
t_ico2 = np.exp(6.1623-0.5189*CO2per)

FED_O2 = ((20.95-O2per)*time_step/((20.95-O2per)*t_io2))
FED_CO2 = ((CO2per*time_step)/(CO2per*t_ico2))

# CO2_corr = np.zeros(len(CO2per))

CO2_corr = np.exp(CO2per/5)

# CO2per_test = CO2per.tolist()

FED = FED * CO2_corr +FED_O2

print ((3.137e-5 * COppm**1.036 * 25 * 2)/30)

print(np.exp(3))
print(CO2_corr)
print (FED)

print (FED_CO2)