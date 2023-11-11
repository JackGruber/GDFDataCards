import os
import sys
import testhelper
from click.testing import CliRunner
from unittest.mock import patch

sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8


def test_noParameterJsonSelected():
    with (
        patch('OPRDatacard.createStructure') as mock_createStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units': ["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="file.json") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main)
        assert mock_createStructure.called
        assert mock_fileSelectDialog.called
        assert mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert not mock_parseArmyTextList.called
        assert result.exit_code == 0, "Exit error"


def test_forceJson():
    with (
        patch('OPRDatacard.createStructure') as mock_createStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units': ["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="file.???") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ['--json'])
        assert mock_createStructure.called
        assert mock_fileSelectDialog.called
        assert mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert not mock_parseArmyTextList.called
        assert result.exit_code == 0, "Exit error"


def test_noParameterTxtSelected():
    with (
        patch('OPRDatacard.createStructure') as mock_createStructure,
        patch('OPRDatacard.parseArmyJsonList') as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="file.txt") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.readTxtFile') as mock_readTxtFile,
        patch('OPRDatacard.parseArmyTextList', return_value={'units': ["data"]}) as mock_parseArmyTextList,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main)
        assert mock_createStructure.called
        assert mock_fileSelectDialog.called
        assert not mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert mock_readTxtFile.called
        assert mock_parseArmyTextList.called
        assert result.exit_code == 0, "Exit error"


def test_FileJson():
    with (
        patch('OPRDatacard.createStructure') as mock_createStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units': ["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog') as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ["-f", "file.json"])
        assert mock_createStructure.called
        assert not mock_fileSelectDialog.called
        assert mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert not mock_parseArmyTextList.called
        assert result.exit_code == 0, "Exit error"


def test_FileDataForceJson():
    with (
        patch('OPRDatacard.createStructure') as mock_createStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units': ["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog') as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ["-f", "file.data", "--json"])
        assert mock_createStructure.called
        assert not mock_fileSelectDialog.called
        assert mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert not mock_parseArmyTextList.called
        assert result.exit_code == 0, "Exit error"


def test_FileTxt():
    with (
        patch('OPRDatacard.createStructure') as mock_createStructure,
        patch('OPRDatacard.parseArmyJsonList') as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog') as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.readTxtFile') as mock_readTxtFile,
        patch('OPRDatacard.parseArmyTextList', return_value={'units': ["data"]}) as mock_parseArmyTextList,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ["-f", "file.txt"])
        assert mock_createStructure.called
        assert not mock_fileSelectDialog.called
        assert not mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert mock_readTxtFile.called
        assert mock_parseArmyTextList.called
        assert result.exit_code == 0, "Exit error"
