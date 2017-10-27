from PIL import Image
import pytesseract
 
image_file = '../2_Data/HRR_Mass_Loss/Test_Image.png'
im = Image.open(image_file)


text = pytesseract.image_to_string(im)

print("=====output=======\n")
print(text)

