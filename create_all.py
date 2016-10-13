import os
from pathlib import Path
import ast
from datetime import date, datetime
import openpyxl as xlsx
from openpyxl import load_workbook
import string
import py2neo as pyneo
from classes import *
import copy
import urllib #for eniro api
from fill_table import insert_sites, sheets_xlsx, import_xlsx, insert_people, data30, insert_ctd, insert_Hg, insert_sediments, insert_PFxx

@data30
def insert_codes():
    fileName="99 Database/161003_SampleCodeList.xlsx"
    sheetNames=sheets_xlsx(fileName)
    for sheet in range(0,len(sheetNames)):
        data=import_xlsx(fileName, sheetNum=sheet, sanitize=True)
        print(str(sheet))
        for datum in data:
            if datum['Sample_code']:
                matched=match(label="Sample", code=datum['Sample_code'])
                datum['code']=datum['Sample_code']
                ppcode=None
                if "ppcode" in datum.keys():
                    ppcode=datum['ppcode']
                    del datum['ppcode']
                    ppcode=(ppcode.replace(" ","")).split(",")
                if "collectingTimeList" in datum.keys():
                    if isinstance(datum['collectingTimeList'], list):
                        datum['collectingTimeList']=[int(p) for p in (datum['collectingTimeList'].replace(' ','').split('+'))]
                del datum['Sample_code']
                #TODO add gestion of water bottles ! !!! two to three bottles per sample code !!!!
                ppcode1=None
                ppcode2=None
                if 'ppcode1' in datum.keys():
                    if datum['ppcode1']:
                        ppcode1=datum['ppcode1'].replace(" ","").lower()
                        del datum['ppcode1']
                if 'ppcode2' in datum.keys():
                    if datum['ppcode2']:
                        ppcode2=datum['ppcode2'].replace(" ","").lower()
                        del datum['ppcode2']
                if len(matched)>0:
                    sample=matched[0]
                    if 'bottleCode' in datum.keys():
                        bottle=match(label="Bottle", code=datum['bottleCode'])
                        if len(bottle)>0:
                            bottle=bottle[0]
                        else:
                            bottle=Bottle(code=datum['bottleCode'])
                            propsBot={}
                            if 'removed' in datum.keys():
                                propsBot['removed']=bool(datum['removed'])
                            Relationship(sample, "STORED_IN", bottle, **propsBot)
                            del datum['bottleCode']
                    sample.add(**datum)
                else:
                    sample=Sample(**datum)
                    site=match(label="Site",code=sample.site)
                    if len(site)>0:
                        Relationship(sample,"FROM", site[0])
                    if ppcode:
                        for person in ppcode:
                            person=person.lower()
                            pp=match(label="Person", initials=person)
                            if len(pp)>0:
                                props={}
                                Relationship(sample, "SUPERVISED_BY", pp[0],**props)
                                
                if ppcode1:
                    propsSecci1={}
                    propsSecci1['secci_depth_left']=datum['seccil']
                    person1=match(label="Person", initials=ppcode1)
                    try:
                        site[0].add(secci_depth_left=datum['seccil'])
                        site[0].push()
                    except:
                        pass
                    try:
                        propsSecci1={side:"left",value:datum['seccil']}
                        Relationship(person1[0],"SECCI",site[0],propsSecci1)
                    except:
                        pass
                if ppcode2:
                    propsSecci2={}
                    propsSecci2['secci_depth_right']=datum['seccir']
                    person2=match(label="Person", initials=ppcode2)
        
                    try:
                        site[0].add(secci_depth_right=datum['seccir'])
                        site[0].push()
                    except:
                        pass
                    try:
                        propsSecci2={side:"right",value:datum['seccir']}
                        Relationship(person2[0],"SECCI",site[0],propsSecci2)
                    except:
                        pass


if __name__=="__main__":
    with with_session():
        #Fish sites
        F1=Site(code="F1",name="Fish site 1", lat=59.334508,lon=17.5396427, region="Mälaren", regionWater="Ref Mälaren")
        F2=Site(code="F2", name="Fish site 2", region="Baltic Sea", regionWater="Ref Baltic Sea")
        Site(code="Control", letter="S")
        Site(code="Blank", letter="Z")
        Site(code="Archive", region="Mälaren", regionSed="Mälaren", letter="O")
        
        insert_sites()
        insert_people()
        insert_codes()
        
        insert_ctd()
        insert_Hg()
        
        insert_sediments()
        
        insert_PFxx()
        
