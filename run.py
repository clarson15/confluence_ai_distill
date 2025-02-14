import os
import http.client
import json
from dotenv import load_dotenv
from openai import OpenAI
import os
import sys

def main():
    load_dotenv()
    if not os.path.exists('prompts/extract_classify.txt'):
        print("File 'prompts/extract_classify.txt' does not exist.")
        sys.exit(1)
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
    client = OpenAI()
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
    
    print("CONFLUENCE_URL:", confluence_url)
    print("CONFLUENCE_API_KEY:", confluence_api_key)

    spaces = []
    inputSpace = "to-fill"
    while inputSpace:
        inputSpace = input("Enter space name (leave blank to continue): ")
        if inputSpace:
            spaces.append(inputSpace)
    print("Spaces:", spaces)

    connection = http.client.HTTPSConnection(confluence_url)
    headers = {
        'Authorization': f'Bearer {confluence_api_key}'
    }

    pages = []
    for space in spaces:
        nextPage = f'/rest/api/space/{space}/content/page'
        while nextPage:
            connection.request("GET", nextPage, headers=headers)
            response = connection.getresponse()
            data_raw = response.read()
            data = json.loads(data_raw)
            nextPage = data["_links"]["next"] if "_links" in data and "next" in data["_links"] else None
            for item in data["results"]:
                if item["type"] == "page":
                    url = f'{item["_links"]["self"]}?expand=body.storage'.replace(f'https://{confluence_url}', '')
                    connection.request("GET", url, headers=headers)
                    response = connection.getresponse()
                    data_raw = response.read()
                    data = json.loads(data_raw)
                    content = data["body"]["storage"]["value"]
                    if len(content) > 100:
                        pages.append({
                            "title": item["title"],
                            "content": content
                        })
    
    print("Pages:", len(pages))

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
                completion = client.chat.completions.create(
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