echo "Running Python Scripts Necessary for Part II of Fire Attack Report" 

echo "Plotting General Results Plots"
Python.exe Fire_Attack_PDF_Plotter.py
echo "Building Data Dictionary"
Python.exe Build_Data_Dictionary.py
echo "Calculate FED Data"
Python.exe Build_FED_Data.py
echo "Calculating Repeatibility Data"
Python.exe Calculate_Repeatibility_Data.py
echo "Building Repeatability Radar Plots"
Python.exe Radar.py
echo "Plotting FED"
Python.exe Plot_FED.py
echo "Plotting Water Flow Charts"
Python.exe Water_Flow_Plotter.py
echo "Plotting Experiment Analysis Plots"
Python.exe Experiment_Analysis_Plotter.py
echo "Plotting Knock Back Analysis Plots"
Python.exe Knock_Back_Time_Plotter.py
echo "Plotting TIC Plots"
Python.exe TIC_Plot.py
echo "Plotting Tactical Considerations Plots"
Python.exe Tactical_Considerations_Plotter.py