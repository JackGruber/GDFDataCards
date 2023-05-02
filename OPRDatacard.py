import io
import platform
import subprocess
from PIL import Image, ImageDraw
from reportlab.lib import utils
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import sys
import os
import urllib.request
import time
import stat
import json
import re
import click
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    BASEPATH = os.path.dirname(sys.executable)
elif __file__:
    BASEPATH = os.path.dirname(__file__)

DATAFOLDER = os.path.join(BASEPATH, "data")
DATAFOLDERARMYBOOK = os.path.join(DATAFOLDER, "armybook")
FONTFOLDER = os.path.join(DATAFOLDER, "fonts")
DATACARDPDF = os.path.join(DATAFOLDER, "datacard.pdf")
IMAGEFOLDER = os.path.join(DATAFOLDER, "images")
DEBUG = False


@click.command()
@click.option(
    "--json / --txt",
    "typeJson",
    default=True,
    required=False
)
@click.option(
    "-f",
    "--file",
    "armyFile",
)
@click.option(
    "--debug / --no-debug",
    "debugOutput",
    default=False,
    required=False
)
def Main(typeJson, armyFile, debugOutput):
    global DEBUG
    DEBUG = debugOutput
    createFolderStructure()
    army = None
    if (typeJson == True):
        if (armyFile == None):
            armyFile = fileSelectDialog()

        if armyFile != None and armyFile != "":
            army = parseArmyJsonList(armyFile)
    else:
        if (armyFile != None):
            txtData = readTxtFile(armyFile)
        else:
            print("Enter Army list from 'Share as Text', complete input with two new lines")
            txtData = readMultipleLines()

        army = parseArmyTextList(txtData)

    if army != None:
        createDataCard(army['units'])
        openFile(DATACARDPDF)


def readTxtFile(file):
    try:
        f = open(file, "r")
        txtData = f.read().split("\n")
        f.close()
    except Exception as ex:
        print("Error Reading test txt file " + str(ex))
    return txtData


def fileSelectDialog():
    Tk().withdraw()
    return askopenfilename()


def createFolderStructure():
    if not os.path.exists(DATAFOLDER):
        try:
            os.makedirs(DATAFOLDER)
        except Exception as ex:
            print("Data folder creation failed")
            print(ex)
            sys.exit(1)

    if not os.path.exists(DATAFOLDERARMYBOOK):
        try:
            os.makedirs(DATAFOLDERARMYBOOK)
        except Exception as ex:
            print("army book folder creation failed")
            print(ex)
            sys.exit(1)

    if not os.path.exists(FONTFOLDER):
        try:
            os.makedirs(FONTFOLDER)
        except Exception as ex:
            print("font folder creation failed")
            print(ex)
            sys.exit(1)

    if not os.path.exists(IMAGEFOLDER):
        try:
            os.makedirs(IMAGEFOLDER)
        except Exception as ex:
            print("image folder creation failed")
            print(ex)
            sys.exit(1)


def openFile(filePath):
    if platform.system() == 'Darwin':
        subprocess.call(('open', filePath))
    elif platform.system() == 'Windows':
        os.startfile(filePath)
    else:
        subprocess.call(('xdg-open', filePath))


