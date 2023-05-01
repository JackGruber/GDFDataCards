import os
import sys
import json

TESTDIR = os.path.dirname(__file__)


def readJsonFile(file):
    try:
        f = open(file, "r", encoding="utf8")
        expected = json.loads(f.read())
        f.close()
    except Exception as ex:
        assert False, "Error Reading test result file " + str(ex)

    return expected
