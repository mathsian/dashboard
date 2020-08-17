from configparser import ConfigParser
from cloudant.client import CouchDB
import pandas as pd


class Connection(object):
    def __init__(self, db_name):
        # read the config
        config_object = ConfigParser()
        config_object.read("config.ini")
        # and get couchdb settings
        couchdb_config = config_object["COUCHDB"]
        couchdb_user = couchdb_config["user"]
        couchdb_pwd = couchdb_config["pwd"]
        couchdb_ip = couchdb_config["ip"]
        couchdb_port = couchdb_config["port"]
        # create connection
        client = CouchDB(
            couchdb_user,
            couchdb_pwd,
            url=f"http://{couchdb_ip}:{couchdb_port}",
            connect=True,
            autorenew=False,
        )
        self.client = client

    def __enter__(self):
        return self.client

    def __exit__(self, type, value, traceback):
        self.client.disconnect()


def save_docs(db_name, docs):
    """
    Does no error checking here
    """
    with Connection(db_name) as c:
        db = c[db_name]
        result = db.bulk_docs(docs)
    return result


def get_data(db_name, doc_type, key_field, key_list):
    """
    Get all docs of given data_type for a list of keys key_list

    key_list may be a single object in which case it is converted to a singleton list
    """
    if not isinstance(key_list, list):
        key_list = [key_list]
    with Connection(db_name) as c:
        db = c[db_name]
        result = db.get_view_result(
            doc_type, key_field, keys=key_list, include_docs=True
        ).all()
    return list(map(lambda r: r["doc"], result))


def get_df(db_name, doc_type, key_field, key_list):
    """Get all docs of given data_type for a list of keys as a pandas DataFrame"""
    records = get_data(db_name, doc_type, key_field, key_list)
    return pd.DataFrame.from_records(records)
