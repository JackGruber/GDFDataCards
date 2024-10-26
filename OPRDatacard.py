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
import pathlib
import requests
import zipfile

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    BASEPATH = os.path.dirname(sys.executable)
elif __file__:
    BASEPATH = os.path.dirname(__file__)

DATAFOLDER = os.path.join(BASEPATH, "data")
DATAFOLDERARMYBOOK = os.path.join(DATAFOLDER, "armybook")
FONTFOLDER = os.path.join(DATAFOLDER, "fonts")
DATACARDFOLDER = os.path.join(DATAFOLDER, "datacards")
IMAGEFOLDER = os.path.join(DATAFOLDER, "images")
IMAGEJSON = os.path.join(IMAGEFOLDER, "images.json")
DEBUG = False


@click.command()
@click.option(
    "--json",
    "forceTypeJson",
    is_flag=True,
    default=False,
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
@click.option(
    "--validate / --no-validate",
    "validateVersion",
    default=True,
    required=False
)

def Main(forceTypeJson, armyFile, debugOutput, validateVersion):
    global DEBUG
    DEBUG = debugOutput
    createStructure()
    checkFonts()

    if (armyFile == None):
        armyFile = fileSelectDialog()

    if armyFile == None or armyFile == "":
        print("No army file selected")
        waitForKeyPressAndExit()

    typeJson = isFileTypeJson(armyFile)
    army = None
    if (typeJson == True or forceTypeJson == True):
        print("Parse json army file")
        army = parseArmyJsonList(armyFile, validateVersion)
    else:
        print("Parse txt army file")
        txtData = readTxtFile(armyFile)
        army = parseArmyTextList(txtData)
    if army != None and army != False:
        if (DEBUG == True):
            saveDictToJson(army, os.path.join(DATAFOLDER, "debug_army.json"))

        pdfFile = createDataCard(army)
        openFile(pdfFile)


def isFileTypeJson(file):
    if file != None and file != "":
        suffixes = pathlib.Path(file).suffixes
        if (suffixes[len(suffixes) - 1].lower() == ".json"):
            return True
    return False


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


def createStructure():
    if not os.path.exists(DATAFOLDER):
        try:
            os.makedirs(DATAFOLDER)
        except Exception as ex:
            print("Data folder creation failed")
            print(ex)
            waitForKeyPressAndExit()

    if not os.path.exists(DATAFOLDERARMYBOOK):
        try:
            os.makedirs(DATAFOLDERARMYBOOK)
        except Exception as ex:
            print("army book folder creation failed")
            print(ex)
            waitForKeyPressAndExit()

    if not os.path.exists(FONTFOLDER):
        try:
            os.makedirs(FONTFOLDER)
        except Exception as ex:
            print("font folder creation failed")
            print(ex)
            waitForKeyPressAndExit()

    if not os.path.exists(IMAGEFOLDER):
        try:
            os.makedirs(IMAGEFOLDER)
        except Exception as ex:
            print("image folder creation failed")
            print(ex)
            waitForKeyPressAndExit()

    if not os.path.exists(DATACARDFOLDER):
        try:
            os.makedirs(DATACARDFOLDER)
        except Exception as ex:
            print("datacard folder creation failed")
            print(ex)
            waitForKeyPressAndExit()

    if not os.path.exists(IMAGEJSON):
        example = [
            {
                'listName': '*',
                'armyFaction': 'Human Defense Force',
                'unitType': 'Company Leader',
                'unitName': '*',
                'weaponOrEquipment': "*",
                'image': 'example.jpg',
            },
            {
                'listName': '*',
                'armyFaction': '*',
                'unitType': '*',
                'unitName': 'Herg Alasem',
                'weaponOrEquipment': "*",
                'image': 'example.jpg',
            },
            {
                'listName': '*',
                'armyFaction': '*',
                'unitType': 'Storm Trooper',
                'unitName': '*',
                'weaponOrEquipment': "Flamer",
                'image': 'example.jpg',
            },
        ]
        saveDictToJson(example, os.path.join(IMAGEJSON))


def openFile(filePath):
    if platform.system() == 'Darwin':
        subprocess.call(('open', filePath))
    elif platform.system() == 'Windows':
        os.startfile(filePath)
    else:
        subprocess.call(('xdg-open', filePath))


def dataCardBoarderFrame(pdf, dataCardParameters):
    pdf.setStrokeColorRGB(dataCardParameters['lineColor'][0],
                          dataCardParameters['lineColor'][1], dataCardParameters['lineColor'][2])
    path = pdf.beginPath()
    path.moveTo(0 + dataCardParameters['sideClearance'], 0 + dataCardParameters['bottomClearance'])
    path.lineTo(0 + dataCardParameters['sideClearance'],
                dataCardParameters['pdfSize'][1] - dataCardParameters['topClearance'])
    path.lineTo(dataCardParameters['pdfSize'][0] - dataCardParameters['sideClearance'],
                dataCardParameters['pdfSize'][1] - dataCardParameters['topClearance'])
    path.lineTo(dataCardParameters['pdfSize'][0] - dataCardParameters['sideClearance'],
                0 + dataCardParameters['bottomClearance'])
    path.close()
    pdf.setLineJoin(1)
    pdf.drawPath(path, stroke=1, fill=0)

def getUnitCost(unit):
    cost = unit['cost']
    if 'upgradeCost' in unit:
        for addCost in unit['upgradeCost']:
            cost += addCost
    return cost

def dataCardUnitPoints(pdf, dataCardParameters, unit):
    if 'cost' in unit:
        startX = (dataCardParameters['pdfSize'][0] / 2) + 35
        startY = dataCardParameters['pdfSize'][1] - 47
        pdf.setFont('regular', 8)
        pdf.setFillColorRGB(0, 0, 0)

        cost = getUnitCost(unit)

        sideClearance = 20
        bottomClearance = 5
        height = 10
        pdf.setFont('regular', 7)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawRightString(dataCardParameters['pdfSize'][0] - 22, bottomClearance +
                            (height/2)-2, str(cost) + " pt")


def dataCardUnitType(pdf, dataCardParameters, unit):
    # Unit type
    pdf.line(dataCardParameters['sideClearance'], dataCardParameters['pdfSize'][1] - 50,
             dataCardParameters['pdfSize'][0] - dataCardParameters['sideClearance'], dataCardParameters['pdfSize'][1] - 50)
    smallInfo = []
    if (unit['size'] > 1):
        smallInfo.append(str(unit['size']) + "x")

    if 'type' in unit and unit['name'] != unit['type']:
        smallInfo.append(unit['type'])

    pdf.setFont('regular', 8)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(5, dataCardParameters['pdfSize'][1] - 47, " ".join(smallInfo))


def dataCardUnitWounds(pdf, dataCardParameters, unit, army):
    if 'gameSystem' in army and army['gameSystem'] == "gff":
        woundsSize = 12
        wounds = 5
        tough = 0
        startX = 2
        startY = dataCardParameters['pdfSize'][1] - 50 - woundsSize
        for rule in unit['rules']:
            if (rule['name'].lower() == "tough"):
                tough = int(rule['rating']) - 1

        pdf.setLineJoin(1)
        pdf.setFillColorRGB(0.5, 0.5, 0.5)
        path = pdf.beginPath()
        path.moveTo(startX, startY)
        path.lineTo(startX + (woundsSize * tough), startY)
        path.lineTo(startX + (woundsSize * tough), startY + woundsSize)
        path.lineTo(startX, startY + woundsSize)
        path.close()
        pdf.drawPath(path, stroke=1, fill=0)

        path = pdf.beginPath()
        path.moveTo(startX + (woundsSize * tough), startY)
        path.lineTo(startX + (woundsSize * tough) + (woundsSize * wounds), startY)
        path.lineTo(startX + (woundsSize * tough) + (woundsSize * wounds), startY + woundsSize)
        path.lineTo(startX + (woundsSize * tough), startY + woundsSize)

        path.close()
        pdf.drawPath(path, stroke=1, fill=1)

        w6 = 5
        for i in range(wounds + tough):
            pdf.line(startX + (woundsSize*i), startY, startX + (woundsSize*i), startY + woundsSize)
            pdf.setFillColorRGB(1, 1, 1)

            if (i < tough):
                text = "-"
            else:
                text = str(w6) + "+"
                w6 -= 1
            pdf.drawCentredString(startX + (woundsSize*i) + (woundsSize/2), startY + (woundsSize/2) - 3, text)


def dataCardUnitRules(pdf, dataCardParameters, unit):
    pdf.setStrokeColorRGB(dataCardParameters['lineColor'][0],
                          dataCardParameters['lineColor'][1], dataCardParameters['lineColor'][2])
    pdf.setFillColorRGB(1, 1, 1)
    path = pdf.beginPath()
    sideClearance = 20
    height = 10
    bottomClearance = 5
    path.moveTo(0 + sideClearance, 0 + bottomClearance)
    path.lineTo(dataCardParameters['pdfSize'][0] - sideClearance, 0 + bottomClearance)
    path.lineTo(dataCardParameters['pdfSize'][0] - sideClearance,
                0 + bottomClearance + height)
    path.lineTo(0 + sideClearance, 0 + bottomClearance + height)
    path.close()
    pdf.setLineJoin(1)
    pdf.drawPath(path, stroke=1, fill=1)
    pdf.setFont('bold', 7)
    pdf.setFillColorRGB(0, 0, 0)

    specialRules = []
    for rule in unit['rules']:
        specialRules.append(rule['label'])
    pdf.drawString(sideClearance+2, bottomClearance +
                   (height/2)-2, ", ".join(specialRules))


def dataCardUnitImage(pdf, dataCardParameters, unit, listName, armyFaction):
    imageInfos = loadJsonFile(IMAGEJSON)

    unitImage = None
    for imageInfo in imageInfos:
        if imageInfo['unitName'] == "*" or re.search(r'(?is)' + imageInfo['unitName'], unit['name'].strip()):
            if imageInfo['unitType'] == "*" or re.search(r'(?is)' + imageInfo['unitType'], unit['type'].strip()):
                if imageInfo['listName'] == "*" or re.search(r'(?is)' + imageInfo['listName'], listName.strip()):
                    if imageInfo['armyFaction'] == "*" or re.search(r'(?is)' + imageInfo['armyFaction'], armyFaction.strip()):
                        if imageInfo['weaponOrEquipment'] == "*":
                            unitImage = os.path.join(IMAGEFOLDER, imageInfo['image'])
                        else:
                            for weapon in unit['weapons']:
                                if re.search(r'(?is)' + imageInfo['weaponOrEquipment'], weapon['name'].strip()):
                                    unitImage = os.path.join(IMAGEFOLDER, imageInfo['image'])

                            if 'equipment' in unit:
                                for equipment in unit['equipment']:
                                    if re.search(r'(?is)' + imageInfo['weaponOrEquipment'], equipment['name'].strip()):
                                        unitImage = os.path.join(IMAGEFOLDER, imageInfo['image'])

                        if unitImage is not None:
                            unitImage = os.path.join(IMAGEFOLDER, imageInfo['image'])
                            if not os.path.exists(unitImage):
                                unitImage = None
                            break

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

    edgeLength = 65
    offsetTop = 2
    offsetRight = 40
    triangle = [
        [dataCardParameters['pdfSize'][0] - edgeLength - offsetRight,
            dataCardParameters['pdfSize'][1] - offsetTop],
        [dataCardParameters['pdfSize'][0] - offsetRight, dataCardParameters['pdfSize'][1] - offsetTop],
        [dataCardParameters['pdfSize'][0] - (edgeLength/2) - offsetRight,
         dataCardParameters['pdfSize'][1] - offsetTop - edgeLength]
    ]

    pdf.setStrokeColorRGB(dataCardParameters['lineColor'][0],
                          dataCardParameters['lineColor'][1], dataCardParameters['lineColor'][2])
    if (unitImage != None):
        pdf.drawImage(utils.ImageReader(imageBuffer), dataCardParameters['pdfSize'][0] - offsetRight - edgeLength,
                      dataCardParameters['pdfSize'][1] - offsetTop - edgeLength, edgeLength, edgeLength, mask=[0, 0, 255, 255, 0, 0])
        fillPath = 0
    else:
        fillPath = 1
    path = pdf.beginPath()
    path.moveTo(triangle[0][0], triangle[0][1])
    path.lineTo(triangle[1][0], triangle[1][1])
    path.lineTo(triangle[2][0], triangle[2][1])
    path.close()
    pdf.setLineJoin(1)
    pdf.setFillColorRGB(0.7, 0.7, 0.7)
    pdf.drawPath(path, stroke=1, fill=fillPath)


def dataCardUnitName(pdf, dataCardParameters, unit):
    # Unit Name
    parts = unit['name'].split(" ")
    nameLines = []
    maxLineChars = 25
    lineParts = []
    for part in parts:
        if len(" ".join(lineParts)) + len(part) > maxLineChars:
            nameLines.append(" ".join(lineParts))
            lineParts = []
        lineParts.append(part)
    nameLines.append(" ".join(lineParts))

    pdf.setFont('bold', 14)
    pdf.setFillColorRGB(0, 0, 0)
    offset = 0
    for line in nameLines:
        pdf.drawString(5, dataCardParameters['pdfSize'][1] - 25 - offset, line)
        offset += 12


def dataCardUnitSkills(pdf, dataCardParameters, unit):
    startX = dataCardParameters['pdfSize'][0] - 25
    startY = dataCardParameters['pdfSize'][1] - 21
    lineHight = 8
    pdf.setFont('bold', 8)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawCentredString(startX, startY, "Quality")
    pdf.drawCentredString(startX, startY - (lineHight*2), "Defense")
    pdf.setFont('regular', 8)
    pdf.drawCentredString(startX, startY - (lineHight*1), str(unit["quality"]) + "+")
    pdf.drawCentredString(startX, startY - (lineHight*3), str(unit["defense"]) + "+")


def dataCardUnitWeaponsEquipment(pdf, dataCardParameters, unit):
    # Weapon
    startX = 5
    startY = dataCardParameters['pdfSize'][1] - 75
    offsetX = [0, 130, 155, 180, 200]
    offsetY = 0
    headers = ['Weapon', 'RNG', 'ATT', 'AP', 'Special rules']
    for i in range(len(headers)):
        pdf.setFont("bold", 9)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawString(startX + offsetX[i], startY + offsetY, headers[i])
    offsetY -= 10

    for weapon in unit['weapons']:
        pdf.setFont("regular", 9)
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

        offsetY -= 10

    if 'equipment' in unit and len(unit['equipment']) > 0:
        offsetY -= 2

        pdf.setFont("bold", 9)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawString(startX + offsetX[0], startY + offsetY, "Upgrades")
        offsetY -= 10

        for equipment in unit['equipment']:
            pdf.setFont("regular", 9)
            pdf.setFillColorRGB(0, 0, 0)
            pdf.drawString(startX + offsetX[0], startY + offsetY, equipment['name'])
            label = []
            for specialRule in equipment['specialRules']:
                label.append(str(specialRule['label']))

            pdf.drawString(startX + offsetX[4], startY + offsetY, ", ".join(label))
            offsetY -= 10


def unitOverview(pdf, dataCardParameters, army):
    startX = dataCardParameters['sideClearance'] + 2
    startY = dataCardParameters['pdfSize'][1] - dataCardParameters['topClearance'] - 7
    offsetY = 0
    fontSize = 7

    lines = []
    for unit in army['units']:
        if ('type' not in unit):
            unitInfo = unit['name']
        elif (unit['type'] != unit['name']):
            unitInfo = unit['name'] + " (" + unit['type'] + ")"
        else:
            unitInfo = unit['type']

        unitInfo += " [" + str(unit['size']) + "]"
        unitInfo += " -" + str(getUnitCost(unit)) + " pts"
        lines.append(unitInfo)

    pdf.setFont("bold", fontSize)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(startX, startY + offsetY, army['listName'] +
                   " [" + army['armyName'] + "] - " + str(army['listPoints']) + " pts")
    offsetY -= 15

    for line in lines:
        pdf.setFont("regular", fontSize)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawString(startX, startY + offsetY, line)
        offsetY -= 10
        if startY + offsetY < dataCardParameters['bottomClearance']:
            dataCardBoarderFrame(pdf, dataCardParameters)
            pdf.showPage()
            offsetY = 0

    dataCardBoarderFrame(pdf, dataCardParameters)
    pdf.showPage()


def dataCardRuleInfo(pdf, dataCardParameters, army):
    rules = []
    for unit in army['units']:
        for rule in unit['rules']:
            rules.append(rule['name'])

        for weapon in unit['weapons']:
            if 'specialRules' in weapon:
                for rule in weapon['specialRules']:
                    rules.append(rule['name'])

        if 'equipment' in unit:
            for equipment in unit['equipment']:
                for rule in equipment['specialRules']:
                    rules.append(rule['name'])
    rules = list(dict.fromkeys(rules))
    spells = False
    ruleDescriptions = []
    downloadCommonRules(army['gameSystemId'])
    commonRules = loadJsonFile(os.path.join(DATAFOLDERARMYBOOK, "common-rules_" + str(army['gameSystemId']) + ".json"))
    for rule in rules:
        for common in commonRules['rules']:
            if common['name'].lower() == rule.lower():
                ruleDescriptions.append({'name': common['name'], 'description': common['description']})
                if common['name'].lower() == "psychic":
                    spells = True

    if 'armyId' in army:
        armyRules = loadJsonFile(os.path.join(
            DATAFOLDERARMYBOOK, army['armyId'] + "_" + str(army['gameSystemId']) + ".json"))
        for rule in rules:
            for armyRule in armyRules['specialRules']:
                if armyRule['name'].lower() == rule.lower():
                    ruleDescriptions.append({'name': armyRule['name'], 'description': armyRule['description']})
                    if armyRule['name'].lower() == "psychic":
                        spells = True

        if spells == True:
            ruleDescriptions.append({'name': "Spells", 'description': ''})
            for spell in armyRules['spells']:
                ruleDescriptions.append({'name': spell['name'], 'description': str(
                    spell['threshold']) + '+ ' + spell['effect']})

    dataCardBoarderFrame(pdf, dataCardParameters)

    startX = dataCardParameters['sideClearance'] + 2
    startY = dataCardParameters['pdfSize'][1] - dataCardParameters['topClearance'] - 7
    offsetY = 0
    fontSize = 7
    for rule in ruleDescriptions:
        offsetXName = pdf.stringWidth(rule['name'] + ": ", "bold", fontSize)

        parts = rule['description'].split(" ")
        lines = []
        lineParts = []
        offsetXCalc = offsetXName
        for part in parts:
            if startX + offsetXCalc + pdf.stringWidth(" ".join(lineParts), "regular", fontSize) + pdf.stringWidth(" ".join(part), "regular", fontSize) > dataCardParameters['pdfSize'][0] - dataCardParameters['sideClearance']:
                lines.append(" ".join(lineParts))
                lineParts = []
                offsetXCalc = 0
            lineParts.append(part)
        lines.append(" ".join(lineParts))

        if startY - (len(lines)*fontSize) + offsetY < dataCardParameters['bottomClearance']:
            pdf.showPage()
            dataCardBoarderFrame(pdf, dataCardParameters)
            offsetY = 0

        # Name
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("bold", fontSize)
        pdf.drawString(startX, startY + offsetY, rule['name'] + ": ")

        # Description
        pdf.setFont("regular", fontSize)
        pdf.setFillColorRGB(0, 0, 0)
        for line in lines:
            pdf.drawString(startX + offsetXName, startY + offsetY, line)
            offsetY -= fontSize
            offsetXName = 0
        offsetY -= 3
    pdf.showPage()


def getPdfFileName(armyName):
    pdfName = re.sub(r'(?is)([^\w])', '_', armyName.lower())
    pdfName = re.sub(r'(?is)(_+)', '_', pdfName)
    pdfFile = os.path.join(DATACARDFOLDER, pdfName)

    if os.path.exists(pdfFile + ".pdf"):
        nr = 1
        while (os.path.exists(pdfFile + "_" + str(nr) + ".pdf")):
            nr += 1
        pdfFile = pdfFile + "_" + str(nr)
    return pdfFile + ".pdf"


def createDataCard(army):
    print("Create datacards ...")
    try:
        pdfmetrics.registerFont(TTFont('bold', os.path.join(
            FONTFOLDER, "rosa-sans", "hinted-RosaSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont('regular', os.path.join(
            FONTFOLDER, "rosa-sans", "hinted-RosaSans-Regular.ttf")))
    except Exception as ex:
        print("Font is missing!")
        print(ex)
        waitForKeyPressAndExit()

    dataCardParameters = {
        'pdfSize': (300.0, 200.0),
        'lineColor': [1.00, 0.55, 0.10],
        'topClearance': 10,
        'bottomClearance': 10,
        'sideClearance': 2,
    }

    # creating a pdf object
    pdfFile = getPdfFileName(army['listName'])
    pdf = canvas.Canvas(pdfFile, pagesize=dataCardParameters['pdfSize'])
    pdf.setTitle("GDF data card")

    for unit in army['units']:
        print("  ", unit['name'], "(", unit['id'], ")")
        dataCardBoarderFrame(pdf, dataCardParameters)
        dataCardUnitType(pdf, dataCardParameters, unit)
        dataCardUnitWounds(pdf, dataCardParameters, unit, army)
        dataCardUnitRules(pdf, dataCardParameters, unit)
        dataCardUnitPoints(pdf, dataCardParameters, unit)
        dataCardUnitImage(pdf, dataCardParameters, unit, army['listName'], army['armyName'])
        dataCardUnitName(pdf, dataCardParameters, unit)
        dataCardUnitSkills(pdf, dataCardParameters, unit)
        dataCardUnitWeaponsEquipment(pdf, dataCardParameters, unit)

        pdf.showPage()
    dataCardRuleInfo(pdf, dataCardParameters, army)
    unitOverview(pdf, dataCardParameters, army)

    try:
        pdf.save()
        return pdfFile
    except Exception as ex:
        print("Error PDF save failed")
        print(str(ex))
        return None


def getTxtSpecialRule(txt):
    rule = {}
    rule['label'] = txt

    if "(" in txt:
        data = txt.split("(")
        rule['key'] = data[0].lower()
        rule['name'] = data[0]
        rule['rating'] = re.sub(r'(?is)([^\d])', '', data[1])
    else:
        rule['key'] = txt.lower()
        rule['name'] = txt
    return rule


def getRulesFromTxt(data):
    parts = list(data.strip(" "))
    rules = []
    extract = []
    bracket = 0
    for i in range(len(parts)):
        if (parts[i] == "("):
            bracket += 1
        elif (parts[i] == ")"):
            bracket -= 1
        if ((parts[i] == "," and bracket == 0) or i == len(parts) - 1):
            if i == len(parts) - 1:
                extract.append(parts[i])
            rules.append(''.join(extract).strip())
            extract = []
        else:
            extract.append(parts[i])

    return rules


def parseArmyTextList(armyListText):
    armyData = {}

    length = len(armyListText[0])
    if (length > 6 and armyListText[0][0] == "+" and armyListText[0][1] == "+" and armyListText[0][2] == " " and armyListText[0][length - 3] == " " and armyListText[0][length - 2] == "+" and armyListText[0][length - 1] == "+"):
        armyData['parser'] = "txt"

        data = armyListText[0].rstrip(" ++").lstrip("++ ").split("[")
        tmp = data[0].strip().split("-")
        armyData['armyName'] = tmp[len(tmp) - 1].strip()
        tmp.pop(len(tmp) - 1)
        armyData['listName'] = "-".join(tmp).strip()

        data = data[1].split(" ")
        armyData['gameSystem'] = data[0].lower()
        armyData['gameSystemId'] = getGameSystemId(armyData['gameSystem'])
        armyData['listPoints'] = int(re.sub(r'(?is)([^\d])', '', data[1]))
    else:
        print("Error no valid army data found!")
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
                unitData['cost'] = re.sub(r'[^\d]', '', data[1].strip(" "), )
                unitData['specialRules'] = []
                unitData['equipment'] = []
                unitData['id'] = f'{x}'
                rules = getRulesFromTxt(data[2])
                for rule in rules:
                    if re.search(r'(?is)\([A-Z]+', rule.strip()):
                        regExMatch = re.search(r"(?is)(\dx)?([^(]+)(\()(.*)(\))", rule.strip(" "))
                        equipment = {}
                        equipment['name'] = regExMatch.group(2).strip()
                        equipment['specialRules'] = []
                        for equipmentRule in regExMatch.group(4).split(","):
                            equipment['specialRules'].append(getTxtSpecialRule(equipmentRule))
                        unitData['equipment'].append(equipment)
                    else:
                        unitData['specialRules'].append(getTxtSpecialRule(rule))
                regExMatch = re.findall(
                    r"(?P<name>.*)\s\[(?P<unitCount>\d+)\]\sQ(?P<quality>\d+)\+\sD(?P<defense>\d+)\+$", data[0].strip(" "))
                unitData['name'] = regExMatch[0][0]
                unitData['type'] = ""
                unitData['size'] = int(regExMatch[0][1])
                unitData['quality'] = int(regExMatch[0][2])
                unitData['defense'] = int(regExMatch[0][3])
            elif unit == True:
                weapons = getRulesFromTxt(armyListText[x].strip(" "))

                for weapon in weapons:
                    regExMatch = re.search(
                        r"(\d+x)?([^(]+)(\()(.*)(\))", weapon.strip(" "))
                    weaponData = {}
                    weaponData['name'] = regExMatch.group(2).strip()
                    weaponData['count'] = regExMatch.group(1)
                    if weaponData['count'] == None:
                        weaponData['count'] = 1
                    else:
                        weaponData['count'] = int(weaponData['count'].replace("x", ""))

                    weaponRules = regExMatch.group(4).split(",")
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
                            weaponData['specialRules'].append(getTxtSpecialRule(weaponRule))
                    if not "weapons" in unitData:
                        unitData['weapons'] = []
                    unitData['weapons'].append(weaponData)
        else:
            unit = False
            if "name" in unitData:
                armyData['units'].append(unitData)
            unitData = {}
    return armyData


def getUnit(unit, jsonArmyBookList):
    if DEBUG == True:
        print("    Func: getUnit")
    data = {}
    for listUnit in jsonArmyBookList[unit['armyId']]['units']:
        if (listUnit['id'] == unit['id']):
            data['type'] = listUnit['name']
            data['name'] = listUnit['name']
            data['armyId'] = unit['armyId']
            data['id'] = listUnit['id']
            data['cost'] = listUnit['cost']
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

            data['rules'] = getRules(listUnit['rules'])
            data = getUnitUpgrades(unit, data, jsonArmyBookList)
            break
    if "customName" in unit:
        data['name'] = unit['customName']

    return data


def getRules(data):
    if DEBUG == True:
        print(f'    Func: getRules')
    rules = []
    for specialRule in data:
        if DEBUG == True:
            print(f'      {specialRule["name"]}')

        rule = specialRule
        if 'rating' in specialRule and specialRule['rating'] != '':
            rule['label'] = specialRule['name'] + \
                "(" + str(specialRule['rating']) + ")"
        else:
            rule['label'] = specialRule['name']

        rules.append(rule)

    return rules


def getWeapon(data, modCount=-1):
    if DEBUG == True:
        print(f'    Func: getWeapon {data["name"]}')

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
        if weapon['specialRules'][i]['name'].lower() == "ap":
            weapon['ap'] = weapon['specialRules'][i]['rating']
            weapon['specialRules'].pop(i)
            break

    return weapon


def removeWeapon(removeWeapon, count: int, weapons):
    if DEBUG == True:
        print("    Func: removeWeapon", removeWeapon)
    for remove in removeWeapon:
        for i in range(len(weapons)):
            remove = remove.strip()
            group = [remove, remove + "s", remove[:-1]]
            if re.match(r'^(' + "|".join(group) + ')$', weapons[i]['name'].strip()):
                if (count == "any" or count == None or weapons[i]['count'] == 1):
                    weapons.pop(i)
                else:
                    weapons[i]['count'] -= count
                    if weapons[i]['count'] <= 0:
                        weapons.pop(i)
                break
    return weapons


def getUnitUpgrades(unit, unitData, jsonArmyBookList):
    if DEBUG == True:
        print("    Func: getUnitUpgrades")

    for upgrade in unit['selectedUpgrades']:
        armyId = unit['armyId']
        upgradeId = upgrade['upgradeId']
        optionId = upgrade['optionId']

        if DEBUG:
            print(f'      upgradeId: {upgradeId}')

        for package in jsonArmyBookList[armyId]['upgradePackages']:
            for section in package['sections']:
                variant = None
                affects = None
                targets = None
                if "variant" in section:
                    variant = section['variant']
                if "affects" in section:
                    affects = section['affects']
                if "targets" in section:
                    targets = section['targets']

                if (section['uid'] == upgradeId):
                    for option in section['options']:
                        if option['uid'] == optionId:

                            if ('upgradeCost' not in unitData):
                                unitData['upgradeCost'] = []
                            unitData['upgradeCost'].append(option['cost'])

                            for gains in option['gains']:
                                if (gains['type'] == "ArmyBookWeapon"):
                                    if variant in ("upgrade", "replace") and affects and affects['type'] == "all":
                                        modeCount = unitData['size']
                                    else:
                                        modeCount = -1
                                    unitData['weapons'].append(getWeapon(gains, modeCount))
                                elif gains['type'] == "ArmyBookItem":
                                    if len(gains['content']) == 1:
                                        if 'equipment' not in unitData:
                                            unitData['equipment'] = []
                                        unitData['equipment'].append(addEquipment(gains))
                                    else:
                                        if 'equipment' not in unitData:
                                            unitData['equipment'] = []
                                        unitData['equipment'].append(addEquipment(gains, False))

                                        for gain in gains['content']:
                                            if gain['type'] == "ArmyBookItem":
                                                if 'equipment' not in unitData:
                                                    unitData['equipment'] = []
                                                unitData['equipment'].append(addEquipment(gains))
                                            elif gain['type'] == "ArmyBookWeapon":
                                                unitData['weapons'].append(getWeapon(gain,1))
                                            elif gain['type'] == "ArmyBookRule":
                                                unitData['specialRules'].append(getSpecialRules([gain])[0])
                                elif gains['type'] == "ArmyBookRule":
                                    unitData['specialRules'].append(getSpecialRules([gains])[0])
                                else:
                                    print("Error no handling for " +
                                          gains['type'] + " upgradeId " + upgradeId + " optionId " + optionId)

                            if variant == "replace":
                                if (gains['type'] == "ArmyBookWeapon" or gains['type'] == "ArmyBookItem"):
                                    if affects and affects['type'] == "any":
                                        # Not sure, but by Desolator Squad HE-Launchers missing during upgrade uNapO (Replace any HE-Launcher), workarround set affects to 1
                                        affectsValue = 1
                                    elif affects and affects['type'] == "exactly":
                                        affectsValue = affects['value']
                                    elif affects and affects['type'] == "all":
                                        affectsValue = None
                                    elif affects is None:
                                        affectsValue = 999

                                    if unitData['size'] > 1:
                                        unitData['weapons'] = mergeWeapon(unitData['weapons'])

                                    unitData['weapons'] = removeWeapon(targets, affectsValue, unitData['weapons'])
                                else:
                                    print(f"Unhandelt type '{gains['type']}' in unit upgrades")

    return unitData


def mergeWeapon(weapons):
    if DEBUG == True:
        print("    Func: mergeWeapon")

    mergedWeapons = []
    for weapon in weapons:
        add = True
        for added in mergedWeapons:
            if added['name'] == weapon['name'] and added['attacks'] == weapon['attacks']:
                if 'ap' not in added or 'ap' in added and added['ap'] == weapon['ap']:
                    added['count'] += weapon['count']
                    add = False
                    break

        if (add == True):
            mergedWeapons.append(weapon)
    return mergedWeapons


def addEquipment(data, specialRules = True):
    equipment = {}
    equipment['name'] = data['name']
    if specialRules == True:
        equipment['specialRules'] = getSpecialRules(data['content'])
    else:
        equipment['specialRules'] = []

    return equipment


def parseArmyJsonList(armyListJsonFile: str, validateVersion=True):
    print("Parse army list ...")
    armyData = {}
    jsonArmyBookList = {}

    jsonArmyList = loadJsonFile(armyListJsonFile)
    armyData['armyId'] = jsonArmyList['armyId']
    armyData['gameSystem'] = jsonArmyList['gameSystem']
    armyData['gameSystemId'] = getGameSystemId(jsonArmyList['gameSystem'])

    downloadArmyBook(armyData['armyId'], armyData['gameSystemId'])
    downloadCommonRules(armyData['gameSystemId'])

    jsonArmyBookList[armyData['armyId']] = loadJsonFile(os.path.join(
        DATAFOLDERARMYBOOK, armyData['armyId'] + "_" + str(armyData['gameSystemId']) + ".json"))
    armyData['armyName'] = jsonArmyBookList[armyData['armyId']]['name']
    armyData['listPoints'] = jsonArmyList['listPoints']
    armyData['listName'] = jsonArmyList['list']['name']

    versionCheck = checkArmyVersions(jsonArmyList, jsonArmyBookList[armyData['armyId']])
    if (validateVersion and not versionCheck):
        print("Army Book version from JSON is different than Army Book Version from OPR Server")
        waitForKeyPressAndExit()

    armyData['units'] = []
    for unit in jsonArmyList['list']['units']:
        print(f'  Unit ID: {unit["id"]}')
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
        waitForKeyPressAndExit()

    try:
        jsonObj = json.loads(file)
    except json.decoder.JSONDecodeError as ex:
        print(file + " Json is not valid!")
        print(ex)
        waitForKeyPressAndExit()
    except Exception as ex:
        print("Unhandeld Exception")
        print(ex)
        waitForKeyPressAndExit()
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
    print("Check/download army book ...")
    armyBookJsonFile = os.path.join(DATAFOLDERARMYBOOK, str(id) + "_" + str(gameSystemId) + ".json")
    url = f'https://army-forge.onepagerules.com/api/army-books/{id}?gameSystem={gameSystemId}'

    return downloadJson(url, armyBookJsonFile)


def downloadCommonRules(gameSystemId):
    print("Check/download common rules ...")
    armyBookJsonFile = os.path.join(DATAFOLDERARMYBOOK, "common-rules_" + str(gameSystemId) + ".json")
    url = f'https://army-forge.onepagerules.com/api/rules/common/{gameSystemId}'
    return downloadJson(url, armyBookJsonFile)


def downloadJson(url, file):
    # download only when older than 1 day
    download = True
    if os.path.exists(file):
        if time.time() - os.stat(file)[stat.ST_MTIME] < 86400:
            download = False

    if (download == True):
        try:
            print("Download file")
            urllib.request.urlretrieve(url, file)
        except Exception as ex:
            print("Error failed")
            print(ex)
            return False

    if not os.path.exists(file):
        print("No json data found " + id)
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


def checkFonts():
    font1 = os.path.join(FONTFOLDER, "rosa-sans", "hinted-RosaSans-Bold.ttf")
    font2 = os.path.join(FONTFOLDER, "rosa-sans", "hinted-RosaSans-Regular.ttf")

    if not os.path.exists(font1) or not os.path.exists(font2):
        print("Download font ...")

        url = "https://raw.githubusercontent.com/JackGruber/OPRDataCards/master/rosa-sans.zip"
        zipFile = os.path.join(FONTFOLDER, "rosa-sans.zip")
        if downloadFile(url, zipFile) == True:
            print("Unzip fonts ...")
            with zipfile.ZipFile(zipFile, 'r') as zipRef:
                zipRef.extractall(os.path.join(FONTFOLDER, "rosa-sans"))


def downloadFile(url, dstFile):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(dstFile, "wb") as file:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            return True
        else:
            print("Error font download failed")
            return False
    except Exception as ex:
        print("Error font download failed")
        print(ex)
        return False

def checkArmyVersions(armyJson, armyBookJson):
    try:
        armyVersion = armyJson["armyVersions"][0]["version"]
        bookVersion = armyBookJson["versionString"]
    except Exception as ex:
        print("Error on checkArmyVersions")
        print(ex)
        return False
    
    if str(armyVersion) == str(bookVersion):
        return True
    else:
        print(f"Error: Army version {armyVersion} don't match ArmyBook version {bookVersion}")
        return False

def waitForKeyPressAndExit():
    input("Press Enter to continue...")
    sys.exit(1)

if __name__ == "__main__":
    Main()
