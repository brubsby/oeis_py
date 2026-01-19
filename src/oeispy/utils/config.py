import configparser
import os

CONFIG_FILENAME = "config.ini"
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "ini", CONFIG_FILENAME))


# TODO automatically get new cookie with password from config
def get_factordb_cookie():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config.get("Credentials", "fdbuser")


def get_yafu_dir():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config.get("Paths", "yafu")


def get_yafu_bin():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config.get("Paths", "yafu_bin")


def get_yafu_ini():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if config.has_option("Paths", "yafu_ini"):
        return config.get("Paths", "yafu_ini")
    return os.path.join(get_yafu_dir(), "yafu.ini")


if __name__ == "__main__":
    print(get_factordb_cookie())
