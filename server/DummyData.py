#!/usr/bin/python26

# Dummy sequence metadata
def GetDefaultSequence():
    return {"metadata":{"name":"FAC synthesis",
        "time":"8:00",
        "date":"05/01/2012",
        "comment":"Routine FAC synthesis",
        "id":1,
        "creator":"devel",
        "operations":17},
        "components":[{"componenttype":"CASSETTE",
        "id":1,
        "reactor":1,
        "available":True,
        "reagents":[1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10]},
        {"componenttype":"CASSETTE",
        "id":2,
        "reactor":2,
        "available":True,
        "reagents":[11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20]},
        {"componenttype":"CASSETTE",
        "id":3,
        "reactor":3,
        "available":False,
        "reagents":[21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30]},
        {"componenttype":"ADD",
        "id":4,
        "reactor":1,
        "reagent":1},
        {"componenttype":"EVAPORATE",
        "id":5,
        "reactor":1,
        "duration":"00:05.00",
        "evaporationtemperature":"165.0",
        "finaltemperature":"35.0",
        "stirspeed":500},
        {"componenttype":"TRANSFER",
        "id":6,
        "reactor":1,
        "target":"9"},
        {"componenttype":"ELUTE",
        "id":7,
        "reactor":1,
        "reagent":7,
        "target":10},
        {"componenttype":"REACT",
        "id":8,
        "reactor":1,
        "position":1,
        "duration":"00:04.30",
        "reactiontemperature":"165.0",
        "finaltemperature":"35.0",
        "stirspeed":500},
        {"componenttype":"PROMPT",
        "id":9,
        "reactor":0,
        "message":"Please take a sample for analysis"},
        {"componenttype":"INSTALL",
        "id":10,
        "reactor":1,
        "message":"Take a radiation measurement"},
        {"componenttype":"COMMENT",
        "id":11,
        "reactor":0,
        "comment":"Bromination and cytosine coupling"},
        {"componenttype":"ACTIVITY",
        "id":12,
        "reactor":1}]}

# Dummy sequence reagents
def GetDefaultSequenceReagents():
    return [{"available":True,
        "reagentid":1,
        "componentid":1,
        "position":"1",
        "name":"F-18",
        "description":"18F-/K222/K2CO3"},
        {"available":True,
        "reagentid":2,
        "componentid":1,
        "position":"2",
        "name":"MeCN1",
        "description":"Acetonitrile"},
        {"available":True,
        "reagentid":3,
        "componentid":1,
        "position":"3",
        "name":"MeCN2",
        "description":"Acetonitrile"},
        {"available":True,
        "reagentid":4,
        "componentid":1,
        "position":"4",
        "name":"MeCN3",
        "description":"Acetonitrile"},
        {"available":True,
        "reagentid":5,
        "componentid":1,
        "position":"5",
        "name":"H2O1",
        "description":"Water"},
        {"available":True,
        "reagentid":6,
        "componentid":1,
        "position":"6",
        "name":"H2O2",
        "description":"Water"},
        {"available":True,
        "reagentid":7,
        "componentid":1,
        "position":"7",
        "name":"HBr",
        "description":"Hydrobromic acid"},
        {"available":False,
        "reagentid":8,
        "componentid":1,
        "position":"8",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":9,
        "componentid":1,
        "position":"A",
        "name":"QMA",
        "description":"QMA column"},
        {"available":True,
        "reagentid":10,
        "componentid":1,
        "position":"B",
        "name":"Seppak1",
        "description":"Sep-Pak"},
        {"available":True,
        "reagentid":11,
        "componentid":2,
        "position":"1",
        "name":"C6H12O6",
        "description":"Sugar (yum!)"},
        {"available":True,
        "reagentid":12,
        "componentid":2,
        "position":"2",
        "name":"HCl",
        "description":"Hydrochloric acid"},
        {"available":False,
        "reagentid":13,
        "componentid":2,
        "position":"3",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":14,
        "componentid":2,
        "position":"4",
        "name":"H2",
        "description":"Hydrogen gas"},
        {"available":False,
        "reagentid":15,
        "componentid":2,
        "position":"5",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":16,
        "componentid":2,
        "position":"6",
        "name":"KCl",
        "description":"Potassium chloride"},
        {"available":False,
        "reagentid":17,
        "componentid":2,
        "position":"7",
        "name":"",
        "description":""},
        {"available":True,
        "reagentid":18,
        "componentid":2,
        "position":"8",
        "name":"N2",
        "description":"Liquid nitrogen"},
        {"available":True,
        "reagentid":19,
        "componentid":2,
        "position":"A",
        "name":"Seppak2",
        "description":"Sep-Pak"},
        {"available":False,
        "reagentid":20,
        "componentid":2,
        "position":"B",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":21,
        "componentid":3,
        "position":"1",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":22,
        "componentid":3,
        "position":"2",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":23,
        "componentid":3,
        "position":"3",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":24,
        "componentid":3,
        "position":"4",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":25,
        "componentid":3,
        "position":"5",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":26,
        "componentid":3,
        "position":"6",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":27,
        "componentid":3,
        "position":"7",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":28,
        "componentid":3,
        "position":"8",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":29,
        "componentid":3,
        "position":"A",
        "name":"",
        "description":""},
        {"available":False,
        "reagentid":30,
        "componentid":3,
        "position":"B",
        "name":"",
        "description":""}]
