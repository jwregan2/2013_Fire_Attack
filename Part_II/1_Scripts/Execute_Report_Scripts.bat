echo "Running Python Scripts Necessary for Part II of Fire Attack Report" 

echo "Plotting General Results Plots"
Python.exe Fire_Attack_PDF_Plotter.py
echo "Building Data Diectionary"
Python.exe Build_Data_Dictionary.py
echo "Calculate FED Data"
Python.exe Build_FED_Data.py
echo "Calculating Repeatibility Data"
Python.exe Calculate_Repeatibility_Data.py
echo "Plotting FED"
Python.exe Plot_FED.py
echo "Plotting Water Flow Charts"
Python.exe Water_Flow_Plotter.py
echo "Plotting Experiment Analysis Plots"
Python.exe Experiment_Analysis_Plotter.py
