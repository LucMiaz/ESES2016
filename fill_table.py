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
def finddata30(OLDPATH):
    if OLDPATH.name=="Dropbox":
        newPath=OLDPATH.joinpath("ESES Course 2016/30 Data")
    elif OLDPATH.name=='30 Data':
        newPath=OLDPATH
    elif OLDPATH.name=='ESES Course 2016':
        newPath=OLDPATH.joinpath('30 Data')
    else:
        newPath=finddata30(OLDPATH.resolve().parents[0])
    return(newPath)
    
def data30(func, *args, **kwargs):
    def changePath(*args, **kwargs):
        OLDPATH=Path(os.getcwd())
        try:
            newPath=finddata30(OLDPATH)
        except IndexError:
            OLDPATH=Path("/Users/Shared/Dropbox/ESES Course 2016/")
            newPath=finddata30(OLDPATH)
        #print(newPath)
        os.chdir(newPath.as_posix())
        ret=func(*args,**kwargs)
        os.chdir(OLDPATH.as_posix())
        return(ret)
    return changePath
def sanitize_element(element):
    ele_=element
    ele_=ele_.replace(" ","_")
    ele_=ele_.replace("+","AND")
    ele_=ele_.replace("/","_")
    ele_=ele_.replace("*","STAR")
    ele_=ele_.replace("%","perc")
    ele_=ele_.replace("[","_")
    ele_=ele_.replace("]","_")
    ele_=ele_.replace("(","_")
    ele_=ele_.replace(")","_")
    ele_=ele_.replace("-","__")
    return(ele_)
def sanitize_headers(headers):
    newheaders=[]
    for ele in headers:
        if ele:
            newheaders.append(sanitize_element(ele))
        else:
            newheaders.append(ele)
    return(newheaders)
    
@data30
def import_xlsx(xlsxFileName, sheetNum=0, header=True, noBlankTitles=True, onlyHeaders=None,dataOnly=True, headersRow=0, sanitize=True):
    imported=[]
    wb2 = xlsx.load_workbook(filename=xlsxFileName, read_only=True, data_only=dataOnly)
    sheet=wb2[wb2.get_sheet_names()[sheetNum]]
    rows=sheet.rows
    for i in range(0,headersRow):
        next(rows)
    if header:
        headers=[cell.value for cell in next(rows)]
    else:
        headers=[]
        for i in range(0,len(rows[0])):
            headers.append('col'+i)
    copyheaders=[i for i in headers if i]
    copyheaders.sort()
    last=""
    count=1
    for i in copyheaders:
        if last==i:
            
            headers[headers.index(i)]=str(i)+str(count)
            count+=1
        else:
            count=1
        last=i
    if sanitize:
        headers=sanitize_headers(headers)
    for row in rows:
        rowD={}
        disposableHeaders=headers.copy()
        
        for cell in row:
            if len(disposableHeaders)>0:
                if disposableHeaders[0]:
                    rowD[disposableHeaders.pop(0)] = cell.value
        copyRow=copy.copy(rowD)
        
        imported.append(rowD)
    #sanitize de headers
    print(headers)
    return imported

def sheets_xlsx(xlsxFileName):
    wb2 = xlsx.load_workbook(filename=xlsxFileName, read_only=True)
    return wb2.get_sheet_names()

def write_xlsx(xlsxFileName, data):
    wb = Workbook()
    # grab the active worksheet
    ws = wb.active
    for row in data:
        # Rows can also be appended
        ws.append(row)
    # Save the file
    wb.save(xlsxFileName)

def sanitize_sample_code(debut):
    if debut:
        if "+" in debut:
            divided=debut.split(".")#split the string around dots
            last=divided[-1]#takes the last element of the list
            start=divided[:-1]#take the first elements
            pluses=last.split("+")#split around +s
            plusret=[]
            for plus in pluses:
                if len(plus)==1:
                    plus="0"+plus#add a 0 at the start if the plus has only one digit
                plusret.append(plus)#adds it to the list of pluses
            last= "+".join(plusret)#join the plus again
            debut=".".join(start)+"."+last#joint the start and the end.
            print("Changed to "+ debut)
        elif len(debut.split(".")[-1])==1:
            last=debut[-1]
            debut=debut[:-1]+"0"+last
            print("Changed to "+ debut)
        else:
            debut=None  
    return debut

