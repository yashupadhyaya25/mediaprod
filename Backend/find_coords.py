from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

fp = open('InvoicesPDF/Reynaud CHECK/Facture-1074949677-0.pdf', 'rb')
rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
pages = PDFPage.get_pages(fp)

for page in pages:
    print('Processing next page...')
    interpreter.process_page(page)
    layout = device.get_result()
    for lobj in layout:
        if isinstance(lobj, LTTextBox):
            
            x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
            print('----------')
            print(lobj.bbox)
            print('At %r is text: %s' % ((x, y), text))