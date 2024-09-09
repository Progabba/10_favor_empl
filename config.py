import configparser
import os
from configparser import ConfigParser
from pprint import pprint

ROOT_DIR = os.path.dirname(__file__)
filename = os.path.join(ROOT_DIR, "database.ini")

def config(filename=filename, section='postgresql'):
    parser = ConfigParser()  # create a parser
    parser.read(filename)  # read config file
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db



if __name__ == '__main__':
    pprint(config())