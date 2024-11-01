import os
import sys
import testhelper


sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8


def test_Ok():
    OPRDatacard.DATAFOLDERARMYBOOK = os.path.join(testhelper.TESTDIR, 'tmp', 'data')
    OPRDatacard.set_settings(False, True, False)
    result = OPRDatacard.downloadArmyBook("7oi8zeiqfamiur21", 3)
    assert result == True


def test_Error():
    OPRDatacard.DATAFOLDERARMYBOOK = os.path.join(testhelper.TESTDIR, 'tmp', 'data')
    OPRDatacard.set_settings(False, True, False)
    result = OPRDatacard.downloadArmyBook("no", 3)
    assert result == False
