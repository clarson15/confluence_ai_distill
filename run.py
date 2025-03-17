from dotenv import load_dotenv
from openai import OpenAI
from agent_host import HostAgent
from confluence_client import ConfluenceClient
from agent_rag import RagAgent
import os
import sys

def main():
    load_dotenv()
    if not os.path.exists('prompts/agentic_rag.txt'):
        print("File 'prompts/agentic_rag.txt' does not exist.")
        sys.exit(1)
    if not os.path.exists('prompts/agentic_host.txt'):
        print("File 'prompts/agentic_host.txt' does not exist.")
        sys.exit(1)
    log_file_path = os.getenv("ACTIVITY_LOG")
    log_file = None
    if log_file_path:
        log_file = open(f'output/{log_file_path}', 'w+')
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
    confluence_client = ConfluenceClient(confluence_url, confluence_api_key)
    openai_client = OpenAI()
    

    rag_prompt = ''
    with open('prompts/agentic_rag.txt', 'r') as file:
        rag_prompt = file.read()
    host_prompt = ''
    with open('prompts/agentic_host.txt', 'r') as file:
        host_prompt = file.read()
    rag_agent = RagAgent(confluence_client, openai_client, rag_prompt, log_file)
    host_agent = HostAgent(rag_agent, openai_client, host_prompt, log_file)
    if os.path.exists('prompts/user.txt'):
        with open('prompts/user.txt', 'r') as file:
            print(file.read())
    print("'exit' to quit")
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            print("Response: " + host_agent.query(user_input))
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print("An error occurred: " + str(e))
    finally:
        if log_file:
            log_file.close()

if __name__ == "__main__":
    main()