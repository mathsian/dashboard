import argparse
import data
import pandas as pd

def csv_to_couchdb(file_name, dbname=None):
    print(file_name)
    print(dbname)
    df = pd.read_csv(file_name).fillna("").astype(str)
    print(f"{len(df)} rows")
    print(df.columns)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    print(df.head())
    docs = df.to_dict(orient='records')
    confirm = input("Go ahead? y/N ").lower().strip()[:1]
    if confirm != "y":
        return -1
    print(data.save_docs(docs, db_name=dbname))
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a csv")
    parser.add_argument('file_name', nargs=1)
    parser.add_argument('db_name', nargs=1)
    args = parser.parse_args()
    csv_to_couchdb(args.file_name[0], args.db_name[0]) 
