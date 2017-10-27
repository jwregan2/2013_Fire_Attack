from PIL import Image
import os


# for tc in os.listdir('../5_Report/0_Images/Instrumentation/'):

# 	if tc == '.DS_Store':
# 		continue

for pic in os.listdir('../5_Report/0_Images/Instrumentation/Gas_Analyzer/'):
	print (pic)

	if pic == '.DS_Store':
		continue
	
	try:
		im = Image.open('../5_Report/0_Images/Instrumentation/Gas_Analyzer/' + pic)
		width, height = im.size

		im = im.resize((int(width*0.5), int(height*0.5)))

		if not os.path.exists('../5_Report/0_Images/Instrumentation/Small/Gas_Analyzer/'):
			os.makedirs('../5_Report/0_Images/Instrumentation/Small/Gas_Analyzer/')

		im.save('../5_Report/0_Images/Instrumentation/Small/Gas_Analyzer/' + pic, dpi=(150,150))

	except IOError:
		continue


