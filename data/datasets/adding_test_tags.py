import csv
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration variables
INPUT_FILE = 'data/datasets/lab_tests_ingested_with_descriptions_final.csv'
OUTPUT_FILE = 'data/datasets/lab_tests_ingested_with_descriptions_final_with_tags.csv'
AI_MODEL = "gpt-4o-mini"
MAX_ITEMS = None  # Set to None to process all items, or a number to limit processing

# Initialize ChatOpenAI client
chat = ChatOpenAI(
    model=AI_MODEL,
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.openai.com/v1/",
    streaming=True
)

def get_test_tags(test_name):
    try:
        messages = [
            SystemMessage(content="You are a helpful assistant with expertise in medical terminology."),
            HumanMessage(content=f"Generate a list of at least 15 alternative names, related terms, or common variations for the following lab test: {test_name}. Include common abbreviations, full names, and related procedures. Provide the response as a comma-separated list.")
        ]
        response = chat.stream(messages)
        tags = ""
        for chunk in response:
            if chunk.content:
                tags += chunk.content
        return tags.strip()
    except Exception as e:
        print(f"Error generating tags for {test_name}: {e}")
        return "Error retrieving tags"

def process_file():
    try:
        with open(INPUT_FILE, mode='r', newline='', encoding='utf-8') as infile, \
             open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Read and write the header, adding the new 'Tags' column
            header = next(reader)
            header.append('Tags')
            writer.writerow(header)
            
            for i, row in enumerate(reader, 1):
                if MAX_ITEMS is not None and i > MAX_ITEMS:
                    break
                
                test_name = row[2].strip()  # Assuming test name is in the third column
                print(f"Processing test {i}: {test_name}")
                
                tags = get_test_tags(test_name)
                row.append(tags)
                writer.writerow(row)
                
                print(f"Tags generated: {tags}\n")
                time.sleep(1)  # Add delay to handle rate limits
        
        print(f"\nProcessing complete. Output written to {OUTPUT_FILE}")
        print(f"Processed {i} items using the {AI_MODEL.upper()} model.")
    
    except FileNotFoundError:
        print(f"Input file not found: {INPUT_FILE}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_file()