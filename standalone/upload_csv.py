import sys
sys.path.append('..')
import data
import argparse
import pandas as pd

def csv_to_couchdb(file_name, dbname=None):
    print(file_name)
    print(dbname)
    dtype_dict = {
        "_id": str,
        "cohort": str,
        "student_id": str
    }
    df = pd.read_csv(file_name, dtype=dtype_dict).fillna("")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    if not '_id' in df.columns:
        df['_id'] = ""
    if not '_rev' in df.columns:
        df['_rev'] = ""
    new_df = df.query('_id == ""').drop(['_id', '_rev'], axis=1)
    print(new_df)
    changed_df = df.query('_id != ""')
    print(changed_df)
    new_docs = new_df.to_dict(orient='records')
    changed_docs = changed_df.to_dict(orient='records')
    confirm = input("Go ahead? y/N ").lower().strip()[:1]
    if confirm != "y":
        return -1
    print(data.save_docs(new_docs, db_name=dbname))
    print(data.save_docs(changed_docs, db_name=dbname))
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a csv")
    parser.add_argument('file_name', nargs=1)
    parser.add_argument('db_name', nargs=1)
    args = parser.parse_args()
    csv_to_couchdb(args.file_name[0], args.db_name[0]) 
