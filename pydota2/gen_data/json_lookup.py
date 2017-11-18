from pydota2.lib.gfile import *
import json

def getNameOfKey(fname, key):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        data = json.load(infile)
        return data[key]['Name']
        
if __name__ == "__main__":
    print(getNameOfKey('abilities.json', '5014'))