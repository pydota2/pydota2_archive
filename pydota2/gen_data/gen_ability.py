from os.path import join
import re
import json



def writeData(data, fname):
    with open(join('pydota2', 'gen_data', fname), 'w') as outfile:
        json.dump(data, outfile, indent = 4)

def processHeroes():
    fName = open('C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\scripts\\npc\\npc_heroes.txt', 'r')

    content = fName.readlines()
    content = [x.strip() for x in content]
    #print(len(content))

    fName.close()
    
    shiftCount = 0
    heroCount = 0
    currName = None
    heroID = None
    lineCount = 0
    heroes = {}

    for line in content:
        lineCount += 1
        
        if line == '{':
            shiftCount += 1
            continue

        if line == '}':
            shiftCount -= 1
            
            if shiftCount == 1:
                currName = None
                heroID = None
            continue
            
        if shiftCount == 1:
            comment = line[:2] == '//'
            underscore = line.find('_')
            if not comment and underscore > 0:
                #print(line)
                heroCount += 1
                currName = line.strip().replace('"','')
        
        if shiftCount == 2 and currName and currName != 'npc_dota_hero_base':
            comment = line[:2] == '//'
            if not comment:
                if line[:8] == '"HeroID"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    heroID = res[1]
                    heroes[res[1]] = {}
                    if currName != None:
                        heroes[res[1]]['Name'] = currName
                        heroes[res[1]]['Talents'] = {}
                    else:
                        print("ERROR: Name missing!")
                        break
                        
                if line.find('special_bonus') > 0:
                    if heroID != None:
                        res = re.split(r'\s{2,}', line)
                        heroes[heroID]['Talents']['Talent_'+str(len(heroes[heroID]['Talents'])+1)] = res[1].replace('"', '')
                    else:
                        print("Error: HeroID missing!")
                        break
                
                if line[:18] == '"MovementTurnRate"':
                    if heroID != None:
                        res = re.split(r'\s{2,}', line)
                        heroes[heroID]['TurnRate'] = float(res[1].replace('"', ''))
                    else:
                        print("Error: HeroID missing!")
                        break
                    
    print('Processed %d heroes' % (heroCount))
    writeData(heroes, 'heroes.json')

def processAbilities():
    fName = open('C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\scripts\\npc\\npc_abilities.txt', 'r')

    content = fName.readlines()
    content = [x.strip() for x in content]
    #print(len(content))

    fName.close()
    
    shiftCount = 0
    abilitiesCount = 0
    currName = None
    abilityID = None
    lineCount = 0
    abilities = {}

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
                abilitiesCount += 1
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
    writeData(abilities, 'abilities.json')
    
if __name__ == "__main__":
    processAbilities()
    processHeroes()