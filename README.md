# Confluence AI Summarizer

## Overview
Confluence AI Summarizer is a Python script designed to traverse a Confluence space, extract important information, and summarize it in a clean and logical format. The goal is to help teams quickly understand and digest the key content in Confluence, streamlining documentation reviews and aiding in decision-making processes.

## Prerequisites
- Docker (for the containerized version)
- Python 3.6+ (if running the script directly without Docker)

## Installation

### Using Docker
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/confluence-ai-summarizer.git
    cd confluence-ai-summarizer
    ```
2. Run the relevant script:
    ```bash
    ./run.sh
    ```
    or
    ```bash
    ./run.ps1
    ```
3. Provide the confluence space key from the terminal

### Using Python Directly
1. Clone the repository and navigate to the project directory.
2. Create a virtual environment and install the necessary dependencies:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    pip install -r requirements.txt
    ```
3. Run the script:
    ```bash
    python main.py
    ```

## Usage
Configure the script settings (e.g., Confluence API credentials, OpenAI credentials) via a configuration file or environment variables as detailed in the documentation. Then, run the script to generate a summarized version of your Confluence space.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
