import csv
import re

def clean_text(text):
    # Remove numbered list markers
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
    
    # Remove bullet points
    text = re.sub(r'^\s*•\s*', '', text, flags=re.MULTILINE)
    
    # Remove headers (###)
    text = re.sub(r'^###\s*', '', text, flags=re.MULTILINE)
    
    # Remove emphasis and strong emphasis
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    
    # Remove any remaining special characters
    text = re.sub(r'[#*_~`\[\]]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_csv_file(input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if 'Description' in row:
                row['Description'] = clean_text(row['Description'])
            writer.writerow(row)

    print(f"Cleaned CSV has been written to {output_file}")

# Example usage
input_file = 'data/datasets/lab_tests_ingested_with_descriptions.csv'
output_file = 'data/datasets/lab_tests_ingested_with_descriptions_final.csv'
clean_csv_file(input_file, output_file)