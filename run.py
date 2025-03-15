from dotenv import load_dotenv
from openai import OpenAI
from confluence_client import ConfluenceClient
from rag_agent import RagAgent
import os
import sys

def main():
    load_dotenv()
    if not os.path.exists('prompts/agentic_rag.txt'):
        print("File 'prompts/agentic_rag.txt' does not exist.")
        sys.exit(1)
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
    confluence_client = ConfluenceClient(confluence_url, confluence_api_key, debug=True)
    openai_client = OpenAI()
    

    prompt = ''
    with open('prompts/agentic_rag.txt', 'r') as file:
        prompt = file.read()
    rag_agent = RagAgent(confluence_client, openai_client, prompt)
    print("'exit' to quit")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        print("Response: " + rag_agent.find_info(user_input))

if __name__ == "__main__":
    main()