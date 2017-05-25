#!/usr/bin/env bash
echo "Running Python Scripts Necessary for Part II of Fire Attack Report" &&
cd "$(dirname "$0")"
echo "Plotting General Results Plots"
python Fire_Attack_PDF_Plotter.py
echo "Building Data Diectionary"
python Build_Data_Dictionary.py
echo "Calculating Repeatibility Data"
python Calculate_Repeatibility_Data.py
echo "Plotting FED"
python Plot_FED.py
echo "Plotting Water Flow Charts"
python Water_Flow_Plotter.py
echo "Plotting Tactic Results Scripts"
python Tactic_Results_Plot.py