def insert_PFxx():
    
    obs=match(label="Observation", type="PFxx", date=date)
    if len(obs)>0:
        obs=obs[0]
    else:
        obs=Observation(type="PFxx", date=date)
    lc=match(label="Instrument", name="LC")
    if len(lc)>0:
        lc=lc[0]
    else:
        lc=Instrument(name="LC")
    

def fill_PFxx(fileName, instrumentObj, observationObj, ppcode=None, folderName="", idCode="sample ID"):
    fileName=folderName+fileName
    idCode=sanitize_headers([idCode])[0]
    data=import_xlsx(xlsxFileName=fileName, headersRow=1, sanitize=True)
    for row in data:
        ppcode=row['operator'].split(",")
        del row['operator']
        
        
        sampleId=row[idCode]
        sampleId=sanitize_sample_code(sampleId)
        if not sampleId:
            sample=Sample(type='Sediment',site='Archive',code=row[idCode])
            siteCode="Archive"
        elif len(sampleId.split("."))>1:
            sample=match(label='Sample', code=sampleId)[0]
            siteCode=int(sampleId.split(".")[2])
        else:
            typeSample=sampleId.split(" ")[0].lower()
            siteCode=None
            if typeSample =="control":
                sample=Sample(type="Sediment",typeSample="Control",code=sampleId)
            elif typeSample=="blank" or typeSample == "tom":
                sample=Sample(type="Sediment",typeSample="Blank", code=sampleId)
            else:
                print("ERRoR")
                sample=Sample(type="ERROR", code=sampleId)
        del row['idCode']
        val=Value(type="PFxx",**row)
        Relationship(val,"MEASURE_ON",sample)
        for pp in ppcode:
            pp=pp.replace(" ","")
            ppObj=match(label="Person",initials=pp.lower())
            if len(ppObj)>0:
                Relationship(val,"TAKEN_BY", ppObj[0])
            else:
                print("Person not found "+pp+" for sample "+sampleId)
        Relationship(val,"TAKEN_WITH",lc)
        site=match(label="Site", code=siteCode)
        if len(site)>0:
            Relationship(val,"TAKEN_IN",site[0])
        Relationship(val,"MEASURE_OF",obs)


def insert_data_from_file(fileName, relationshipProps, instrumentToValue, observationObj, headersRow=0,folderName="", idLabel="Sample Id", date=None):
    """
    indicate how to find the sample id
    indicate how to find the ppcode
    relationshipProps must contain a list of duples with the original label, the destinated label, unit
    
    """
    fileName=folderName+fileName
    data=import_xlsx(xlsxFileName=fileName, headersRow=headersRow, sanitize=True)
    relProps=[]
    idLabel=sanitize_element(idLabel)
    for original, target, unit in relationshipProps:
        relProps.append([sanitize_element(original), sanitize_element(target), unit])
    for datum in data:
        props={}
        sprops={}
        units={}
        sampleId=datum[idLabel]
        for original, target,unit in relProps:
            try:
                props[target]=datum[original]
            except:
                print("No "+original+" in "+ str(sampleId))
            if unit:
                units[target]=unit
        props["units"]=units
        
        sample=match(label="Sample", code=sampleId)
        if len(sample)>0:
            sample[0].add(**props)
            Relationship(observationObj, "OF",sample[0], **props)

