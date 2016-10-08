@data30
def insert_sediments(xlsxFileName="34 Sediment/SEDIMENT2.xlsx",auto=False, rounding=3):
    sheetNames=sheets_xlsx(xlsxFileName)
    if auto:
        sheetNum=1
    else:
        print("The file "+str(xlsxFileName)+" contains the following sheets :")
        for i in range(0,len(sheetNames)):
            print(str(i+1)+". "+sheetNames[i])
        res=0
        while res < 1 or res-1>len(sheetNames):
            res=input("Select sheet name (use q to quit): ")
            if res=="q":
                res=1
            else:
                try:
                    res=int(res)
                except:
                    print("insert only integers or q")
                    res=0
        sheetNum=res-1
    data=import_xlsx(xlsxFileName=xlsxFileName,sheetNum=sheetNum,dataOnly=True, sanitize=False)
    priorityraw=import_xlsx(xlsxFileName=xlsxFileName, sheetNum=sheetNum+1, dataOnly=True, sanitize=False)
    priority=[]
    for row in priority:
        codepriority=row['Sample code']
        res=codepriority.split(".")
        if len(res)>1:
            if res[0]=="E" and res[1]=="S":
                priority.append(codepriority)
    #todo add type of water in the sediment xlsx and import it
    sediments=[]
    for sample in data:
        
        labels={}
        variables={}
        units={}
        labelsToVar=[
                    ['Cermic vial weight + sample','ceramicAndSampleWg','g'],
                    ['After burning','ceramicAfterBurnWg','g'],
                    ['Weight for PF (g)','PFusedWg','g'],
                    ['weight to get 1mg of organic matter [mh]','onemgOrgMatter','mg'],
                    ['Ceramic vial weight','ceramicWg','g'],
                    ['Wet-weight sample (g)','wetSampleWg','g'],
                    ['WC [%]','waterContent','g'],
                    ['Weight Aluminium + sample (g)','aluminiumAndSampleWg','g'],
                    ['Weight Aluminium box (g)','aluminiumWg','g'],
                    ['Dry weight sample (g)','drySampleWg','g'],
                    ['DC [%]','dc','%'],
                    ['Ceramic vial code','ceramicCode',''],
                    ['Sample code','code','g'],
                    ['Dry weight sample aluminium box+sample (g)','drySampleAndAluminiumWg','g'],
                    ['Weight of plastic bottle (g)','plasticBottleWg','g'],
                    ['LOI [%]','loi','%']]
        
        unit='gram'
        unitabb='g'
        
        #TODO waterType
        waterType=0
        prio=(sample['Sample code'] in priority)
        seds=Sample(type="Sediment")
        seds.add(priority=prio,waterType=waterType)
        for ltv in labelsToVar:
            labels[ltv[0]]=ltv[1]
            variables[ltv[1]]=ltv[0]
            units[ltv[1]]=ltv[2]
            valueofprop=sample[ltv[0]]
            if isinstance(valueofprop,float):
                valueofprop=round(valueofprop,rounding)
            try:
                propsToAdd={ltv[1]:valueofprop}
            except:
                print(ltv[0])
            seds.add(**propsToAdd)
        splittedCode=sample['Sample code'].split(".")
        if len(splittedCode)==4:
            
            siteCode=int(splittedCode[2])
            try:
                depth=int(splittedCode[3])
            except:
                depth=splittedCode[3]
        else:
            print(str(splittedCode))
            siteCode=1
            depth=1
        loi=(seds.ceramicAndSampleWg-seds.ceramicAfterBurnWg)/(seds.ceramicAndSampleWg-seds.ceramicWg)
        #print(str(loi))
        seds.loi=loi
        seds.add(siteCode=siteCode,depth=depth)
        seds.push()
        seds.takenIn()
        sediments.append(seds)
    
    return(sediments)


