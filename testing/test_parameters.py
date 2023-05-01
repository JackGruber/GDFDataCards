import os
import sys
import testhelper
from click.testing import CliRunner
from unittest.mock import patch

sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8

def test_json():
    with (
        patch('OPRDatacard.createFolderStructure') as mock_createFolderStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units':["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="somepath") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
        patch('OPRDatacard.readMultipleLines') as mock_readMultipleLines,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ['--json'])
        assert mock_createFolderStructure.called
        assert mock_fileSelectDialog.called
        assert mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert not mock_parseArmyTextList.called
        assert not mock_readMultipleLines.called
        assert result.exit_code == 0, "Exit error"

def test_json_file():
    with (
        patch('OPRDatacard.createFolderStructure') as mock_createFolderStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units':["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="somepath") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
        patch('OPRDatacard.readMultipleLines') as mock_readMultipleLines,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ['--json', '-f' , 'somefile'])
        assert mock_createFolderStructure.called
        assert not mock_fileSelectDialog.called
        assert mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert not mock_parseArmyTextList.called
        assert not mock_readMultipleLines.called
        assert result.exit_code == 0, "Exit error"

def test_txt():
    with (
        patch('OPRDatacard.createFolderStructure') as mock_createFolderStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units':["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="somepath") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
        patch('OPRDatacard.readMultipleLines') as mock_readMultipleLines,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ['--txt'])
        assert mock_createFolderStructure.called
        assert not mock_fileSelectDialog.called
        assert not mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert mock_parseArmyTextList.called
        assert mock_readMultipleLines.called
        assert result.exit_code == 0, "Exit error"

def test_json_file():
    with (
        patch('OPRDatacard.createFolderStructure') as mock_createFolderStructure,
        patch('OPRDatacard.parseArmyJsonList', return_value={'units':["data"]}) as mock_parseArmyJsonList,
        patch('OPRDatacard.fileSelectDialog', return_value="somepath") as mock_fileSelectDialog,
        patch('OPRDatacard.createDataCard') as mock_createDataCard,
        patch('OPRDatacard.openFile') as mock_openFile,
        patch('OPRDatacard.parseArmyTextList') as mock_parseArmyTextList,
        patch('OPRDatacard.readMultipleLines') as mock_readMultipleLines,
        patch('OPRDatacard.readTxtFile') as mock_readTxtFile,
    ):
        runner = CliRunner()
        result = runner.invoke(OPRDatacard.Main, ['--txt', '-f' , 'somefile'])
        print(result.output)
        assert mock_createFolderStructure.called
        assert not mock_fileSelectDialog.called
        assert not mock_parseArmyJsonList.called
        assert mock_createDataCard.called
        assert mock_openFile.called
        assert mock_readTxtFile.called
        assert mock_parseArmyTextList.called
        assert not mock_readMultipleLines.called
        assert result.exit_code == 0, "Exit error"
