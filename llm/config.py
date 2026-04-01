import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the /llm directory
load_dotenv()

class Config:
    # --- AWS Bedrock Settings ---
    REGION = os.getenv("AWS_REGION", "us-east-1")
    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    
    # --- Inference Parameters ---
    TEMPERATURE = 0.2
    MAX_TOKENS = 2500
    TOP_P = 0.9

    # --- Path Resolution (Windows/Linux Compatible) ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

    # --- File System Paths (Input/Output) ---
    INPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "input.json"))
    OUTPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "output.json"))