def insert_hg(fileName, group, date, ppcode=None, folderName="37 HgDMA/"):
    fileName=folderName+fileName
    data=import_xlsx(xlsxFileName=fileName, sanitize=True)
    dma=Instrument(name="DMA-80",manufacturer="Milestones Srl", website="http://www.milestonesrl.com/en/mercury/dma-80/features.html")
    obs=Observation(type="Hg", group=group, date=date)
    Relationship(obs, "TAKEN_WITH", dma)
    for pp in ppcode:
        ppObj=match(type="Person", initials=pp)
        try:
            Relationship(obs,"TAKEN_BY",ppObj[0])
        except:
            print(ppObj)
    values=[]
    for row in data:
        try:
            row['code']=row['ID_sample']
            del row['ID_sample']
        except:
            row['code']=None
        if row['code']:
            code=row['code']
            rawcode=code.split(".")
            save=True
            if len(rawcode)==4:
                site=rawcode[2]
                number=rawcode[3]
                analyte=rawcode[1]
                if analyte=="S":
                    analyste="Sediment"
                elif analyte=="F":
                    analyte="Fish"
                elif analyte=="Z":
                    analyte="Zoo"
                elif analyte=="W":
                    analyte="Water"
                else:
                    analyte="Unknown"
                    print("Unknown")
                row["analyte"]=analyte
                try:
                    site=int(site)
                    row['site']=site
                except:
                    print("nope for site :"+str(site))
                    site=None
                try:
                    number=int(number)
                except:
                    number="".join([digit for digit in number if digit in ["0","1","2","3","4","5","6","7","8","9","+"]])
                    letter="".join([letter for letter in number if letter in ["0","1","2","3","4","5","6","7","8","9"]])
                    if letter=="M":
                        row["analyte"]=row['analyte']+" Musle"
                    elif letter=="G":
                        row["analyte"]=row['analyte']+" Gonads"
                if site <10:
                    twodigits="0"+str(site)
                else:
                    twodigits=str(site)
                debut=rawcode[0]+"."+rawcode[1]+"."+twodigits+"."+str(number)
                
            elif len(rawcode)==1:
                site=None
                if rawcode[0] in ["tom","Tom"]:
                    row['analyte']='tom'
                elif rawcode[0] in ['SE3','se3']:
                    row['analyte']='SE3'
                else:
                    print(rawcode)
                debut=None
            else:
                site=None
                print("Print raw-code "+str(rawcode))
                debut=None
                save=False

            if save:
                try:
                    del row[None]
                except:
                    pass
                try:
                    del row["check ∑ !"]
                except:
                    pass
                rowcopy=copy.copy(row)
                
                        
                row=rowcopy
                site=None
                val=Value(**row)
                if site:
                    siteObj=match(type="Site", code=site)
                    if len(siteObj)>0:
                        Relationship(val,"VALUE_OF",site[0])
                if debut:
                    sample=match(type="Sample", code=debut)
                    if len(sample)>0:
                        Relationship(val, "MEASURE_OF", sample[0])
                    else:
                        
                        debut=sanitize_sample_code(debut)
                        
                        sample=match(type="Sample", code=debut)
                        if len(sample)>0:
                            Relationship(val, "MEASURE_OF", sample[0])
                            print("Sample name corrected & relation added")
                        else:
                            print("ERROR !!!!!!!")
                
                        
                Relationship(val,"MEASURED_ON",obs)
                values.append(val)
                print("-----")
    return(values)

