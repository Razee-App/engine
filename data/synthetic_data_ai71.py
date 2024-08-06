import csv
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration variables
AI_MODEL = "gpt-4o-mini"  # Set this to "falcon" or "gpt-4o-mini"
MAX_ITEMS = None  # Set to None to process all items

# Model-specific configurations
MODEL_CONFIGS = {
    "falcon": {
        "model": "tiiuae/falcon-180B-chat",
        "api_key": os.getenv('AI71_API_KEY'),
        "base_url": "https://api.ai71.ai/v1/",
    },
    "gpt-4o-mini": {
        "model": "gpt-4o-mini",
        "api_key": os.getenv('OPENAI_API_KEY'),
        "base_url": "https://api.openai.com/v1/",
    }
}

# Select the appropriate configuration based on AI_MODEL
selected_config = MODEL_CONFIGS.get(AI_MODEL)
if not selected_config:
    raise ValueError(f"Invalid AI_MODEL specified. Choose either 'falcon' or 'gpt4'.")

# Initialize ChatOpenAI client
chat = ChatOpenAI(
    model=selected_config["model"],
    api_key=selected_config["api_key"],
    base_url=selected_config["base_url"],
    streaming=True
)

# Function to get a detailed scientific description from the AI API
def get_test_description(test_name):
    try:
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=f"Provide a detailed scientific description of the following lab test: {test_name}, and the purpose of conducting such test and benefits for patience in terms of health outcome")
        ]
        response = chat.stream(messages)
        description = ""
        for chunk in response:
            if chunk.content:
                description += chunk.content
        return description.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Error retrieving description"

# Read lab tests from CSV file
input_file = 'data/labTests.csv'  # Input CSV file containing lab test names
output_file = 'data/datasets/lab_tests_ingested_with_descriptions.csv'  # Output CSV file for the descriptions

# Prepare data for CSV
csv_data = [["Test ID", "CPT Code", "Test Name", "Sample Type", "Container", "TAT", "Price (AED)", "Description"]]

try:
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Skip header row
        for i, row in enumerate(reader):
            if MAX_ITEMS is not None and i >= MAX_ITEMS:
                break
            test_id, cpt_code, test_name, sample_type, container, tat, price = row
            test_name = test_name.strip()
            if test_name:
                print(f"\nFetching description for: {test_name}")
                description = get_test_description(test_name)
                csv_data.append([test_id, cpt_code, test_name, sample_type, container, tat, price, description])
                print(f"Test ID: {test_id}")
                print(f"CPT Code: {cpt_code}")
                print(f"Test Name: {test_name}")
                print(f"Sample Type: {sample_type}")
                print(f"Container: {container}")
                print(f"TAT: {tat}")
                print(f"Price: {price}")
                print(f"Description: {description}\n")
                print("-" * 80)  # Print a separator line
                time.sleep(1)  # Add delay to handle rate limits
except FileNotFoundError:
    print(f"Input file not found: {input_file}")
except Exception as e:
    print(f"Error reading the input file: {e}")

# Write data to CSV file
try:
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerows(csv_data)
    print(f"\nCSV file with descriptions has been created successfully: {output_file}")
except Exception as e:
    print(f"\nError writing to the output file: {e}")

print(f"\nProcessed {len(csv_data) - 1} items using the {AI_MODEL.upper()} model.")