import sys
import os
import urllib.request
import time
import stat
import json
import re

DATAFOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATAFOLDERARMYBOOK = os.path.join(DATAFOLDER, "armybook")


def Main():
    parseArmyTextList()


def parseArmyTextList():
    print("Enter Army list from 'Share as Text', complete input with two new lines")
    armyListText = readMultipleLines()
    armyData = {}

    length = len(armyListText[0])
    if (length > 6 and armyListText[0][0] == "+" and armyListText[0][1] == "+" and armyListText[0][2] == " " and armyListText[0][length - 3] == " " and armyListText[0][length - 2] == "+" and armyListText[0][length - 1] == "+"):
        armyData['listName'] = armyListText[0].rstrip(" ++").lstrip("++ ")
    else:
        print("No Army Data!")
        sys.exit(1)

    unit = False
    armyData['units'] = []
    unitData = {}
    for x in range(1, len(armyListText)):
        if len(armyListText[x]) > 5:
            if unit == False and armyListText[x].count('|') == 2:
                unitData = {}
                unit = True
                data = armyListText[x].split("|")
                unitData['points'] = data[1].strip(" ")
                unitData['specialRules'] = data[2].split(",")
                regExMatch = re.findall(
                    r"(?P<name>.*)\s\[(?P<unitCount>\d+)\]\sQ(?P<quality>\d+)\+\sD(?P<defense>\d+)\+$", data[0].strip(" "))
                unitData['name'] = regExMatch[0][0]
                unitData['unitCount'] = regExMatch[0][1]
                unitData['quality'] = regExMatch[0][2]
                unitData['defense'] = regExMatch[0][3]
            elif unit == True:
                regExMatch = re.findall(
                    r"([^(]+)\s(\(.*?\))(?:,\s|$)", armyListText[x].strip(" "))

                for weapon in regExMatch:
                    weaponData = {}
                    weaponData['name'] = weapon[0]
                    weaponRules = list(weapon[1])
                    weaponRules[0] = " "
                    weaponRules[len(weaponRules)-1] = " "
                    weaponRules = ''.join(weaponRules)
                    weaponRules = weaponRules.strip(" ").split(",")
                    for weaponRule in weaponRules:
                        weaponRule = weaponRule.strip(" ")
                        if re.match(r'\d+"', weaponRule):
                            weaponData['range'] = weaponRule
                        elif re.match(r'A\d+', weaponRule):
                            weaponData['attacks'] = weaponRule
                        elif re.match(r'AP\(\d+\)', weaponRule):
                            weaponData['ap'] = weaponRule.replace(
                                "AP(", "").replace(")", "")
                        else:
                            if not "specialRules" in weaponData:
                                weaponData['specialRules'] = []
                            weaponData['specialRules'].append(weaponRule)
                    if not "weapon" in unitData:
                        unitData['weapon'] = []
                    unitData['weapon'].append(weaponData)
        else:
            unit = False
            if "name" in unitData:
                armyData['units'].append(unitData)
            unitData = {}
    return armyData


def readMultipleLines():
    buffer = []
    end = 0
    while end < 2:
        line = sys.stdin.readline()
        buffer.append(line.rstrip("\n"))
        if (line == "\n"):
            end += 1
        else:
            end = 0
    return buffer



def downloadArmyBook(id: str):
    armyBookJsonFile = os.path.join(DATAFOLDERARMYBOOK, id + ".json")
    download = True

    if not os.path.exists(DATAFOLDERARMYBOOK):
        try:
            os.makedirs(DATAFOLDERARMYBOOK)
        except Exception as ex:
            print("Data folder creation failed")
            print(ex)
            sys.exit(1)

    # download only when older than 1 day
    if os.path.exists(armyBookJsonFile):
        if time.time() - os.stat(armyBookJsonFile)[stat.ST_MTIME] < 86400:
            download = False

    if (download == True):
        try:
            print("Download army book ...")
            urllib.request.urlretrieve(
                "https://army-forge-studio.onepagerules.com/api/army-books/" + id + "~3?armyForge=true", armyBookJsonFile)
        except Exception as ex:
            print("Download of army book failed")
            print(ex)

    if not os.path.exists(armyBookJsonFile):
        print("No aramy book for " + id)
        sys.exit(1)

    return True


if __name__ == "__main__":
    Main()
