import os
import sys
import json
import testhelper

sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8


def test_parseArmyTextList():
    armyList = readArmyTxt(os.path.join(testhelper.TESTDATADIR, 'txt_army.txt'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'txt_army_expected.json'))
    result = OPRDatacard.parseArmyTextList(armyList)
    assert result == expected, "Parsed Armylist is wrong"


def readArmyTxt(file):
    try:
        f = open(os.path.join(testhelper.TESTDIR, file), "r")
        armyList = f.read().split("\n")
        f.close()
    except Exception as ex:
        assert False, "Error Reading test txt file " + str(ex)

    return armyList
