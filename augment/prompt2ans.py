import os
import json
import asyncio
from poe_api_wrapper import AsyncPoeApi
from datetime import datetime
import argparse


# MongoDB connection
#mongo_client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
#b = mongo_client['qiwen_responses']  # Database name
#ollection = db['responses']  # Collection name

# Define your tokens for the Poe API
tokens = {
    'p-b': 'Fs1mwf2Ym3oGvXooZG6Zsg%3D%3D',  # Replace with your actual token
    'p-lat': '%2FJyLl2HrWb42Uh7oLhxw81N0Go%2FI7HZHrnoknnY38A%3D%3D',  # Replace with your actual token
    #'p-b': 'Fs1mwf2Ym3oGvXooZG6Zsg%3D%3D',  # Replace with your actual token
    #'p-lat': 'z1CIIXXmuEyntM4RMVrNe3puY2Us433OUME1hanapg%3D%3D',  # Replace with your actual token
    #'formkey': '939bde191131f22f6168acdb7cf6953c',
}

async def send_prompt_to_poe(prompt):
    """Send prompt to Poe API and return response."""
    try:
        client = await AsyncPoeApi(tokens=tokens).create()
        full_response = ""  # Initialize an empty string to accumulate the response
        async for chunk in client.send_message(bot="capybara", message=prompt):
            full_response += chunk["response"]  # Accumulate the response from chunks
        return full_response  # Return the complete response
    except Exception as e:
        print(f"An error occurred while contacting the Poe API: {e}")
        return None

def append_response_to_json(response, prompt_filename, output_file_path):
    """Append response to JSON file."""
    try:
        # Check if the file exists and is not empty
        file_exists = os.path.isfile(output_file_path) and os.path.getsize(output_file_path) > 0
        
        with open(output_file_path, 'a', encoding='utf-8') as json_file:
            if file_exists:
                # Only add a comma if the file is not empty
                json_file.write(',\n')  # Add comma separator if the file is not empty
            
            # Append the new response
            json.dump({"content": response, "prompt_file": prompt_filename}, json_file, ensure_ascii=False)
        
        print(f"Response appended to {output_file_path} from {prompt_filename}")
    except Exception as e:
        print(f"An error occurred while appending the response: {e}")

#def save_response_to_mongodb(response, prompt_filename):
#    """Save response to MongoDB."""
#    try:
#        # Insert into MongoDB
#        collection.insert_one({"content": response, "prompt_file": prompt_filename})
#        print("Response saved to MongoDB.")
#    except Exception as e:
#        print(f"An error occurred while saving the response to MongoDB: {e}")

def check_response_exists(prompt_filename, output_file_path):
    """Check if the response for the given prompt_filename already exists in the output JSON file."""
    try:
        if os.path.isfile(output_file_path):
            with open(output_file_path, 'r', encoding='utf-8') as json_file:
                # Load the existing responses
                existing_responses = json.load(json_file)
                # Check if the prompt_filename already exists
                for response in existing_responses:
                    if response.get("prompt_file") == prompt_filename:
                        return True  # Found a matching prompt_file
    except Exception as e:
        print(f"An error occurred while checking existing responses: {e}")
    
    return False  # No matching prompt_file found

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-source_prompts", type=str, required=True, help="prompt documents directory")
    parser.add_argument("-output_json", type=str, required=True, help="output json name")
    parser.add_argument("-previous_json", type=str, required=True, help="previous json name")

    args = parser.parse_args()
    # args.source_prompts = './compliance_files/prompt_164'  
    prompts_dir = args.source_prompts # Replace with your prompts folder path
    
    # Generate a timestamp for the output file name
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #f'response_content_{timestamp}.json'
    output_file_path = args.output_json # Output file path with timestamp
    #"response_content_25.json"
    previous_file_path = args.previous_json

    # Create JSON file and write the start of the array
    with open(output_file_path, 'a', encoding='utf-8') as json_file:
        json_file.write('[\n')  # Start JSON array

    # Iterate through all files in the prompts folder
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.txt'):  # Only process .txt files
            file_path = os.path.join(prompts_dir, filename)
            print(f"Reading prompt from file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                prompt = file.read().strip()  # Read file content and remove whitespace
            
            # Check if the response for this prompt already exists
            if check_response_exists(filename, previous_file_path):
                print(f"Response for {filename} already exists. Skipping...")
                continue  # Skip to the next file
            
            print(f"Sending prompt to Poe API: {prompt}")
            response = await send_prompt_to_poe(prompt)
            
            if response:
                print("Poe API Response:\n")
                print(response)
                
                # Append response to JSON file
                append_response_to_json(response, filename, output_file_path)
                
                # Save response to MongoDB
#                save_response_to_mongodb(response, filename)

    # End JSON array
    with open(output_file_path, 'a', encoding='utf-8') as json_file:
        json_file.write('\n]')  # End JSON array

if __name__ == "__main__":
    asyncio.run(main()) 