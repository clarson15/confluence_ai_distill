import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_api_key = os.getenv("CONFLUENCE_API_KEY")
    
    print("CONFLUENCE_URL:", confluence_url)
    print("CONFLUENCE_API_KEY:", confluence_api_key)

    with open("./output/test.txt", "w") as file:
        file.write("This is a test file for the confluence summarizer.")
        file.close()
    
    # print file names in the output directory
    print("Files in the output directory:")
    for file in os.listdir("./output"):
        print(file)

if __name__ == "__main__":
    main()