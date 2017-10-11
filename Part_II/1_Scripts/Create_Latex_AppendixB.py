import fnmatch
import os
import re

report_location = '../5_Report/'
charts_location = '../0_Images/Script_Figures/Results/'

file = open(report_location + 'Appendix_B.tex',"w")

firstline = '\t\\begin{figure}[H]\n'
secondline	= '\t\t\\centering\n'
lastline = '\t\end{figure}\n \n'

experiments = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,26]

for exp in experiments:

	filenames = os.listdir(charts_location + 'Experiment_' + str(exp) + '_Data')

	exp_charts = charts_location + 'Experiment_' + str(exp) + '_Data/'

	#file.write('\t\\Begin{center}\n' + '\t\t\\large\n' + '\t\t\\textbf{Experiment ' + str(exp)+' Data}\n' + '\t\\end{center}\n\n')
	file.write('\\clearpage')
	file.write('\t\t\\large\n' + '\\section{Experiment ' + str(exp)+' Data} \\label{App:Exp'+str(exp) +'Results} \n' + '\n')

	x = 0

	for name in filenames:
		if name.replace(' ',' ')[len(name)-4:] == '.pdf':
			x = x + 1
			file.write(firstline)
			file.write(secondline)
			figurename = '\t\t\includegraphics[height=3.7in]{' + exp_charts + name + '}\n'
			file.write(figurename)
			figureTitle = re.sub(r"(?<=\w)([1-9])", r" \1", re.sub(r"(?<=\w)([A-Z])", r" \1", name.replace('_',' ')[:-4]))
			figurecaption = '\t\t\caption[]{Experiment '+ str(exp) +' - ' + figureTitle + '}'
			file.write(figurecaption +'\n')
			file.write(lastline)
			if x%2 is 0:
				file.write('\t\\clearpage\n')
			file.write('\n')
		X = 0

file.close