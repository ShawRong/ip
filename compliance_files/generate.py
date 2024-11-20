import pandas as pd

def read_csv_to_dataframe(file_path):
    df = pd.read_csv(file_path)
    return df

dataframe = read_csv_to_dataframe('compliance_files/test_real_cases_hipaa_compliance.csv')
