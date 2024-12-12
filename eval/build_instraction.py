import pandas as pd
import sys
import ast
import json

direct_instruction_template = {
    "instruction": "Please determine whether the HIPAA Privacy Rule permits or forbids the case. Please use Permit or Forbid to answer.",
    "input": "Read the case: {case}",
    "response": "{response}"
}

rag_instruction_template = {
    "instruction": """Please assess the case for compliance with the HIPAA Privacy Rule through the following steps:
    Step 1: Check the HIPAA regulation IDs ({rag_laws}) and their content.
    Step 2: Determine whether the HIPAA Privacy Rule permits or forbids the case.
    Step 3: Please use Permit or Forbid to answer.""",
    "input": "Read the case: {case}",
    "response": "{response}"
}

def build_instruction_compliance(row, mode):
    """
    mode: rag, direct
    """
    if mode == "direct":
        direct_instruction = direct_instruction_template.copy()
        case = row["generate_background"]
        direct_instruction["input"] = direct_instruction["input"].replace("{case}", case)
        return direct_instruction
    elif mode == "rag":
        rag_instruction = rag_instruction_template.copy()
        case = row["generate_background"]
        rag_instruction["input"] = rag_instruction["input"].replace("{case}", case)
        laws_string = row["rag_laws"]
        cleaned_string = laws_string.strip("{}")
        items = [item.strip().strip("'") for item in cleaned_string.split(",")]
        items = [item.replace('.txt', '') for item in items]  # Using replace
        rag_laws = ",".join(items)
        rag_instruction["instruction"] = rag_instruction["instruction"].replace("{rag_laws}", rag_laws)
        return rag_instruction

#test_row = pd.read_csv('./eval/cases/test_real_cases_hipaa_compliance_rag.csv')
#row = test_row.iloc[0]
#a = build_instruction_compliance(row, "rag")
#print(a)