def createDataCard(units):
    print("Create datacards ...")
    try:
        pdfmetrics.registerFont(TTFont('bold', os.path.join(
            FONTFOLDER, "rosa-sans", "hinted-RosaSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont('regular', os.path.join(
            FONTFOLDER, "rosa-sans", "hinted-RosaSans-Regular.ttf")))
    except Exception as ex:
        print("Font is missing!")
        print(ex)
        sys.exit(1)

    datacardSize = (200.0, 130.0)
    lineColor = [1.00, 0.55, 0.10]
    # creating a pdf object
    pdf = canvas.Canvas(DATACARDPDF, pagesize=datacardSize)
    pdf.setTitle("GDF data card")

    for unit in units:
        print("  ", unit['name'], "(", unit['id'], ")")

        # Card Box
        topClearance = 10
        bottomClearance = 10
        sideClearance = 2
        pdf.setStrokeColorRGB(lineColor[0], lineColor[1], lineColor[2])
        path = pdf.beginPath()
        path.moveTo(0 + sideClearance, 0 + bottomClearance)
        path.lineTo(0 + sideClearance, datacardSize[1] - topClearance)
        path.lineTo(datacardSize[0] - sideClearance,
                    datacardSize[1] - topClearance)
        path.lineTo(datacardSize[0] - sideClearance,
                    0 + bottomClearance)
        path.close()
        pdf.setLineJoin(1)
        pdf.drawPath(path, stroke=1, fill=0)
        pdf.line(sideClearance, datacardSize[1] - 45,
                 datacardSize[0]-sideClearance, datacardSize[1] - 45)

        # Bottom Info Box
        pdf.setStrokeColorRGB(lineColor[0], lineColor[1], lineColor[2])
        pdf.setFillColorRGB(1, 1, 1)
        path = pdf.beginPath()
        sideClearance = 20
        sideClearance = 20
        height = 10
        bottomClearance = 5
        path.moveTo(0 + sideClearance, 0 + bottomClearance)
        path.lineTo(datacardSize[0] - sideClearance, 0 + bottomClearance)
        path.lineTo(datacardSize[0] - sideClearance,
                    0 + bottomClearance + height)
        path.lineTo(0 + sideClearance, 0 + bottomClearance + height)
        path.close()
        pdf.setLineJoin(1)
        pdf.drawPath(path, stroke=1, fill=1)
        pdf.setFont('bold', 4)
        pdf.setFillColorRGB(0, 0, 0)

        specialRules = []
        for rule in unit['specialRules']:
            specialRules.append(rule['label'])
        pdf.drawString(sideClearance+2, bottomClearance +
                       (height/2)-1, ", ".join(specialRules))

        # Image box
        unitImage = re.sub(r'(?is)([^\w])', '_', unit['name'].lower())
        unitImage = os.path.join(IMAGEFOLDER, unitImage)
        if os.path.exists(unitImage + ".jpg"):
            unitImage = unitImage + ".jpg"
        elif os.path.exists(unitImage + ".jpeg"):
            unitImage = unitImage + ".jpeg"
        elif os.path.exists(unitImage + ".png"):
            unitImage = unitImage + ".png"
        else:
            unitImage = None

        if (unitImage != None):
            with Image.open(unitImage) as img:
                img.load()
                imgSize = img.size
                draw = ImageDraw.Draw(img)
                draw.polygon(((0, 0), (imgSize[0]/2, imgSize[1]),
                              (0, imgSize[1])), fill=(0, 255, 0))
                draw.polygon(((imgSize[0], 0), (imgSize[0]/2, imgSize[1]),
                              (imgSize[0], imgSize[1])), fill=(0, 255, 0))
                imageBuffer = io.BytesIO()
                img.save(imageBuffer, "png")
                imageBuffer.seek(0)

        edgeLength = 60
        offsetTop = 2
        offsetRight = 35
        triangle = [
            [datacardSize[0] - edgeLength - offsetRight,
                datacardSize[1] - offsetTop],
            [datacardSize[0] - offsetRight, datacardSize[1] - offsetTop],
            [datacardSize[0] - (edgeLength/2) - offsetRight,
             datacardSize[1] - offsetTop - edgeLength]
        ]

        pdf.setStrokeColorRGB(lineColor[0], lineColor[1], lineColor[2])
        if (unitImage != None):
            pdf.drawImage(utils.ImageReader(imageBuffer), datacardSize[0] - offsetRight - edgeLength,
                          datacardSize[1] - offsetTop - edgeLength, edgeLength, edgeLength, mask=[0, 0, 255, 255, 0, 0])
            fillPath = 0
        else:
            fillPath = 1
        path = pdf.beginPath()
        path.moveTo(triangle[0][0], triangle[0][1])
        path.lineTo(triangle[1][0], triangle[1][1])
        path.lineTo(triangle[2][0], triangle[2][1])
        path.close()
        pdf.setLineJoin(1)
        pdf.drawPath(path, stroke=1, fill=fillPath)

        # Unit Name
        parts = unit['name'].split(" ")
        nameLines = []
        maxLineCahrs = 20
        lineParts = []
        for part in parts:
            if len(" ".join(lineParts)) + len(part) > maxLineCahrs:
                nameLines.append(" ".join(lineParts))
                lineParts = []
            lineParts.append(part)
        nameLines.append(" ".join(lineParts))

        pdf.setFont('bold', 10)
        pdf.setFillColorRGB(0, 0, 0)
        offset = 0
        for line in nameLines:
            pdf.drawString(5, datacardSize[1] - 25 - offset, line)
            offset += 8

        # Skills
        startX = datacardSize[0] - 25
        startY = datacardSize[1] - 20
        lineHight = 5
        pdf.setFont('bold', lineHight)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawCentredString(startX, startY, "Quality")
        pdf.drawCentredString(startX, startY - (lineHight*3), "Defense")
        pdf.setFont('regular', 5)
        pdf.drawCentredString(startX, startY - (lineHight*1), str(unit["quality"]) + "+")
        pdf.drawCentredString(startX, startY - (lineHight*4), str(unit["defense"]) + "+")

        # Weapon
        startX = 5
        startY = datacardSize[1] - 70
        offsetX = [0, 70, 90, 115, 130]
        offsetY = 0
        headers = ['Weapon', 'Range', 'Attacks', 'AP', 'Special rules']
        for i in range(len(headers)):
            pdf.setFont("bold", 5)
            pdf.setFillColorRGB(0, 0, 0)
            pdf.drawString(startX + offsetX[i], startY + offsetY, headers[i])
        offsetY -= 8

        for weapon in unit['weapons']:
            pdf.setFont("regular", 5)
            pdf.setFillColorRGB(0, 0, 0)

            if weapon['count'] > 1:
                weaponLabel = str(weapon['count']) + "x " + weapon['name']
            else:
                weaponLabel = weapon['name']

            pdf.drawString(startX + offsetX[0],
                           startY + offsetY, weaponLabel)

            if "range" in weapon:
                pdf.drawString(startX + offsetX[1], startY + offsetY, str(weapon['range']) + '"')
            else:
                pdf.drawString(startX + offsetX[1], startY + offsetY, "-")

            pdf.drawString(startX + offsetX[2], startY + offsetY, "A" + str(weapon['attacks']))

            if "ap" in weapon:
                pdf.drawString(startX + offsetX[3], startY +
                               offsetY, str(weapon['ap']))
            else:
                pdf.drawString(startX + offsetX[3], startY + offsetY, "-")

            if "specialRules" in weapon and len(weapon['specialRules']) > 0:
                label = []
                for specialRule in weapon['specialRules']:
                    label.append(str(specialRule['label']))

                pdf.drawString(startX + offsetX[4], startY + offsetY, ", ".join(label))
            else:
                pdf.drawString(startX + offsetX[4], startY + offsetY, "-")

            offsetY -= 8

        if 'equipment' in unit and len(unit['equipment']) > 0:
            headers = {'name': 'Equipment', 'specialRules': ['']}
            unit['equipment'].insert(0, headers)
            font = "bold"
            for equipment in unit['equipment']:
                pdf.setFont(font, 5)
                pdf.setFillColorRGB(0, 0, 0)
                pdf.drawString(startX + offsetX[0], startY + offsetY, equipment['name'])
                pdf.drawString(startX + offsetX[4], startY + offsetY, ", ".join(equipment['specialRules']))
                offsetY -= 8
                font = "regular"

        pdf.showPage()
    try:
        pdf.save()
    except Exception as ex:
        print("Error PDF save failed")
        print(str(ex))


