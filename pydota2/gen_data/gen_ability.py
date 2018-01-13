from os.path import join
import re
import json



def writeData(data, fname):
    with open(join('pydota2', 'gen_data', fname), 'w') as outfile:
        json.dump(data, outfile, indent = 4)

def processUnits():
    fName = open('C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\scripts\\npc\\npc_units.txt', 'r')
    
    content = fName.readlines()
    content = [x.strip() for x in content]
    #print(len(content))

    fName.close()
    
    shiftCount = 0
    unitCount = 0
    currName = None
    unitID = None
    lineCount = 0
    units = {}
    
    for line in content:
        lineCount += 1
        
        if line == '{':
            shiftCount += 1
            continue

        if line == '}':
            shiftCount -= 1
            
            if shiftCount == 1:
                currName = None
                unitID = None
            continue
        
        if shiftCount == 1:
            comment = line[:2] == '//'
            underscore = line.find('_')
            if not comment and underscore > 0:
                #print(line)
                unitCount += 1
                currName = line.strip().replace('"','')
        
        if shiftCount == 2 and currName:
            comment = line[:2] == '//'
            if not comment:
                if not currName in units.keys():
                    units[currName] = {}
                
                if line[:15] == '"ArmorPhysical"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    units[currName]['PhysicalResist'] = float(res[1])
                
                if line[:19] == '"MagicalResistance"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    units[currName]['MagicResist'] = float(res[1])
    
    print('Processed %d units' % (unitCount))
    writeData(units, 'units.json')
    

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
    
    heroValues = [
        "MovementTurnRate",
        "MovementSpeed",
        "AttackRange",
        "ProjectileSpeed",
        "AttackRate",
        "AttributeBaseStrength",
        "AttributeStrengthGain",
        "AttributeBaseIntelligence",
        "AttributeIntelligenceGain",
        "AttributeBaseAgility",
        "AttributeAgilityGain",
        "ArmorPhysical",
    ]

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
                
                for value in heroValues:
                    if heroID != None and line[:len(value)+2] == ('"'+value+'"'):
                        res = re.split(r'\s{1,}', line)
                        try:
                            if res[1].find('.') >= 0:
                                heroes[heroID][value] = float(res[1].replace('"', ''))
                            elif res[1].find('_') >= 0:
                                heroes[heroID][value] = str(res[1].replace('"', ''))
                            else:
                                heroes[heroID][value] = int(res[1].replace('"', ''))
                        except Exception as e:
                            print(e, res)
                    
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
                    res = re.split(r'\s{1,}', line)
                    res[1] = res[1].replace('"','').replace('//', '')
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
                    if line.find("DOTA_ABILITY_BEHAVIOR_PASSIVE") >= 0:
                        if abilityID != None:
                            abilities[abilityID]['Passive'] = 1
                        else:
                            print("Error: AbilityID missing!")
                            break
                    if line.find("DOTA_ABILITY_BEHAVIOR_AOE") >= 0:
                        if abilityID != None:
                            abilities[abilityID]['AOE'] = 1
                        else:
                            print("Error: AbilityID missing!")
                            break
                    if line.find("DOTA_ABILITY_BEHAVIOR_AURA") >= 0:
                        if abilityID != None:
                            abilities[abilityID]['Aura'] = 1
                        else:
                            print("Error: AbilityID missing!")
                            break
                            
                    
                    tgt_mask = 0
                    if line.find("DOTA_ABILITY_BEHAVIOR_POINT") >= 0:
                        tgt_mask |= 1
                    if line.find("DOTA_ABILITY_BEHAVIOR_UNIT_TARGET") >= 0:
                        tgt_mask |= 2
                    if line.find("DOTA_ABILITY_BEHAVIOR_NO_TARGET") >= 0:
                        tgt_mask |= 4    
                    if abilityID != None:
                        abilities[abilityID]['TargetMask'] = tgt_mask
                    else:
                        print("Error: AbilityID missing!")
                        break
                
                if line[:23] == '"AbilityUnitTargetTeam"':
                    tgt_team = None
                    if line.find("DOTA_UNIT_TARGET_TEAM_ENEMY") >= 0:
                        tgt_team = 1
                    elif line.find("DOTA_UNIT_TARGET_TEAM_FRIENDLY") >= 0:
                        tgt_team = 2
                    elif line.find("DOTA_UNIT_TARGET_TEAM_BOTH") >= 0:
                        tgt_team = 3
                    elif line.find("DOTA_UNIT_TARGET_TEAM_CUSTOM") >= 0:
                        tgt_team = 4
                        
                    if abilityID != None:
                        abilities[abilityID]['TargetTeam'] = tgt_team
                    else:
                        print("Error: AbilityID missing!")
                        break
                
                if line[:23] == '"AbilityUnitDamageType"':
                    # 0 is none (for non-damaging abilities), won't be listed
                    # 1 - physical, 2 - magic, 3 - pure
                    dmg_type = 0
                    if line.find("DAMAGE_TYPE_PURE") >= 0:
                        dmg_type = 3
                    elif line.find("DAMAGE_TYPE_MAGICAL") >= 0:
                        dmg_type = 2
                    elif line.find("DAMAGE_TYPE_PHYSICAL") >= 0:
                        dmg_type = 1
                        
                    if abilityID != None:
                        abilities[abilityID]['DamageType'] = dmg_type
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
                
                if line[:18] == '"AbilityCastPoint"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    
                    multi = re.split(r'\s{1,}', res[1])
                    if not multi:
                        multi = [res[1]]
                    
                    if abilityID != None:
                        abilities[abilityID]['Castpoint'] = []
                        for value in multi:
                            abilities[abilityID]['Castpoint'].append(float(value))
                    else:
                        print("Error: AbilityID missing!")
                        break
                
                if line[:17] == '"AbilityCooldown"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    
                    multi = re.split(r'\s{1,}', res[1])
                    if not multi:
                        multi = [res[1]]
                    
                    if abilityID != None:
                        abilities[abilityID]['Cooldown'] = []
                        for value in multi:
                            abilities[abilityID]['Cooldown'].append(float(value))
                    else:
                        print("Error: AbilityID missing!")
                        break
                        
                if line[:17] == '"AbilityManaCost"':
                    res = re.split(r'\s{2,}', line)
                    res[1] = res[1].replace('"','')
                    
                    multi = re.split(r'\s{1,}', res[1])
                    if not multi:
                        multi = [res[1]]
                    
                    if abilityID != None:
                        abilities[abilityID]['Manacost'] = []
                        for value in multi:
                            abilities[abilityID]['Manacost'].append(float(value))
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
    processUnits()