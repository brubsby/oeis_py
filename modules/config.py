import configparser
import os

CONFIG_FILENAME = "config.ini"
CONFIG_PATH = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'data', 'ini', CONFIG_FILENAME))


# TODO automatically get new cookie with password from config
def get_factordb_cookie():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config.get("Credentials", "fdbuser")


if __name__ == "__main__":
    print(get_factordb_cookie())
