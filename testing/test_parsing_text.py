import os
import sys
import json
TESTDIR = os.path.dirname(__file__)
sys.path.append(os.path.join(TESTDIR, '..'))
import OPRDatacard  # nopep8


def test_parseArmyTextList():
    armyList = readArmyTxt("gff_army.txt")
    expected = readJsonFile('gff_army_expected.json')
    result = OPRDatacard.parseArmyTextList(armyList)
    assert result == expected, "Parsed Armylist is wrong"


def readArmyTxt(file):
    try:
        f = open(os.path.join(TESTDIR, file), "r")
        armyList = f.read().split("\n")
        f.close()
    except Exception as ex:
        assert False, "Error Reading test txt file " + str(ex)

    return armyList


def readJsonFile(file):
    try:
        f = open(os.path.join(TESTDIR, file), "r")
        expected = json.loads(f.read())
        f.close()
    except Exception as ex:
        assert False, "Error Reading test result file " + str(ex)

    return expected