def insert_Hg():
    folderName="37 HgDMA"
    fileNames=["HgDMA_160920_ESES1_sed+zoo prel.xlsx","HgDMA_160922_ESES2_sed+zoo prel.xlsx","HgDMA_160928_ESES_fish+sed prel2.xlsx","HgDMA_160929_ESES_sedFD1 prel.xlsx","HgDMA_160930_ESES_sedFD2 prel.xlsx"]
    dma=match(label="Instrument",name="DMA-80")
    if len(dma)>0:
        dma=dma[0]
    else:
        dma=Instrument(name="DMA-80",manufacturer="Milestones Srl", website="http://www.milestonesrl.com/en/mercury/dma-80/features.html")
    groups={"ESES1":["lumi","faba","jeis","cagr","lojs","giho"],"ESES2":["erwi","mamä","idbo","mahe","laan","jojo"]}
    for filen in fileNames:
        print(filen)
        xlsxFileName= folderName+"/"+filen
        relationshipProps=[["W boat","boatWg","g"],["W sample","sampleWg","g"],["W boat+ash","boatANDashWg","g"],["Comments","comments",None],["Hg ng","Hg","ng"],["Hg ng/g","Hg_","ng/g"],["LOI*","loi","%"],["Row","row",None]]
        splitted=filen.split("_")
        date=splitted[1]
        group=splitted[2]
        name=splitted[3]
        observationObj=match(label="Observation", name=name, date=date)
        if len(observationObj)>0:
            observationObj=observationObj[0]
        else:
            observationObj=Observation(type="Hg", name=name, date=date, group=group)
            Relationship(observationObj,"WITH",dma)
            if group in groups.keys():
                pp=groups[group]
                for person in pp:
                    personObj=match(label="Person", initials=person)
                    if len(personObj)>0:
                        personObj=personObj[0]
                        Relationship(observationObj, "BY", personObj, group=group, date=date)
            insert_data_from_file(xlsxFileName, relationshipProps,dma,observationObj, headersRow=0, idLabel="ID sample")


def insert_water():
    filename="33 Water/161004_Water compilation_MH.xlsx"
    sheets=[1,2,3]
    
    

@data30
def insert_sites(xlsxFileName="31 Sites/Site description (Sunbeam).xlsx"):
    data=import_xlsx(xlsxFileName=xlsxFileName, sheetNum=2, sanitize=False, headersRow=1)
    letters=list(string.ascii_uppercase)
    sitesObj=[]
    for site in data:
        
        if site['GPS'] and isinstance(site['Site'],int):
            latraw,lonraw=site["GPS"].split(",")
            lat=float(latraw[2:4])+float(latraw[6:12])/60
            lon=float(lonraw[3:5])+float(lonraw[7:13])/60
            
            siteDict={"name":site["Site name"], "code":site["Site"], "letter":letters.pop(0), "lat":round(lat,6), "lon":round(lon,6),"temperature":site["Temperature (°C)"], "depth":site["Depth (m)"],"region":site["Region"], "eniroDepth":site["Eniro depth (m)"]}
            matched=match(label="Site", code=site["Site"], letter=siteDict['letter'], lat=siteDict['lat'], lon=siteDict['lon'])
            if len(matched)>0:
                sitesObj.append(matched[0])
            else:
                sitesObj.append(Site(**siteDict))
            
    return sitesObj
    
