from os.path import join
import re
import json

lineCount = 0

abilities = {}

def writeData(data):
    with open(join('pydota2', 'gen_data', 'abilities.json'), 'w') as outfile:
        json.dump(data, outfile, indent = 4)

        
shiftCount = 0
abilitiesCount = 0
currName = None
abilityID = None
if __name__ == "__main__":
    fName = open('C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\scripts\\npc\\npc_abilities.txt', 'r')

    content = fName.readlines()
    content = [x.strip() for x in content]
    #print(len(content))

    fName.close()

    for line in content:
        lineCount += 1
        
        if line == '{':
            shiftCount += 1
            continue

        if line == '}':
            shiftCount -= 1
            
            if shiftCount == 1:
                currName = None
                abilityID = None
                
            continue
        
        if shiftCount == 1:
            comment = line[:2] == '//'
            underscore = line.find('_')
            if not comment and underscore > 0:
                #print(line)
                abilitiesCount = abilitiesCount + 1
                currName = line.strip().replace('"','')
                
        if shiftCount == 2:
            comment = line[:2] == '//'
            if not comment:
                if line[:4] == '"ID"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    abilityID = res[1]
                    abilities[res[1]] = {}
                    if currName != None:
                        abilities[res[1]]['Name'] = currName
                    else:
                        print("ERROR: Name missing!")
                        break
                if line[:17] == '"AbilityBehavior"':
                    if line.find("DOTA_ABILITY_BEHAVIOR_HIDDEN") >= 0:
                        if abilityID != None:
                            abilities[abilityID]['Hidden'] = 1
                        else:
                            print("Error: AbilityID missing!")
                            break
                if line[:13] == '"AbilityType"':
                    if line.find("DOTA_ABILITY_TYPE_ULTIMATE") >= 0:
                        if abilityID != None:
                            abilities[abilityID]['Ultimate'] = 1
                        else:
                            print("Error: AbilityID missing!")
                            break
                if line[:15] == '"RequiredLevel"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    if abilityID != None:
                        abilities[abilityID]['LevelAvailable'] = int(res[1])
                    else:
                        print("ERROR: abilityID missing!")
                        break
                if line[:23] == '"LevelsBetweenUpgrades"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    if abilityID != None:
                        abilities[abilityID]['LevelsBetweenUpgrades'] = int(res[1])
                    else:
                        print("ERROR: abilityID missing!")
                        break
                        
    #print(abilities)
    print('Processed %d abilities' % (abilitiesCount))
    writeData(abilities)