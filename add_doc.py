import argparse
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader

chatId = ''
fileName = ''

def get_pdf_text():
    filePath = 'chats/' + chatId

    raw_text = ''

    if fileName.endswith('.pdf'):
        # provide the path of pdf file/files.
        pdfreader = PdfReader(filePath + '/' + fileName)

        # read text from pdf
        for j, page in enumerate(pdfreader.pages):
            content = page.extract_text()
            if content:
                raw_text += content
    else:
        # Open the image file
        image = Image.open(filePath + '/' + fileName)

        # Perform OCR using PyTesseract
        raw_text += pytesseract.image_to_string(image)
    
    return raw_text

def main():
    # get pdf text
    raw_text = get_pdf_text()

    # write the text in the knowledge.txt file
    with open('chats/' + chatId + '/knowledge.txt', 'w', encoding='utf-8') as f:
        f.write('### start of ' + fileName + ' ###\n')
        f.write(raw_text + '\n')
        f.write('### end of ' + fileName + ' ###\n')

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chatId")
    parser.add_argument("--file")
    args = parser.parse_args()

    global chatId, fileName
    chatId = args.chatId
    fileName = args.file

    main()

if __name__ == '__main__':
    run()