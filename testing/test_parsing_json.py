import os
import sys
import json
import testhelper

sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8

armyBookHdf = testhelper.readJsonFile(os.path.join(testhelper.TESTDIR, 'armybook_hdf.json'))


def test_addEquipment():
    upgrade = armyBookHdf["upgradePackages"][2]["sections"][0]["options"][3]

    result = OPRDatacard.addEquipment(upgrade['gains'][0])
    expected = {'name': 'Forward Observer', 'specialRules': ['Take Aim']}
    assert result == expected


def test_getSpecialRules_Weapons():
    testCases = [
        {'unit': 0, 'equipment': 1, 'expected': []},
        {'unit': 1, 'equipment': 1, 'expected': [
            {'key': 'ap', 'name': 'AP', 'rating': '1', 'modify': False, 'label': 'AP(1)'}]},
        {'unit': 8, 'equipment': 1, 'expected': [{'key': 'blast', 'name': 'Blast', 'rating': '3', 'modify': False, 'label': 'Blast(3)'}, {
            'key': 'indirect', 'name': 'Indirect', 'rating': '', 'modify': False, 'label': 'Indirect'}]},
    ]
    for test in testCases:
        rules = armyBookHdf["units"][test['unit']]["equipment"][test['equipment']]['specialRules']
        result = OPRDatacard.getSpecialRules(rules)
        print(result)
        assert result == test['expected'], "Test for unit " + str(test['unit']) + " equipment " + str(test['equipment'])


def test_getWeapon():
    testCases = [
        {'unit': 0, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Rifle', 'range': 24, 'specialRules': []}},
        {'unit': 1, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Heavy Rifle', 'range': 24, 'specialRules': [], 'ap': '1'}},
        {'unit': 4, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Plasma Rifle', 'range': 24, 'specialRules': [], 'ap': '4'}},
        {'unit': 8, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Mortar', 'range': 30, 'specialRules': [
            {'key': 'blast', 'name': 'Blast', 'rating': '3', 'modify': False, 'label': 'Blast(3)'}, {'key': 'indirect', 'name': 'Indirect', 'rating': '', 'modify': False, 'label': 'Indirect'}]}},
        {'unit': 9, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Sniper Rifle', 'range': 30, 'specialRules': [
            {'key': 'sniper', 'name': 'Sniper', 'rating': '', 'modify': False, 'label': 'Sniper'}], 'ap': '1'}},
        {'unit': 10, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Mini GL', 'range': 18, 'specialRules': [
            {'key': 'blast', 'name': 'Blast', 'rating': '3', 'modify': False, 'label': 'Blast(3)'}]}},
    ]

    for test in testCases:
        weapon = armyBookHdf["units"][test['unit']]["equipment"][test['equipment']]
        result = OPRDatacard.getWeapon(weapon)
        assert result == test['expected'], "Test for unit " + str(test['unit']) + " equipment " + str(test['equipment'])


def test_removeWeapon():
    weapons = [{'name': 'CCW'}, {'name': 'Heavy Rifle'}, {'name': 'Heavy Pistol'}, {'name': 'CCW'}]
    testCases = [
        {'remove': [], 'expected': [{'name': 'CCW'}, {'name': 'Heavy Rifle'}, {'name': 'Heavy Pistol'}, {'name': 'CCW'}]},
        {'remove': ['CCW'], 'expected': [{'name': 'Heavy Rifle'}, {'name': 'Heavy Pistol'}, {'name': 'CCW'}]},
        {'remove': ['Heavy Pistol'], 'expected': [{'name': 'CCW'}, {'name': 'Heavy Rifle'}, {'name': 'CCW'}]},
        {'remove': ['Some'], 'expected': [{'name': 'CCW'}, {
            'name': 'Heavy Rifle'}, {'name': 'Heavy Pistol'}, {'name': 'CCW'}]},
        {'remove': ['CCW', 'Heavy Rifle'], 'expected': [{'name': 'Heavy Pistol'}, {'name': 'CCW'}]},
        {'remove': ['CCW', 'CCW'], 'expected': [{'name': 'Heavy Rifle'}, {'name': 'Heavy Pistol'}]},
    ]

    for test in testCases:
        result = OPRDatacard.removeWeapon(test['remove'], weapons.copy())
        print(result)
        assert result == test['expected'], "Weapon remove error for: " + ", ". join(test['remove'])


def test_getUnitUpgrades():
    book = {}
    book['TestArmyId'] = armyBookHdf
    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": []}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'weapons': []}, book)
    assert result == {'weapons': []}, "No upgrades"

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": [
        {"instanceId": "oM5IcF6CY", "upgradeId": "biu0sem", "optionId": "uG08OTq"}]}
    expected = {'weapons': [{'attacks': 1, 'name': 'Heavy Pistol', 'range': 12, 'specialRules': [], 'ap': '1'}]}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'weapons': []}, book)
    assert result == expected, "Upgrade Heavy Pistol"

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": [
        {"instanceId": "oM5IcF6CY", "upgradeId": "biu0sem", "optionId": "uG08OTq"}, {"instanceId": "QrSaPfNsR", "upgradeId": "KLO_Oyg", "optionId": "8TLlvtc"}, {"instanceId": "29BbXH9Me", "upgradeId": "r5XpHsA", "optionId": "8reDsp0"}]}
    expected = {'weapons': [{'attacks': 1, 'name': 'Plasma Pistol', 'range': 12, 'specialRules': [
    ], 'ap': '4'}], 'equipment': [{'name': 'Forward Observer', 'specialRules': ['Take Aim']}]}

    result = OPRDatacard.getUnitUpgrades(unitFromList, {'weapons': []}, book)
    assert result == expected, "3 Upgrades to (Heavy Pistol, than to Plasma and Take Aim)"


def test_getUnit():
    book = {}
    book['TestArmyId'] = armyBookHdf

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": []}
    result = OPRDatacard.getUnit(unitFromList, book)
    assert result['type'] == 'Storm Leader'
    assert result['name'] == 'Storm Leader'
    assert result['defense'] == 4
    assert result['quality'] == 4
    assert len(result['weapons']) == 2
    assert len(result['specialRules']) == 3
    assert len(result['specialRules']) == 3
