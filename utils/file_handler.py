import pandas as pd

def extract_emails_from_file(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        emails = df.iloc[:, 0].dropna().tolist()
        return emails

    except Exception as e:
        return []