def parseArmyTextList(armyListText):
    armyData = {}

    length = len(armyListText[0])
    if (length > 6 and armyListText[0][0] == "+" and armyListText[0][1] == "+" and armyListText[0][2] == " " and armyListText[0][length - 3] == " " and armyListText[0][length - 2] == "+" and armyListText[0][length - 1] == "+"):
        armyData['listName'] = armyListText[0].rstrip(" ++").lstrip("++ ")
    else:
        return False

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
                unitData['specialRules'] = []
                unitData['equipment'] = []
                for specialRules in data[2].split(","):
                    if re.match(r'^\s?(\dx\s|Scopes)', specialRules):
                        regExMatch = re.search(
                            r"(\dx)?([^(]+)(\()(.*)(\))", specialRules.strip(" "))
                        unitData['equipment'].append(
                            {'name': regExMatch.group(2).strip(" "), 'specialRules': regExMatch.group(4).split(",")})
                    else:
                        unitData['specialRules'].append({'label': specialRules})
                regExMatch = re.findall(
                    r"(?P<name>.*)\s\[(?P<unitCount>\d+)\]\sQ(?P<quality>\d+)\+\sD(?P<defense>\d+)\+$", data[0].strip(" "))
                unitData['name'] = regExMatch[0][0]
                unitData['unitCount'] = int(regExMatch[0][1])
                unitData['quality'] = int(regExMatch[0][2])
                unitData['defense'] = int(regExMatch[0][3])
            elif unit == True:
                parts = armyListText[x].strip(" ").split(" ")
                parts = list(armyListText[x].strip(" "))

                weapons = []
                weaponExtract = []
                bracket = 0
                weaponRule = False
                for part in parts:
                    if (part == "("):
                        bracket += 1
                        weaponRule = True
                    elif (part == ")"):
                        bracket -= 1

                    if (part == "," and len(weaponExtract) == 0):
                        continue

                    weaponExtract.append(part)

                    if (weaponRule == True and bracket == 0):
                        weapons.append(''.join(weaponExtract).strip())
                        weaponExtract = []
                        weaponRule = False

                for weapon in weapons:
                    regExMatch = re.search(
                        r"([^(]+)(\()(.*)(\))", weapon.strip(" "))
                    weaponData = {}
                    weaponData['name'] = regExMatch.group(1)
                    weaponRules = regExMatch.group(3).split(",")
                    for weaponRule in weaponRules:
                        weaponRule = weaponRule.strip(" ")
                        if re.match(r'\d+"', weaponRule):
                            weaponData['range'] = int(
                                weaponRule.replace('"', ''))
                        elif re.match(r'A\d+', weaponRule):
                            weaponData['attacks'] = int(
                                weaponRule.replace("A", ""))
                        elif re.match(r'AP\(\d+\)', weaponRule):
                            weaponData['ap'] = int(weaponRule.replace(
                                "AP(", "").replace(")", ""))
                        else:
                            if not "specialRules" in weaponData:
                                weaponData['specialRules'] = []
                            weaponData['specialRules'].append({'label': weaponRule})
                    if not "weapons" in unitData:
                        unitData['weapons'] = []
                    unitData['weapons'].append(weaponData)
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


