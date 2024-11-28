import pandas as pd
import sys
import ast
import json
sys.path.append("../")

direct_instruction_template = {
    "instruction": "Please determine whether the HIPAA Privacy Rule permits or forbids the case.",
    "input": "Read the case: {case}",
    "response": "{response}"
}

cot_instruction_template = {
    "instruction": """Please assess the case for compliance with the HIPAA Privacy Rule through the following steps:
    Step 1: Check the HIPAA regulation IDs ({rag_laws}) and their content.
    Step 2: Determine whether the HIPAA Privacy Rule permits or forbids the case.""",
    "input": "Read the case: {case}",
    "response": "{response} "
}
refer_document = "./document_27"
def build_instruction_compliance(row, mode, eval):
    """
    mode: cot, direct
    """
    if mode == "direct":
        direct_instruction = direct_instruction_template.copy()
        case = row["generate_background"]
        direct_instruction["input"] = direct_instruction["input"].replace("{case}", case)
        if not eval:
            response = "HIPAA Privacy Rule permits the case." if row["generate_HIPAA_type"] == "Permit" else "HIPAA Privacy Rule forbids the case."
            direct_instruction["response"] = direct_instruction["response"].replace("{response}", response)
        return direct_instruction
    elif mode == "cot":
        cot_instruction = cot_instruction_template.copy()
        case = row["generate_background"]
        cot_instruction["input"] = cot_instruction["input"].replace("{case}", case)
        laws_string = row["rag_laws"]
        cleaned_string = laws_string.strip("{}")
        items = [item.strip().strip("'") for item in cleaned_string.split(",")]
        items = [item.replace('.txt', '') for item in items]  # Using replace
        rag_laws = ",".join(items)
        cot_instruction["instruction"] = cot_instruction["instruction"].replace("{rag_laws}", rag_laws)
        if not eval:
            response = "HIPAA Privacy Rule permits the case." if row["generate_HIPAA_type"] == "Permit" else "HIPAA Privacy Rule forbids the case."
            cot_instruction["response"] = cot_instruction["response"].replace("{response}", response)
        return cot_instruction

test_row = pd.read_csv('./eval/cases/test_real_cases_hipaa_compliance_rag.csv')
row = test_row.iloc[0]
a = build_instruction_compliance(row, "cot", True)
print(a)