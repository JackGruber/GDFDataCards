import os
import sys


TESTDIR = os.path.dirname(__file__)
sys.path.append(os.path.join(TESTDIR, '..'))
import OPRDatacard  # nopep8


def test_Ok():
    OPRDatacard.DATAFOLDERARMYBOOK = os.path.join(TESTDIR, 'tmp', 'data')
    result = OPRDatacard.downloadArmyBook("z65fgu0l29i4lnlu")
    assert result == True


def test_Error():
    OPRDatacard.DATAFOLDERARMYBOOK = os.path.join(TESTDIR, 'tmp', 'data')
    result = OPRDatacard.downloadArmyBook("no")
    assert result == False