def getUnit(unit, jsonArmyBookList):
    if DEBUG == True:
        print("Func: getUnit")
    data = {}
    for listUnit in jsonArmyBookList[unit['armyId']]['units']:
        if (listUnit['id'] == unit['id']):
            data['type'] = listUnit['name']
            data['name'] = listUnit['name']
            data['armyId'] = unit['armyId']
            data['id'] = listUnit['id']
            data['defense'] = listUnit['defense']
            data['quality'] = listUnit['quality']
            data['upgrades'] = listUnit['upgrades']
            data['size'] = listUnit['size']
            if "notes" in unit:
                data['notes'] = unit['notes']
            else:
                data['notes'] = None
            data['weapons'] = []
            for equipment in listUnit['equipment']:
                data['weapons'].append(getWeapon(equipment))

            data['specialRules'] = getSpecialRules(listUnit['specialRules'])
            data = getUnitUpgrades(unit, data, jsonArmyBookList)
            break
    if "customName" in unit:
        data['name'] = unit['customName']

    return data


def getSpecialRules(data):
    specialRules = []
    for specialRule in data:
        rule = specialRule
        if specialRule['rating'] != "":
            rule['label'] = specialRule['name'] + \
                "(" + specialRule['rating'] + ")"
        else:
            rule['label'] = specialRule['name']

        specialRules.append(rule)

    return specialRules


