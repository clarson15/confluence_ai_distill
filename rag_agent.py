from confluence_client import ConfluenceClient
from openai import OpenAI
import json

class RagAgent():
    def __init__(self, confluence_client: ConfluenceClient, openai_client: OpenAI, prompt: str, debug: bool = False):
        self.confluence_client = confluence_client
        self.openai_client = openai_client
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_document",
                    "description": "Fetches the contents and children of a document",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "page": {
                                "type": "string",
                                "description": "The page URL (https://confluence.yourcompany.com/display/ABC/Overview) or page ID (1234567) to fetch."
                            }
                        },
                        "required": ["page"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]
        self.prompt = prompt
        self.debug = debug

    def find_info(self, prompt) -> str:
        messages = [
            {
                "role": "developer",
                "content": self.prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        try:
            final_answer = None
            while True:
                completion = self.openai_client.chat.completions.create(
                    model = "gpt-4o-mini",
                    tools = self.tools,
                    messages = messages
                )
                messages.append(completion.choices[0].message)
                if completion.choices[0].message.tool_calls:
                    final_answer = None
                    for tool_call in completion.choices[0].message.tool_calls:
                        if tool_call.type == "function" and tool_call.function.name == "get_document":
                            args = json.loads(tool_call.function.arguments)
                            if "page" not in args:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": "Missing page id"
                                })
                                continue

                            page_id = args["page"]
                            page = self.confluence_client.get_page_content(page_id)
                            children = self.confluence_client.get_page_children(page_id)
                            page += f'\n# Children\n'
                            page += '\n'.join([f'Page ID: {child[1]}: Title: {child[0]}' for child in children])
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": page
                            })
                            continue
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "Invalid function call"
                        })
                    continue

                if final_answer and completion.choices[0].message.content == "Yes.":
                    if self.debug:
                        print(messages)
                    return final_answer
                elif final_answer:
                    print(completion.choices[0].message.content)
                
                final_answer = completion.choices[0].message.content
                messages.append({
                    "role": "user",
                    "content": "Have you completely answered `{prompt}` to the best of your abilities? If yes, respond only with 'Yes.'. If no, continue exploring the documentation and respond again with a new final answer."
                })

        except Exception as e:
            print(messages)
            return str(e)