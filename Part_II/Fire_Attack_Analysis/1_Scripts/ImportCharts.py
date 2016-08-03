import fnmatch
import os
import re

file = open("TFRanchAppendixFigures.tex","w")

firstline = '\t\\begin{figure}[h!]\n'
secondline	= '\t\t\\centering\n'
lastline = '\t\end{figure}\n \n'

file.write('\\documentclass{article}\n')
file.write('\\usepackage{placeins}\n')
file.write('\\usepackage{graphicx}\n\n')
file.write('\\usepackage[toc,page]{appendix}\n')
file.write('\\usepackage{chngcntr} \n')
file.write('\\begin{document}\n')
file.write('\n\\tableofcontents\n\n')

file.write('\\begin{appendices}\n\n')
file.write('\\counterwithin{figure}{section}\n\n')
file.write('\\section{Experimental Results}\n')

for exp in range(1,3):

	filenames = os.listdir('../0_Images/Results/PDF/Training_Fire_' + str(exp) + '_Data')

	#file.write('\t\\Begin{center}\n' + '\t\t\\large\n' + '\t\t\\textbf{Experiment ' + str(exp)+' Data}\n' + '\t\\end{center}\n\n')
	file.write('\\clearpage')
	file.write('\t\t\\large\n' + '\\subsection{Experiment ' + str(exp)+' Data} \\label{App:Exp'+str(exp) +'Results} \n' + '\n')

	x = 0

	for name in filenames:
		if name.replace(' ',' ')[len(name)-4:] == '.pdf':
			x = x + 1
			file.write(firstline)
			file.write(secondline)
			figurename = '\t\t\includegraphics[height=3.05in]{../0_Images/Results/PDF/Training_Fire_'+ str(exp) + '_Data/' + name + '}\n'
			file.write(figurename)
			figureTitle = re.sub(r"(?<=\w)([1-9])", r" \1", re.sub(r"(?<=\w)([A-Z])", r" \1", name.replace('_',' ')[:-4]))
			figurecaption = '\t\t\caption{Experiment '+ str(exp) +' - ' + figureTitle + '}'
			file.write(figurecaption +'\n')
			file.write(lastline)
			if x%2 is 0:
				file.write('\t\\clearpage\n')
			file.write('\n')
			print name
		X = 0

	file.write('\t\t\\clearpage\n')

file.write('\\end{appendices}')
file.write('\\end{document}\n')
file.close