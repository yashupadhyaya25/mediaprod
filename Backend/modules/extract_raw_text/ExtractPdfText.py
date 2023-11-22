import cv2
import os
import pytesseract
from PIL import Image
import pdf2image
from configparser import ConfigParser

#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####

configur = ConfigParser()
config_file_obj = configur.read('config.ini')

pdf_file_path = configur.get(enivronment,'user_upload_pdf')
image_path = configur.get(enivronment,'user_upload_pdf_image')
tesseract_cmd_path = configur.get(enivronment,'tesseract_cmd')
poppler_path = configur.get(enivronment,'poppler_path')

class ExtractPdfText() :
    def pdf_to_text(file):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

        image = pdf2image.convert_from_path(pdf_file_path+file,poppler_path = poppler_path,transparent=True,grayscale=True)[0]
        image.save(image_path+file.split('.pdf')[0]+'.png')
        images =cv2.imread(image_path+file.split('.pdf')[0]+'.png')
        cv2.blur(images, (5,5))      

        text = pytesseract.image_to_string(Image.open(image_path+file.split('.pdf')[0]+'.png'))
        text = text.replace("'","").replace('"',"").replace("None","").replace("#","").replace('\n',' ').strip()
        text = text.encode('ascii', errors='ignore')
        text = text.decode('ascii', errors='ignore')
        return text
