import time
import argparse
import pytesseract
import asyncio
import websockets
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from colorama import Fore
from os import listdir
from os.path import isfile, join
from PIL import Image

conversation = None
chat_history = None


def get_pdf_text(chatId):
    filesPath = 'chats/' + chatId
    files = [f for f in listdir(filesPath) if isfile(join(filesPath, f))]

    raw_text = ''

    for i, fileName in enumerate(files):
        if fileName.endswith('.pdf'):
            # provide the path of pdf file/files.
            pdfreader = PdfReader(filesPath + '/' + fileName)

            # read text from pdf
            for j, page in enumerate(pdfreader.pages):
                content = page.extract_text()
                if content:
                    raw_text += content
        elif fileName.endswith('.txt'):
            # do nothing
            print()
        else:
            # Open the image file
            image = Image.open(filesPath + '/' + fileName)

            # Perform OCR using PyTesseract
            raw_text += pytesseract.image_to_string(image)
    
    return raw_text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 800,
        chunk_overlap = 200,
        length_function = len,
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = conversation({'question': user_question})
    global chat_history
    chat_history = response['chat_history']

    # for i, message in enumerate(chat_history):
    #     if i % 2 == 0:
    #         print(Fore.RED + "Me: " + message.content)
    #     else:
    #         print(Fore.CYAN + "Bot: " + message.content)
    return chat_history[len(chat_history) - 1].content

async def listen(websocket):
    question = await websocket.recv()
    print(Fore.RED + f'Question: {question}')

    answer = handle_userinput(question)
    await websocket.send(answer)
    print(Fore.CYAN + f'Answer: {answer}')


async def main(chatId):
    load_dotenv()

    # get pdf text
    raw_text = get_pdf_text(chatId)

    # get the text chunks
    text_chunks = get_text_chunks(raw_text)

    # create vector store
    vectorstore = get_vectorstore(text_chunks)

    # create conversation chain
    global conversation
    conversation = get_conversation_chain(vectorstore)

    async with websockets.serve(listen, "192.168.0.130", 8765) as server:
        #print(server.sockets[0].getsockname()[1])
        await asyncio.Future() # run forever

def run(chatId = None):
    if chatId == None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--chatId")
        args = parser.parse_args()

        chatId = args.chatId

    asyncio.run(main(chatId))

if __name__ == '__main__':
    run()
