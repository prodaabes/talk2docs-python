import argparse

chatId = ''
fileName = ''

content = ''
modified_content = ''

def main():

    global content, modified_content

    # Read the content of the knowledge.txt
    with open('chats/' + chatId + '/knowledge.txt', 'r') as f:
        content = f.read()

    # Find the start and end indices of the text to be removed
    start_marker = '### start of ' + fileName + ' ###'
    end_marker = '### end of ' + fileName + ' ###'
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)

    # Check if both markers are present in the content
    if start_index != -1 and end_index != -1:
        # Remove the text between the markers
        modified_content = content[:start_index] + content[end_index + len(end_marker):]
    else:
        # If markers are not found, keep the original content
        modified_content = content

    # Write the modified content to the knowledge.txt
    with open('chats/' + chatId + '/knowledge.txt', 'w') as f:
        f.seek(0)
        f.truncate()
        f.write(modified_content)
        f.close()


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