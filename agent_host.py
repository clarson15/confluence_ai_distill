from io import TextIOWrapper
from agent_rag import RagAgent
from openai import OpenAI
import json

class HostAgent():
    def __init__(self, rag_agent: RagAgent, openai_client: OpenAI, prompt: str, log_file: TextIOWrapper | None = None):
        self.rag_agent = rag_agent
        self.openai_client = openai_client
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "lookup_info",
                    "description": "Looks up information in the documentation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The question to research and answer from the documentation"
                            }
                        },
                        "required": ["prompt"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]
        self.prompt = prompt
        self.log_file = log_file

    def query(self, prompt) -> str:
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
        if self.log_file:
            self.log_file.write(f"[Host Agent] Prompt: {prompt}\n")
        try:
            while True:
                completion = self.openai_client.chat.completions.create(
                    model = "gpt-4o-mini",
                    tools = self.tools,
                    messages = messages
                )
                messages.append(completion.choices[0].message)
                if self.log_file and completion.choices[0].message.content:
                    self.log_file.write(f"[Host Agent] Response: {completion.choices[0].message.content}\n")
                if completion.choices[0].message.tool_calls:
                    for tool_call in completion.choices[0].message.tool_calls:
                        if tool_call.type == "function" and tool_call.function.name == "lookup_info":
                            args = json.loads(tool_call.function.arguments)
                            if "prompt" not in args:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": "Missing prompt"
                                })
                                continue

                            rag_prompt = args["prompt"]
                            rag_answer = self.rag_agent.find_info(rag_prompt)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": rag_answer
                            })
                            continue
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "Invalid function call"
                        })
                    continue
                return completion.choices[0].message.content

        except Exception as e:
            print(messages)
            return str(e)