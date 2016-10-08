import fill_table as flt
from datetime import datetime
t= datetime.now()
sites=flt.insert_sites()

deltat=datetime.now()-t
print("sites --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> people")
pp=flt.insert_people()

deltat=datetime.now()-t
print("people --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> ctd")


ctd=flt.insert_ctd()

deltat=datetime.now()-t
print("ctd --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> sediments")
sediments=flt.insert_sediments(auto=True)
deltat=datetime.now()-t
print("sediments --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> fishes")
fishes=flt.insert_fish()

deltat=datetime.now()-t
print("fishes --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> zoo")
zoo=flt.insert_zoo()

deltat=datetime.now()-t
print("zoo --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> hg1")

dt=flt.insert_hg(fileName='HgDMA_160920_ESES1_sed+zoo prel.xlsx',folderName="37 HgDMA/copy in xlsx/", group="ESES1", date="2016-09-20", ppcode=["lumi","faba", "jeis", "giho","cagr","losj"])

deltat=datetime.now()-t
print("hg1 --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> hg2")

dt2=flt.insert_hg(fileName='HgDMA_160922_ESES2_sed+zoo prel.xlsx',folderName="37 HgDMA/copy in xlsx/", group="ESES2", date="2016-09-22", ppcode=["mamä","idbo", "mahe", "laan","jojo","erwi"])

deltat=datetime.now()-t
print("hg2 --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> hg3")

dt3=flt.insert_hg(fileName='HgDMA_160928_ESES_fish+sed prel2.xlsx',folderName="37 HgDMA/copy in xlsx/", group="", date="2016-09-28", ppcode=[])
deltat=datetime.now()-t
print("hg3 --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> archive")

archive=flt.Site(code="Archive")
deltat=datetime.now()-t
print("archive --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s"  +"\n---> pfxx")

pfxx=flt.insert_PFxx(fileName="PFOS_compilation.xlsx",folderName="39 PFxx/Quantification of samples/")

deltat=datetime.now()-t
print("pfxx --->| \n "+str(int(deltat.seconds/60))+"mn "+str(deltat.seconds%60)+"s" +"\n---> end")


#MATCH (n:Person{name:"Luc"}) match (m)-[p:MEASURED_ON]->(o)-[r:TAKEN_BY]->(n) RETURN m,n,o,p,r