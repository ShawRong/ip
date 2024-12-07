import sys
sys.path.append("../")
import argparse
import csv
import json
from tqdm import tqdm
import datetime
import pandas as pd
import os
from poe_api_wrapper import AsyncPoeApi
import asyncio
from .build_instraction import build_instruction_compliance

# Replace with your actual tokens
tokens = {
    'p-b': 'Fs1mwf2Ym3oGvXooZG6Zsg%3D%3D',  # Replace with your actual token
    'p-lat': 'z1CIIXXmuEyntM4RMVrNe3puY2Us433OUME1hanapg%3D%3D',  # Replace with your actual token
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

def generate_prompt(instruction: str, input: str = None) -> str:
    if input:
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n### Instruction: {instruction}\n### Input: {input}\n### Response:"""
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.\n### Instruction: {instruction}\n### Response:"""

def build_prompt_legal_expert(msg="How are you today?"):
    messages = [
        {"role": "user", "content": msg}
    ]
    return messages

async def eval_cot_api(args):
    df = pd.read_csv(args.input_file)
    start = 0
    
    # Create a directory for saving responses if it doesn't exist
    output_dir = "results/responses_2"
    os.makedirs(output_dir, exist_ok=True)

    for i in tqdm(range(start, len(df))):
        row = df.iloc[i]
        
        instruction = build_instruction_compliance(row, args.mode, True)
        prompt = generate_prompt(instruction["instruction"], instruction["input"])
        
        resp = await send_prompt_to_poe(prompt)  # Get the response from Poe API
        
        # Save the response to a text file named with the index i
        response_file_path = os.path.join(output_dir, f"response_{i}.txt")
        if resp is not None:
            with open(response_file_path, 'w', encoding='utf-8') as response_file:
                response_file.write(resp)  # Write the response to the text file
        else:
            with open(response_file_path, 'w', encoding='utf-8') as response_file:
                response_file.write("No response")  # Handle case where response is None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-model", type=str, default="gpt-35-turbo")
    parser.add_argument("-task", type=str, default="compliance", choices=["compliance", "applicability"], help="Choose the task: compliance or applicability")
    parser.add_argument("-mode", type=str, default="cot", choices=["cot", "direct"], help="Choose the mode: cot or direct")
    parser.add_argument("-input_file", type=str, help="Input file path")
    
    args = parser.parse_args()
    if not args.input_file:
        args.input_file = f"../cases/train_val_test/test_real_cases_hipaa_{args.task}.csv"

    os.makedirs("results", exist_ok=True)
    
    asyncio.run(eval_cot_api(args))