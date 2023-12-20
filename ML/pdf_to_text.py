import cv2
import os
import pytesseract
from PIL import Image
import pdf2image
import shutil

def pdf_to_text():
    #### If you dont have tesseract install it from : 
    # Download tesseract exe from https://github.com/UB-Mannheim/tesseract/wiki.
    # Install this exe in Any folder of your choice
    # Run pip install pytesseract
    ####################################################################
    pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR/tesseract.exe' ## just give path till tesseract.exe that you have installed in above step
    pdf_file_path = r'ML/ML - InvoicesPDF/Training_PDFs/'
    trained_pdf_file_path = r'ML/ML - InvoicesPDF/Trained PDFs/'
    image_path = r'ML/Image/'
    txt_file_path = r'ML/Train_txt/'
    for folder in os.listdir(pdf_file_path) :
        print(folder)
        if not os.path.exists(trained_pdf_file_path+folder) :
            os.makedirs(trained_pdf_file_path+folder)
        for file in os.listdir(pdf_file_path+folder):
            # print(file)
            if '.ini' not in file :           
                if not os.path.exists(txt_file_path+folder+'/'+file.split('.pdf')[0]+'.txt'):
                    print(file)
                    image = pdf2image.convert_from_path(pdf_file_path+folder+'/'+file,poppler_path = r'Backend/poppler-0.68.0/bin',transparent=True,grayscale=True)[0]
                    image.save(image_path+file.split('.pdf')[0]+'.png')
                    images =cv2.imread(image_path+file.split('.pdf')[0]+'.png')
                    cv2.blur(images, (5,5))      

                    text = pytesseract.image_to_string(Image.open(image_path+file.split('.pdf')[0]+'.png'))
                    # added by developer testing
                    text = text.replace("'","").replace('"',"").replace("None","").replace("#","").replace('\n',' ').strip()
                    text = text.encode('ascii', errors='ignore')
                    text = text.decode('ascii', errors='ignore')
                    print(text)
                    # finish by developer testing
                    os.remove(image_path+file.split('.pdf')[0]+'.png')
                    if not os.path.exists(txt_file_path+folder):
                        os.mkdir(txt_file_path+folder)
                    with open (txt_file_path+folder+'/'+file.split('.pdf')[0]+'.txt',mode='w') as txt_file_writer:
                        txt_file_writer.writelines(text)
                    txt_file_writer.close()
                shutil.move(pdf_file_path+folder+'/'+file,trained_pdf_file_path+folder+'/'+file) 

if '__main__' == __name__ :
    pdf_to_text()