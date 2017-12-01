from pydota2.lib.gfile import *
import json

def getNameOfKey(fname, key):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        data = json.load(infile)
        return data[key]['Name']
        
def isAbilityHidden(fname, key):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        data = json.load(infile)
        return 'Hidden' in data[key].keys()
        
def isAbilityUltimate(fname, key):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        data = json.load(infile)
        return 'Ultimate' in data[key].keys()

def getUltStartingLevel(fname, key):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        data = json.load(infile)
        if 'LevelAvailable' in data[key].keys():
            return data[key]['LevelAvailable']
        else:
            return 6

def getUltLevelInterval(fname, key):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        data = json.load(infile)
        if 'LevelsBetweenUpgrades' in data[key].keys():
            return data[key]['LevelsBetweenUpgrades']
        else:
            return 6
            
if __name__ == "__main__":
    print(getNameOfKey('abilities.json', '5014'))
