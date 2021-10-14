import argparse
import data
import pandas as pd

def couchdb_to_csv(doc_type, db_name):
    docs = data.get_data("all", "type", doc_type, db_name=db_name)
    df = pd.DataFrame.from_records(docs)
    df.to_csv(f"{db_name}_{doc_type}.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a csv")
    parser.add_argument('doc_type', nargs=1)
    parser.add_argument('db_name', nargs=1)
    args = parser.parse_args()
    couchdb_to_csv(args.doc_type[0], args.db_name[0]) 