def getWeapon(data, modCount=-1):
    if DEBUG == True:
        print("Func: getWeapon")

    weapon = {}
    weapon['attacks'] = data['attacks']

    if (modCount != -1):
        weapon['count'] = modCount
    else:
        weapon['count'] = data['count']

    if "name" in data:
        weapon['name'] = data['name']

    if "range" in data and data['range'] > 0:
        weapon['range'] = data['range']

    weapon['specialRules'] = getSpecialRules(data['specialRules'])

    for i in range(len(weapon['specialRules'])):
        if weapon['specialRules'][i]['key'] == "ap":
            weapon['ap'] = weapon['specialRules'][i]['rating']
            weapon['specialRules'].pop(i)
            break

    return weapon


def removeWeapon(removeWeapon, count: int, weapons):
    for remove in removeWeapon:
        for i in range(len(weapons)):
            if re.match(r'^' + remove.strip() + 's?$', weapons[i]['name'].strip()):
                if (count == "any" or count == None or weapons[i]['count'] == 1):
                    weapons.pop(i)
                else:
                    weapons[i]['count'] -= count
                break
    return weapons


def getUnitUpgrades(unit, unitData, jsonArmyBookList):
    if DEBUG == True:
        print("Func: getUnitUpgrades")

    for upgrade in unit['selectedUpgrades']:
        armyId = unit['armyId']
        upgradeId = upgrade['upgradeId']
        optionId = upgrade['optionId']
        for package in jsonArmyBookList[armyId]['upgradePackages']:
            for section in package['sections']:
                type = None
                affects = None
                replaceWhat = None
                if "type" in section:
                    type = section['type']
                if "affects" in section:
                    affects = section['affects']
                if "replaceWhat" in section:
                    replaceWhat = section['replaceWhat']

                if (section['uid'] == upgradeId):
                    for option in section['options']:
                        if option['uid'] == optionId:
                            for gains in option['gains']:
                                if (gains['type'] == "ArmyBookWeapon"):
                                    if type == "upgrade" and affects == "all":
                                        modeCount = unitData['size']
                                    else:
                                        modeCount = -1
                                    unitData['weapons'].append(getWeapon(gains, modeCount))
                                elif gains['type'] == "ArmyBookItem":
                                    if 'equipment' not in unitData:
                                        unitData['equipment'] = []
                                    unitData['equipment'].append(addEquipment(gains))
                                elif gains['type'] == "ArmyBookRule":
                                    unitData['specialRules'].append(getSpecialRules([gains])[0])
                                else:
                                    print("Error no handling for " +
                                          gains['type'] + " upgradeId " + upgradeId + " optionId " + optionId)

                            if type == "replace":
                                if (gains['type'] == "ArmyBookWeapon"):
                                    if affects == "any":
                                        # Not sure, but by Desolator Squad HE-Launchers missing during upgrade uNapO (Replace any HE-Launcher), workarround set affects to 1
                                        affects = 1
                                    unitData['weapons'] = mergeWeapon(unitData['weapons'])
                                    unitData['weapons'] = removeWeapon(replaceWhat, affects, unitData['weapons'])
                                else:
                                    print(f"Unhandelt type '{type}' in unit upgrades")

    return unitData


