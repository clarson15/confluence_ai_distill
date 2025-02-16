from dotenv import load_dotenv
from openai import OpenAI
from confluence_client import ConfluenceClient
import os
import sys
import json

def main():
    load_dotenv()
    if not os.path.exists('prompts/extract_classify.txt'):
        print("File 'prompts/extract_classify.txt' does not exist.")
        sys.exit(1)
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
    confluence_client = ConfluenceClient(confluence_url, confluence_api_key)
    openai_client = OpenAI()
    tools = [
        {
            "type": "function",
            "function": {
                "name": "label_text",
                "description": "Labels the text with the given label",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to label"
                        },
                        "label": {
                            "type": "string",
                            "description": "The label to apply to the text"
                        }
                    },
                    "required": ["text", "label"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    ]

    spaces = []
    inputSpace = "to-fill"
    while inputSpace:
        inputSpace = input("Enter space name (leave blank to continue): ")
        if inputSpace:
            spaces.append(inputSpace)
    print("Spaces:", spaces)
    
    pages = []
    for space in spaces:
        pages += confluence_client.get_pages_in_space(space)
    print("Pages:", len(pages))

    if not os.path.exists("output/confluence"):
        os.makedirs("output/confluence")
    for page in pages:
        data = confluence_client.get_page_content(page[1])
        filename = ''.join(ch for ch in page[0] if ch.isalnum())
        with open(f'output/confluence/{filename}.txt', 'w+') as file:
            file.write(data)
    return

    prompt = ''
    with open('prompts/extract_classify.txt', 'r') as file:
        prompt = file.read()

    data = {}
    try:
        for page in pages:
            print(f'Page: {page["title"]}')
            messages = [
                {
                    "role": "developer",
                    "content": prompt.replace('{labels}', ', '.join(list(data.keys())))
                },
                {
                    "role": "user",
                    "content": "Respond with 'Done' if you understand."
                },
                {
                    "role": "assistant",
                    "content": "Done"
                },
                {
                    "role": "user",
                    "content": f'Title: {page["title"]}\n\n{page["content"]}'
                }
            ]

            safetyCounter = 0
            
            while True:
                completion = openai_client.chat.completions.create(
                    model = "gpt-4o-mini",
                    tools = tools,
                    messages = messages
                )
                messages.append(completion.choices[0].message)
                if completion.choices[0].message.tool_calls:
                    for tool_call in completion.choices[0].message.tool_calls:
                        if tool_call.type == "function" and tool_call.function.name == "label_text":
                            args = json.loads(tool_call.function.arguments)
                            if "label" not in args or "text" not in args:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": "Missing label or text in arguments"
                                })
                                continue

                            if args["label"] not in data:
                                data[args["label"]] = []
                            data[args["label"]] += [args["text"]]
                            print(f'Labeled {args["text"]} as {args["label"]}')
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f'Labeled {args["text"]} as {args["label"]}'
                            })
                    continue

                if completion.choices[0].message.content.endswith("Done"):
                    break

                messages.append({
                    "role": "user",
                    "content": "Continue. End response with 'Done' when finished."
                })
                safetyCounter += 1
                if safetyCounter > 3:
                    print(f"Safety counter reached {safetyCounter} for page {page['title']}")
                if safetyCounter > 6:
                    print(f"Aborting page {page['title']}")
                    print(messages)
                    break
    except Exception as e:
        print(e)
    
    save_data(data)

def save_data(data):
    for label in data.keys():
        with open(f'output/{label}.txt', 'w+') as file:
            for item in data[label]:
                file.write(item + '\n')

if __name__ == "__main__":
    main()