import os
import sys
import json
import testhelper

sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8

armyBookHdf = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'armybook_hdf_3.json'))


def test_addEquipment():
    upgrade = "Forward Observer"

    for upgradePackages in armyBookHdf["upgradePackages"]:
        for section in upgradePackages['sections']:
            for option in section['options']:
                if option['gains'][0]['name'].lower() == upgrade.lower():
                    gains = option['gains'][0]
                    break

    result = OPRDatacard.addEquipment(gains)
    expected = {'name': 'Forward Observer', 'specialRules': [{'id': 'KskX8qPX3I8G', 'name': 'Take Aim', 'type': 'ArmyBookRule', 'label': 'Take Aim'}]}

    assert result['name'] == "Forward Observer"
    assert len(result['specialRules']) == 1
    assert result == expected


def test_getSpecialRules_Weapons():
    testCases = [
        {'unit': 'Company Leader', 'weapon': 'Master Rifle', 
            'expected': []},
        {'unit': 'Storm Leader', 'weapon': 'Master Heavy Pistol', 
            'expected': [{'type': 'ArmyBookRule', 'id': '17crjK7P6_w6', 'name': 'AP', 'rating': 1, 'label': 'AP(1)'}]},
        {'unit': 'Sniper', 'weapon': 'Sniper Rifle', 
            'expected': [{'type': 'ArmyBookRule', 'id': '17crjK7P6_w6', 'name': 'AP', 'rating': 1, 'label': 'AP(1)'}, {'type': 'ArmyBookRule', 'id': 'Zx4mWN0SbmK8', 'name': 'Reliable', 'label': 'Reliable'}]},

    ]

    units = armyBookHdf["units"]
    
    for test in testCases:
        specialRules = None
        for unit in units:
            if unit['name'].lower() == test['unit'].lower():
                for weapon in unit['weapons']:
                    print(weapon['name'])
                    if weapon['name'].lower() == test['weapon'].lower():
                        if 'specialRules' in weapon:
                            specialRules = weapon['specialRules']
                            break
            if specialRules is not None:
                break
        if len(test['expected']) == 0:
            assert specialRules is None, "Test for unit " + str(test['unit']) + " weapon " + str(test['weapon'])
        else:
            assert specialRules is not None, "Test for unit " + str(test['unit']) + " weapon " + str(test['weapon'])
            result = OPRDatacard.getRules(specialRules)
            assert result == test['expected'], "Test for unit " + str(test['unit']) + " weapon " + str(test['weapon'])
        

def test_getWeapon():
    testCases = [
        {'unit': 'Company Leader', 'weapon': 'CCW', 
            'expected': {'attacks': 2, 'count': 1, 'name': 'CCW', 'specialRules': []}},
        {'unit': 'OGRE Robot', 'weapon': 'OGRE Gatling Gun', 
            'expected': {'attacks': 3, 'count': 1, 'name': 'OGRE Gatling Gun', 'range': 12, 'specialRules': [], 'ap': '1'}},
        {'unit': 'Sapper', 'weapon': 'Grenade Launcher', 
            'expected': {'attacks': 1, 'count': 1, 'name': 'Grenade Launcher', 'range': 24, 'specialRules': [{'type': 'ArmyBookRule', 'id': 'w_vX0mi58KKt', 'name': 'Blast', 'rating': 3, 'label': 'Blast(3)'}]}},
    ]

    units = armyBookHdf["units"]
    for test in testCases:
        weapon = None
        for unit in units:
            if unit['name'].lower() == test['unit'].lower():
                for equipment in unit['weapons']:
                    if equipment['name'].lower() == test['weapon'].lower():
                        weapon = equipment
                        break
            if weapon is not None:
                break
        
        assert weapon is not None, "Test for unit " + str(test['unit']) + " weapon " + str(test['weapon'])
        result = OPRDatacard.getWeapon(weapon)
        assert result == test['expected'], "Test for unit " + str(test['unit']) + " weapon " + str(test['weapon'])

def test_removeWeapon():
    weapons = [{'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
        'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}]
    testCases = [
        {'remove': [], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {'name': 'Heavy Pistol',
                                                                               'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['CCW'], 'count': 1, 'expected': [
            {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['Heavy Pistol'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['Some'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['CCW', 'Heavy Rifle'], 'count': 1, 'expected': [
            {'name': 'Heavy Pistol',
             'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['CCW', 'CCW'], 'count': 1, 'expected': [
            {'name': 'Heavy Rifle', 'count': 1},
            {'name': 'Heavy Pistol', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['Grenade'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 1}
        ]},
        {'remove': ['Grenade'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}
        ]},
        {'remove': ['Heavy Pistols', 'CCW'], 'count': 1, 'expected': [
            {'name': 'Heavy Rifle', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 1}
        ]},
    ]

    for test in testCases:
        result = OPRDatacard.removeWeapon(test['remove'], test['count'], weapons.copy())
        assert result == test['expected'], "Weapon remove error for: " + ", ". join(test['remove'])


def test_getUnitUpgrades():
    book = {}
    book['TestArmyId'] = armyBookHdf
    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": []}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'size': 1, 'weapons': []}, book)
    assert result == {'size': 1, 'weapons': []}, "No upgrades"

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": [{ "instanceId": "8E9g2SWmn", "upgradeId": "r5XpHsA", "optionId": "8reDsp0"},]}
    expected = {'size': 1, 'weapons': [], 'upgradeCost': [50], 'equipment': [{'name': 'Forward Observer', 'specialRules': [{'key': 'take aim', 'name': 'Take Aim', 'type': 'ArmyBookRule', 'label': 'Take Aim', 'modify': False, 'rating': ''}]}]}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'size': 1, 'weapons': []}, book)
    assert result == expected, "One Upgrade"

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": [
                    {"instanceId": "8E9g2SWmn","upgradeId": "r5XpHsA","optionId": "8reDsp0"},
                    {"instanceId": "rA1CrnoXB","upgradeId": "F8Om0","optionId": "6omIv"},
                    {"instanceId": "TAXwR2a7W","upgradeId": "O0U5OGl","optionId": "yKOK0P1"}]}
    expected = {'size': 1, 'weapons': [{'attacks': 2, 'count': 1, 'name': 'Energy Fist', 'specialRules': [], 'ap': 4}], 'upgradeCost': [50, 5, 15], 'equipment': [{'name': 'Forward Observer', 'specialRules': [{'key': 'take aim', 'name': 'Take Aim', 'type': 'ArmyBookRule', 'label': 'Take Aim', 'modify': False, 'rating': ''}]}, {'name': 'Heavy Armor', 'specialRules': [{'name': 'Defense', 'type': 'ArmyBookRule', 'label': 'Defense(1)', 'modify': True, 'rating': 1}]}]}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'size': 1, 'weapons': []}, book)
    assert result == expected, "3 Upgrades"


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


def test_unitWithManyUpgrades():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'gf_many_upgrades.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'gf_many_upgrades_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_hdf():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hdf.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hdf_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gf_pb():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gf_pb.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gf_pb_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_prime_brothers():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_prime_brothers.json'))
    expected = testhelper.readJsonFile(os.path.join(
        testhelper.TESTDATADIR, 'army_list_gff_prime_brothers_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_deudak_guard():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_feudal_guard.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_feudal_guard_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_hb():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hb.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hb_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gf_rl():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gf_rl.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gf_rl_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_replace_all():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'replace_all.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'replace_all_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"
