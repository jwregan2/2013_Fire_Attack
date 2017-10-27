from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import cv2
import os
import numpy as np

image_file = '../2_Data/HRR_Mass_Loss/Test_Image.png'

im = Image.open(image_file)
im = im.filter(ImageFilter.MedianFilter())
im.save(image_file[:-14] + 'New_Filter.png')

enhancer = ImageEnhance.Contrast(im)

im = enhancer.enhance(7)
# im.save(image_file[:-14] + 'New_Enhance.png')

# im = im.convert('1')
# im.save(image_file[:-14] + 'New_Convert.png')


# im.save(image_file[:-14] + 'New_Test.png')
# text = pytesseract.image_to_string(im)
# print ("text={}".format(text))


# # im = Image.open(image_file)
im = cv2.imread(image_file[:-14] + 'New_Filter.png')

im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# # (thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

thresh = 205
im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]

# im_bw = cv2.GaussianBlur(im_bw, (5,5), 0)

# # gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# # kernel = np.ones((1,1), np.uint8)

# # img = cv2.dilate(im, kernel, iterations=10)
# # img = cv2.erode(img, kernel, iterations=10)

cv2.imwrite(image_file[:-14] + 'New_Image.png', im_bw)

# # print (image_file[:-16] + 'New_Image.png')

img_new = Image.open(image_file[:-14] + 'New_Image.png')
enhancer = ImageEnhance.Contrast(img_new)

img_new = enhancer.enhance(111)
cv2.imwrite(image_file[:-14] + 'New_Image.png', im_bw)

# # os.remove(image_file[:-16] + 'New_Image.png')

# text = pytesseract.image_to_string(img_new, config='--psm 10 --eom 3 -c tessedit_char_whitelist=0123456789')
# text = pytesseract.image_to_string(img_new, config='outputbase digits')
# text = pytesseract.image_to_string(img_new, config='--psm 13')
# text = pytesseract.image_to_string(img_new, boxes=True)
# info = img_new.tobytes()

text = pytesseract.image_to_string(img_new, config='--psm 10')




print("=====output=======\n")
print(text)