@data30   
def insert_ctd(xlsxName='33 Water/332 CTD/CTD_160926_rawData_MaHe.xlsx'):
    #inserting ctd observations
    ctdHeaders=sheets_xlsx(xlsxName)
    ctdInst=Instrument(name="ctd", measures=[{"pressure":"dbar"},{"temperature":"degC"},{"conductivity":"mS/cm"},{"salinity":"ppt"},{"sigma":"kg/m3"},{"time":"absolute"}])
    for sheetNum in ctdHeaders:
        try:
            siteCode=(sheetNum.split("_")[0]).split(" ")[1]
        except:
            if siteCode == "Transect":
                siteCode=0
                site=Site(code=0, name="Transect", letter="T")
        else:
            try:
                siteCode="".join([letter if letter in ["0","1","2","3","4","5","6","7","8","9"] else "" for letter in siteCode])
            except:
                print("Problem with "+str(siteCode)+". Could not digit-join.")
            else:
                if siteCode=="":
                    siteCode=99
        try:
            siteCode=int(siteCode)
        except:
            print("Could not convert "+str(siteCode)+ " to string")
        print(siteCode)
        try:
            repCode=sheetNum.split("_")[1]
        except:
            failed.append(str(sheetNum))
        else:
            try:
                repCode=int(repCode)
            except ValueError:
                repCode="".join([letter if letter in ["0","1","2","3","4","5","6","7","8","9"] else "" for letter in repCode])
                if repCode=="":
                    repCode=99
                repCode=int(repCode)
            code="E.ctd."+str(siteCode)+"."+str(repCode)
            imported=import_xlsx(xlsxName,sheetNum=ctdHeaders.index(sheetNum), sanitize=False)
            dateObs= imported[0]["date"]
            values=[sheetNum,repCode,str(dateObs.year)+"-"+str(dateObs.month)+"-"+str(dateObs.day),siteCode]
            failed=[]
            #
            ctd=Sample(type="ctd",site=siteCode, number=repCode, date=str(dateObs.year)+"-"+str(dateObs.month)+"-"+str(dateObs.day))
            instrumentrelation=Relationship(ctd,"TAKEN_WITH",ctdInst)
            
            data={"dataset":[],"pressure":[],"temperature":[],"conductivity":[],"salinity":[],"sigma":[],"time":[]}
            dataUnits={"dataset":"","pressure":"dbar","temperature":"degC","conductivity":"mS/cm","salinity":"ppt","sigma":"kg/m3","time":"absolute"}
            for datum in imported:
                time=datum["time"]
                timeStr=str(time.hour)+":"+str(time.minute)
                measure={"dataset":datum["Datasets"],"pressure":datum["Press [dbar]"],"temperature":datum["Temp [degC]"],"conductivity":datum["Cond [mS/cm]"],"salinity":datum["SALIN [ppt]"],"sigma": datum["SIGMA [kg/m3]"],"time":timeStr}
                data["dataset"].append(datum["Datasets"])
                data["pressure"].append(datum["Press [dbar]"])
                data["temperature"].append(datum["Temp [degC]"])
                data["conductivity"].append(datum["Cond [mS/cm]"])
                data["salinity"].append(datum["SALIN [ppt]"])
                data["sigma"].append(datum["SIGMA [kg/m3]"])
                data["time"].append(timeStr)
                #testing if up and down
                
                #obs=Observation(**measure)
                #Relationship(obs,"OF",ctd)
                #Relationship(obs,"BY",ctdInst)
            lowest=max(data['pressure'])
            highest=min(data['pressure'])
            lindex=data['pressure'].index(lowest)
            half=data['pressure'][lindex:]
            halfhighest=min(half)
            if (halfhighest-lowest)/(highest-lowest) < 0.5:
                data["run"]="down"
            else:
                data["run"]="down+up"
            data['code']=code
            ctd.add(**data)
            ctd.push()
            site=match(label="Site",code=int(siteCode))
            if len(site)>0:
                Relationship(ctd,"TAKEN_IN",site[0])
            else:
                print("No site to match for ctd measure : "+str(ctd))
    return failed




def insert_people():
    People=[]
    people=[["Luc","Miaz","luc.miaz@gmail.com"],["Lotta", "Sjöholm", "lotta.sjoholm@live.com"],["Erika", "Wikmark", "erikawikmark@gmail.com"],["Magdalena", "Mähler", "magdalenamahler@hotmail.com"],["Ida", "Bohman", "ida.c.bohman@gmail.com"],["Fabian", "Balk", "fabian.g.p.balk@gmail.com"],["Gisela", "Horlitz", "gisela_horlitz@gmx.de"],["Markus", "Hermann", "markushermann01@googlemail.com"], ["Jennifer", "Isaksson", "jennifer.isaksson@gmail.com"],["Caroline", "Grannemann", "caroline.grannemann@rwth-aachen.de"], ["Laura", "Anthony", "laura_anthony@hotmail.com"],["Josefine", "Johansson", "josefine.johansson@hotmail.com"]]
    for person in people:
        newone=match(label="Person",name=person[0],surname=person[1])
        if len(newone)>0:
            People.append(newone[0])
        else:
            newone=Person(name=person[0],surname=person[1],email=person[2])
            People.append(newone)
    return(People)
    





    

