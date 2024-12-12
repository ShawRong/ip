import pandas as pd
import argparse
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score




def calculate_metrics(true_labels, predicted_labels):
    accuracy = accuracy_score(true_labels, predicted_labels)
    
    precision = precision_score(true_labels, predicted_labels, average=None)  # Precision for each label
    recall = recall_score(true_labels, predicted_labels, average=None)  # Recall for each label
    f1 = f1_score(true_labels, predicted_labels, average=None)  # F1 score for each label
    
    return {
        'accuracy': accuracy,
        'precision': precision.tolist(),
        'recall': recall.tolist(),
        'f1_score': f1.tolist()
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-case_file", type=str, required=True, help="目标文件夹路径")
    parser.add_argument("-test_file", type=str, required=True, help="目标文件夹路径")
    args = parser.parse_args()

    read_file = args.case_file
    df = pd.read_csv(read_file)

    df['label'] = df['generate_HIPAA_type']
    df['index'] = df.index
    test = df[['index', 'label']]
    test['label'] = test['label'].apply(lambda x: 0 if x == 'Forbid' else 1)



    to_check = args.test_file
    to_check = pd.read_csv(to_check)

    to_check['label'] = to_check['label']
    to_check['index'] = to_check.index
    predict = to_check[['index', 'label']]
    predict['label'] = predict['label'].apply(lambda x: 0 if x == 'forbid' else 1)

    
    # Calculate and print metrics
    print(test)
    print(predict)
    metrics = calculate_metrics(test['label'], predict['label'])
    print(metrics)