def insert_fish(fileName="35 Biota/FISH.xlsx"):
    data=import_xlsx(xlsxFileName=fileName, sanitize=False)
    fishSpecie=""
    lat=float((data[0]['GPS'])[2:])
    lon=float((data[1]['GPS'])[2:])
    date=""
    time=""
    weather=""
    note=""
    
    for row in data:
        if row['SAMPLE CODE']:
            if row['SITE']:
                fishSpecie=row['SITE']
            if row['DATE']:
                date=str(row['DATE'].year)+"-"+str(row['DATE'].month)+"-"+str(row['DATE'].day)
            if row['TIME']:
                time=row['TIME']
            if row['WEATHER']:
                weather=row['WEATHER']
            if row['NOTE']:
                note=row['NOTE']
            if row['GPS']:
                if row['GPS'].split(' ')[0]=="N":
                    lat=float((row['GPS'])[2:])
                elif row['GPS'].split(' ')[0]=='E':
                    lon=float((row['GPS'])[2:])

            try:
                code=row['SAMPLE CODE']
                codesplitted=code.split(".")
                site=int(codesplitted[2])
                number=int(codesplitted[3])
            except:
                print("Error with :" +str(code))
            else:
                disect=row['TIME']
                prepdate=row["DATE OF PREP"]
                prepdate=str(prepdate.year)+"-"+str(prepdate.month)+"-"+str(prepdate.day)
                disectionTime=str(disect.hour)+":"+str(disect.minute)
                fish=Sample(type="Fish", code=code, site=site, number=number, lat=lat, lon=lon, fishGroup=fishSpecie)
                
                #inserting props
                props={}
                propsList=[["gonadWgFishlab","GONAD WEIGHT (fishlab)"],
                                ["gonadWgSedlab","GONAD WEIGHT (sedlab)"],
                                ["specie","SPECIES"],
                                ["sex",'SEX'],
                                ["gonadMaturation","GONAD MATURATION (SM/SIM)"],
                                ["weight",'TOTAL WEIGHT [g]'],
                                ["lengthmm","TOTAL LENGTH [mm]"],
                                ["forkLength",'FORK LENGTH [mm]'],
                                ["length","STANDARD LENGTH [mm]"],
                                ["liverWg","LIVER WEIGHT [g]"],
                                ["gonadWgFishLab",'GONAD WEIGHT (fishlab)'],
                                ["gonadWgSedLab",'GONAD WEIGHT (sedlab)'],
                                ["musleWgSedLab",'MUSCLE WEIGTH (sed lab)'],
                                ["skin",'SKIN'],
                                ["fins",'FINS'],
                                ["dryGonadWgVialLid",'Gonad dry weight+vial+lid (g)'],
                                ["gonadWgVial",'Gonad vial weight (g)'],
                                ["dryGonadComment",'Gonad dry weighing comment'],
                                ["dryMusleWgVialLid",'Musle dry weight+vial+lid (g)'],
                                ["musleVialWg",'Musle vial weight (g)'],
                                ["dryMusleComment",'Musle dry weighing comment']]
                for duo in propsList:
                    cellValue=row[duo[1]]
                    try:
                        cellValue=float(cellValue)
                    except:
                        pass
                    props[duo[0]]=cellValue
                try:
                    props["dryMusleWg"]=props["dryMusleWgVialLid"]-props["musleVialWg"]
                except:
                    props["dryMusleWg"]="n/a"
                try:
                    props["dryGonadWg"]=props["dryGonadWgVialLid"]-props["gonadWgVial"]
                except:
                    props["dryGonadWg"]="n/a"
                
                props["preparationDate"]=prepdate
                props["disectionTime"]=disectionTime,
                """
                props["gonadWgFishlab"]=float(row["GONAD WEIGHT (fishlab)"])
                props["gonadWgSedlab"]=float(row["GONAD WEIGHT (sedlab)"])
                props["specie"]=row["SPECIES"]
                props["sex"]=row['SEX']
                props["gonadMaturation"]=row["GONAD MATURATION (SM/SIM)"]
                props["weight"]=float(row['TOTAL WEIGHT [g]'])
                props["lengthmm"]=float(row["TOTAL LENGTH [mm]"])
                props["forkLength"]=float(row['FORK LENGTH [mm]'])
                props["length"]=float(row["STANDARD LENGTH [mm]"])
                props["liverWg"]=float(row["LIVER WEIGHT [g]"])
                props["gonadWgFishLab"]=float(row['GONAD WEIGHT (fishlab)'])
                props["gonadWgSedLab"]=float(row['GONAD WEIGHT (sedlab)'])
                props["musleWgSedLab"]=float(row['MUSCLE WEIGTH (sed lab)'])
                props["skin"]=row['SKIN']
                props["fins"]=row['FINS']
                props["dryGonadWgVialLid"]=float(row['Gonad dry weight+vial+lid (g)'])
                props["gonadWgVial"]=float(row['Gonad vial weight (g)'])
                props["dryGonadComment"]=row['Gonad dry weighing comment']
                props["dryMusleWgVialLid"]=float(row['Musle dry weight+vial+lid (g)'])
                props["musleVialWg"]=float(row['Musle vial weight (g)'])
                props["dryMusleComment"]=row['Musle dry weighing comment']
                
                props["dryMusleWg"]=props["dryMusleWgVialLid"]-props["musleVialWg"]
                props["dryGonadWg"]=props["dryGonadWgVialLid"]-props["gonadWgVial"]
                
                props["preparationDate"]=prepdate
                props["disectionTime"]=disectionTime,
                props["dryMusleWg"]=dryMusleWg
                props["dryGonadWg"]=dryGonadWg
                """
                
                fish.add(**props)
                site=match(type="Site", code=site)
                if len(site)>0:
                    Relationship(fish,"TAKEN_IN",site[0])
                else:
                    print("Error, site not found for "+str(fish))
def insert_zoo(fileName="35 Biota/Zooplankton overview + dw & ww.xlsx"):
    data=import_xlsx(xlsxFileName=fileName, headersRow=1, sanitize=False)
    zoofishnet=Instrument(name="Zoofishnet")
    zoos=[]
    for row in data:
        try:
            code = row["Sample Code"]
        except:
            code=None
        else:
            spltcode=code.split(".")
            continuer=True
            try:
                site=spltcode[2]
                site=int(site)
            except:
                print("No site for "+str(code))
                continuer=False
            try:
                rep=spltcode[3]
                rep=int(rep)
            except:
                print("No repetition code for "+str(code))
                continuer=False
            if continuer:
                zoo=Sample(type="Zoo", code=code, repetition=rep, site=site)
                props={}
                collectingTimeList=row['Collecting Time [min]']
                try:
                    collectingTimeList=collectingTimeList.split("+")
                    collectingList=[int(t) for t in collectingTimeList]
                except:
                    collectingList=[collectingTimeList]
                    try:
                        collectingList=int(collectingList)
                    except:
                        pass
                
                props['collectingTimeList']=collectingList
                props['time']=str(row['Time'].hour)+":"+str(row['Time'].minute)
                propListe=[["comments","Comments"],["collectingTime","Collecting Time (total [min])"],["weather","Weather"]]
                zoo.add(**props)
                site=match(type="Site",code=site)
                if len(site)>0:
                    Relationship(zoo,"TAKEN_IN",site[0])
                else:
                    print("Site not found for "+code)
                ppcodes=row["PP Code"]
                ppcodes=ppcodes.split(",")
                ppcodes=[("".join(p.split())) for p in ppcodes]
                for person in ppcodes:
                    pp=match(type="Person", initials=person.lower())
                    if len(pp)>0:
                        Relationship(zoo, "TAKEN_BY",pp[0])
                    else:
                        print("Person not found : "+str(person))
                Relationship(zoo,"TAKEN_WITH", zoofishnet)
                zoos.append(zoo)
        
    
    return(data)

