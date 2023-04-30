import os
import sys
import pytest
import json
import importlib
TESTDIR = os.path.dirname(__file__)
sys.path.append(os.path.join(TESTDIR, '..'))
import OPRDatacard  # nopep8


def test_parseArmyTextList():

    try:
        f = open(os.path.join(TESTDIR, 'gff_army.txt'), "r")
        armyList = f.read().split("\n")
        f.close()
    except Exception as ex:
        assert False, "Error Reading test txt file " + str(ex)

    try:
        f = open(os.path.join(TESTDIR, 'gff_army_expected.json'), "r")
        expected = json.loads(f.read())
        f.close()
    except Exception as ex:
        assert False, "Error Reading test result file " + str(ex)

    result = OPRDatacard.parseArmyTextList(armyList)

    assert result == expected, "Parsed Armylist is wrong"