def mergeWeapon(weapons):
    if DEBUG == True:
        print("Func: mergeWeapon")

    mergedWeapons = []
    for weapon in weapons:
        add = True
        for added in mergedWeapons:
            if added['name'] == weapon['name']:
                added['count'] += weapon['count']
                add = False
                break

        if (add == True):
            mergedWeapons.append(weapon)
    return mergedWeapons


def addEquipment(data):
    equipment = {}
    equipment['name'] = data['name']
    equipment['specialRules'] = []

    for rule in data['content']:
        equipment['specialRules'].append(rule['label'])

    return equipment


def parseArmyJsonList(armyListJsonFile: str):
    print("Parse army list ...")
    armyData = {}
    jsonArmyBookList = {}

    jsonArmyList = loadJsonFile(armyListJsonFile)
    armyData['armyId'] = jsonArmyList['armyId']
    armyData['gameSystemId'] = getGameSystemId(jsonArmyList['gameSystem'])

    downloadArmyBook(armyData['armyId'], armyData['gameSystemId'])

    jsonArmyBookList[armyData['armyId']] = loadJsonFile(os.path.join(
        DATAFOLDERARMYBOOK, armyData['armyId'] + "_" + str(armyData['gameSystemId']) + ".json"))
    armyData['armyName'] = jsonArmyBookList[armyData['armyId']]['name']
    armyData['listPoints'] = jsonArmyList['listPoints']
    armyData['listName'] = jsonArmyList['list']['name']

    armyData['units'] = []
    for unit in jsonArmyList['list']['units']:
        unitData = getUnit(unit, jsonArmyBookList)
        if unitData != {}:
            armyData['units'].append(unitData)

    return armyData


def loadJsonFile(jsonFile: str):
    try:
        f = open(jsonFile, encoding="utf8")
        file = f.read()
        f.close()
    except Exception as ex:
        print("file failed to open " + jsonFile)
        print(ex)
        sys.exit(1)

    try:
        jsonObj = json.loads(file)
    except json.decoder.JSONDecodeError as ex:
        print(file + " Json is not valid!")
        print(ex)
        sys.exit(1)
    except Exception as ex:
        print("Unhandeld Exception")
        print(ex)
        sys.exit(1)
    return jsonObj


def getGameSystemId(gameSystem: str):
    if (gameSystem == "gf"):
        return 2
    elif (gameSystem == "gff"):
        return 3
    elif (gameSystem == "aof"):
        return 4
    elif (gameSystem == "aofs"):
        return 5
    elif (gameSystem == "aofr"):
        return 6
    else:
        return 0


def downloadArmyBook(id: str, gameSystemId):
    armyBookJsonFile = os.path.join(DATAFOLDERARMYBOOK, str(id) + "_" + str(gameSystemId) + ".json")
    download = True
    if not os.path.exists(DATAFOLDERARMYBOOK):
        try:
            os.makedirs(DATAFOLDERARMYBOOK)
        except Exception as ex:
            print("Error data folder creation failed")
            print(ex)
            return False

    # download only when older than 1 day
    if os.path.exists(armyBookJsonFile):
        if time.time() - os.stat(armyBookJsonFile)[stat.ST_MTIME] < 86400:
            download = False

    if (download == True):
        try:
            print("Download army book ...")
            urllib.request.urlretrieve(
                "https://army-forge-studio.onepagerules.com/api/army-books/" + str(id) + "~" + str(gameSystemId) + "?armyForge=true", armyBookJsonFile)
        except Exception as ex:
            print("Error download of army book failed")
            print(ex)
            return False

    if not os.path.exists(armyBookJsonFile):
        print("Error no aramy book for " + id)
        return False

    return True


def saveDictToJson(dictData, file):
    try:
        with open(file, 'w') as fp:
            fp.write(json.dumps(dictData, indent=4))
    except Exception as ex:
        print("Error saving dict to json")
        print(ex)
        return False
    return True


if __name__ == "__main__":
    Main()