def insert_PFxx(fileName, date="2016-10-01", ppcode=None, folderName=""):
    fileName=folderName+fileName
    data=import_xlsx(xlsxFileName=fileName, headersRow=1)
    lc=Instrument(name="LC")
    ppcode=None
    addObs=True#Do I have to instantiate a new observation ?
    obs=Observation(type="PFxx", date=date)
    for row in data:
        ppcode=row['operator'].split(",")
        del row['operator']

        sampleId=row['sample ID']
        sampleId=sanitize_sample_code(sampleId)
        if not sampleId:
            sample=Sample(type='Sediment',site='Archive',code=row['sample ID'])
            siteCode="Archive"
        elif len(sampleId.split("."))>1:
            sample=match(type='Sample', code=sampleId)[0]
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
        del row['sample ID']
        val=Value(type="PFxx",**row)
        Relationship(val,"MEASURE_ON",sample)
        for pp in ppcode:
            pp=pp.replace(" ","")
            ppObj=match(type="Person",initials=pp.lower())
            if len(ppObj)>0:
                Relationship(val,"TAKEN_BY", ppObj[0])
            else:
                print("Person not found "+pp+" for sample "+sampleId)
        Relationship(val,"TAKEN_WITH",lc)
        site=match(type="Site", code=siteCode)
        if len(site)>0:
            Relationship(val,"TAKEN_IN",site[0])
        Relationship(val,"MEASURE_OF",obs)

@data30
def insert_sites_old():
    #inserting sites
    sites=[]
    malaren="Mälaren"
    city="Stockholm"
    baltic="Baltic"
    sites.append(['Söder Björdfjärden', 18, 'A', 17,29.827,59,17.742,16.1,39.4,malaren])
    sites.append(['Norr Björdfjärden', 2, 'B', 17,24.952,59,26.694,16.1,43.2,malaren])
    sites.append(['Hattholmen', 3, 'C', 17,32.193,59,29.04,16.4,37.2,malaren])
    sites.append(['Sandviken', 20, 'D',17,38.276,59,28.136,16.6,23.9,malaren])
    sites.append(['Brafjärden', 4, 'E', 17,38.276,59,28.136,16.6,23.9 ,city])
    sites.append(['Görväln', 6, 'F', 17,44.73,59,25.238,16.7,47.9,city])
    sites.append(['Hässelby', 21, 'G', 17,51.052,59,20.074,16.8,19.4,city])
    sites.append(['Drottningholm', 7, 'H', 17,53.618,59,20.075,17.0,10.2,city])
    sites.append(['Värbyfjärden', 17, 'I', 17,52.502,59,17.295,17.2,17.9,city])
    sites.append(['Traneberg', 8, 'J', 17,57.494,59,18.579,17.3,34.8,city])
    sites.append(['Traneberg', 9, 'K',17,59.601,59,19.761,17.5,19.2,city])
    sites.append(['Riddarfjärden', 10, 'L', 18,2.754,59,19.369,17.6,18.,city])
    sites.append(['Årstaviken', 1, 'M', 18,2.229,59,18.503,17.7,6.6,city])
    sites.append(['Varsadjupet', 11, 'N', 18,5.258,59,19.215,12.2,28.3,city])
    sites.append(['Halvkakssundet (Koppala)', 12, 'O', 18,14.066,59,20.997,14.,52.3,city])
    sites.append(['Torsbyfjärden', 13, 'P', 18,27.715,59,19.345,15.9,31.1,baltic])
    sites.append(['Ösaxarfjärden', 16, 'Q', 18,30.836,59,27.001,15.3,58.5,baltic])
    
    #for site in sites:
    #    cur.execute("INSERT INTO site VALUES(?,?,?,?,?)",site)
    #con.commit()
    sitesObj=[]
    for site in sites:
        siteDict= {"name":site[0], "code":site[1], "letter":site[2], "lat":round(site[3]+site[4]/60,4), "lon":round(site[5]+site[6]/60,4),"temperature":site[7], "depth":site[8],"area":site[9]}
        sitesObj.append(Site(**siteDict))
    return sitesObj