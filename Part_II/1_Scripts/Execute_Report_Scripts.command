#!/usr/bin/env bash
echo "Running Python Scripts Necessary for Part II of Fire Attack Report" &&
cd "$(dirname "$0")"
echo "Plotting General Results Plots"
python Fire_Attack_PDF_Plotter.py
echo "Building Data Diectionary"
python Build_Data_Dictionary.py
echo "Build FED Data"
python Build_FED_Data.py
echo "Calculating Repeatibility Data"
python Calculate_Repeatibility_Data.py
echo "Building Repeatability Radar Plots"
python Radar.py
echo "Plotting FED"
python Plot_FED.py
echo "Plotting Water Flow Charts"
python Water_Flow_Plotter.py
echo "Plotting Experiment Analysis Plots"
python Experiment_Analysis_Plotter.py
echo "Plotting Knock Back Analysis Plots"
python Knock_Back_Time_Plotter.py
echo "Plotting Tactical Considerations Plots"
python Tactical_Considerations_Plotter.py