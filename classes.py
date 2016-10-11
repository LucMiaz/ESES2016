import uuid
from neo4j.v1 import GraphDatabase, basic_auth
import ast
from datetime import datetime
import pandas as pd


class with_session(object):
    def __init__(self, url="bolt://hobby-keipgkicjildgbkelajdofnl.dbs.graphenedb.com:24786", user="ESES2016",pwd="JPTJ5EFwAW8C5AJm0vPM"):
        self.url=url
        self.user=user
        self.pwd=pwd
        self.sessionNeo4j=None

           
    def __call__(self, func):
        def operate(*args, **kwargs):
            try:
                kwargs["sessionNeo4j"]=self.sessionNeo4j
                return func(*args, **kwargs)
            except:
                kwargs["sessionNeo4j"]=sessionNeo4j =GraphDatabase.driver(self.url, auth=basic_auth(self.user,self.pwd)).session()
                result=func(*args, **kwargs)
                sessionNeo4j.close()
                return result
        return operate

        
    def __enter__(self):
        print("creating session")
        self.sessionNeo4j = GraphDatabase.driver(self.url, auth=basic_auth(self.user,self.pwd)).session()
        self.active=True
    
    def __exit__(self, ex, ft, k):
        print("closing session")
        self.sessionNeo4j.close()
        self.active=False

    

    
"""

#in case of local


class with_session(object):
    def __init__(self, url="bolt://localhost", user="neo4j",pwd="eses"):
        self.url=url
        self.user=user
        self.pwd=pwd
        self.sessionNeo4j=None

           
    def __call__(self, func):
        def operate(*args, **kwargs):
            try:
                kwargs["sessionNeo4j"]=self.sessionNeo4j
                return func(*args, **kwargs)
            except:
                kwargs["sessionNeo4j"]=sessionNeo4j =GraphDatabase.driver(self.url, auth=basic_auth(self.user,self.pwd)).session()
                result=func(*args, **kwargs)
                sessionNeo4j.close()
                return result
        return operate

        
    def __enter__(self):
        print("creating session")
        self.sessionNeo4j = GraphDatabase.driver(self.url, auth=basic_auth(self.user,self.pwd)).session()
        self.active=True
    
    def __exit__(self, ex, ft, k):
        print("closing session")
        self.sessionNeo4j.close()
        self.active=False
       """
       
@with_session()
def RUN(command,sessionNeo4j):
    return sessionNeo4j.run(command)

@with_session()
def RUN_df(command, sessionNeo4j):
    data=sessionNeo4j.run(command)
    df = pd.DataFrame(columns=data.keys())
    keys=data.keys()
    count=0
    for datum in data:
        df.loc[count]=[datum[key] for key in keys]
        count+=1
    return(df)
 
def node(func):
    def init_wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        super(self.__class__, self).__init__(**kwargs)
    return init_wrapper

def match(*args,**kwargs):
    try:
        label=kwargs.pop("label")
    except:
        print("label was not found. Needed for match function.")
    else:
        properties=kwargs
        if len(properties.keys())>0:
            command='MATCH (n:'+label+dictToStr(properties)+') RETURN n'
        else:
            command='MATCH (n:'+label+') RETURN n'
        result=RUN(command)
        #print(command)
        result_list=list(result)
        returnlist=[]
        if len(result_list)==0:
            pass
            #print("No match for search : "+ command)
        else:
            for record in result_list:
                props=record["n"].properties
                klass=globals()[label](**props)
                returnlist.append(klass)
        return(returnlist)



def dictToStr(props):
    string=[]
    for prop in props.keys():
        if  isinstance(props[prop], int) or isinstance(props[prop], float):
            string.append(prop+': '+str(props[prop]))
        elif isinstance(props[prop], bool):
            string.append(prop+': '+str(int(props[prop])))
        else:
            string.append(prop+': "'+str(props[prop])+'"')
    propsRet=("{"+",".join(string)+"}")
    return propsRet
    
class Node(object):
    element_type="Node"
    unique=True
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if "id" in kwargs.keys():
            self.id=kwargs["id"]
            self.push()
        else:
            self.id=str(uuid.uuid1())
            self.create()
    
    def create(self):
        if self.unique:
            command="MERGE (a:"+self.element_type+" "+self.__props__+")"
        else:
            command="CREATE (a:"+self.element_type+" "+self.__props__+")"
        RUN(command)
        
    def push(self):
        command='MATCH (n:'+self.element_type+') WHERE n.id="'+self.id+'" SET n = '+str(self.__props__)
        RUN(command)
    def add(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return(kwargs)
    @property
    def __props__(self):
        props=dictToStr(self.__dict__)
        return(props)
    def pull(self):
        self=match(**self.__dict__)
    

class Relationship(object):
    element_type="Relationship"
    def __init__(self, Node1, label, Node2,**kwargs):
        self.n1=Node1
        self.n2=Node2
        self.label=label
        self.props=kwargs
        self.create()
    
    def create(self):
        matchCommand="MATCH (n:"+self.n1.element_type+") WHERE n.id= '"+self.n1.id+"' MATCH (m:"+self.n2.element_type+") WHERE m.id='"+self.n2.id+"'"
        createCommand=" CREATE (n)-[:"+self.label+dictToStr(self.props)+"]->(m)"
        #print(createCommand)
        RUN(matchCommand+createCommand)

    def push(self):
        matchCommand="MATCH (n:"+self.n1.element_type+") WHERE n.id= '"+self.n1.id+"' MATCH (m:"+self.n2.element_type+") WHERE m.id='"+self.n2.id+"' MATCH (n)-[R:"+self.label+"]->(m)"
        setCommand="SET R="+dictToStr(self.props)
        RUN(matchCommand+setCommand)

class Person(Node):
    element_type = "Person"
    @node
    def __init__(self, name, surname, **kwargs):
        self.name = name
        self.surname = surname
        self.initials = (name[0:2]+surname[0:2]).lower()
    def __str__(self):
        return(self.name+" "+self.surname+" (" +self.initials+")")
    def __repr__(self):
        return(self.initials)
    def name(self):
        return(self.name)
    def fullName(self):
        return(self.name +" " +self.surname)
    def initials(self):
        return(self.initials)
    def samples(self):
        return(commaJoin(self.handled,True))
    def addSample(self, sample):
        pass

class Site(Node):
    element_type = "Site"
    @node
    def __init__(self, **kwargs):
        pass    

class Bottle(Node):
    element_type="Bottle"
    @node
    def __init__(self, code, **kwargs):
        self.code=code


class Sample(Node):
    element_type = "Sample"
    @node
    def __init__(self, type, **kwargs):
        for prop in [p for p in ctdSample.__dict__.keys() if p[0]!="_"]:
            if getattr(self,prop)[0]=="[":
                setattr(self, prop, ast.literal_eval(self.get(prop)))
        self.type=type
        self.units={}
    
    def takenIn(self, site=None, properties=None):
        if not site:
            try:
                site=int(self.siteCode)
            except KeyError:
                print("No 'SiteCode' property")
                return None
        siteRef=match(type="Site",code=site)
        if siteRef:
            r=Relationship(self,"TAKEN_IN",siteRef[0])
            return r
        else:
            print("No site found with siteCode : "+str(self.siteCode))
            return None
    def __str__(self):
        return(self.element_type+" "+self.code)
    def __repr__(self):
        return(self.code)
    def handlers(self):
        return(commaJoin(self.handlers,False))
    def site(self):
        site=match(type="Site",code="self.siteCode")
        return(self.site[0].code+" " +self.site[0].name)
    
class WaterSample(Sample):
    element_type = "WaterSample"
    def __init__(self, **kwargs):
        pass
        

class ZooSample(Sample):
    element_type = "ZooSample"
    @node
    def __init__(self, **kwargs):
        pass
        
class SedimentSample(Sample):
    element_type = "SedimentSample"
    @node
    def __init__(self, priority, waterType, **kwargs):
        """waterType is either "fresh" or "salt"
        priority is 1,2 or 0 (0 is for no priority)"""
        if waterType not in ["fresh", "salt"]:
            waterType=None
            print("error in waterType of sediment sample")
        self.waterType=waterType
        if priority not in [0,1,2]:
            priority=0
            print("error in priority of sediment sample set to 0")
        self.priority=priority
    def __str__(self):
        return("Sediment sample " +self.code)
class ctdSample(Node):
    element_type="ctdSample"
    @node
    def __init__(self, **kwargs):
        pass
        
        
class Observation(Node):
    """
    an observation of a variable, for one or several samples (for example one run of DMA-80)
    """
    element_type="Observation"
    @node
    def __init__(self, type, date, **kwargs):
        self.type=type
        self.date=date
        
        
    def handledBy(self, subject, properties=None):
        """links the observation with the people that carried it, using their initials"""
        pp=[]
        try:
            for person in self.ppcode:
                pp.append(match(type="Person",initials=person)[0])
        except KeyError:
            print("No 'ppcode' property")
        else:
            for person in pp:
                r=Relationship(self,"HANDLED_BY",person)
                return r
class Value(Node):
    """
    the values measured during one observation (for example during one run of DMA-80)
    """
    element_type="Value"
    @node
    def __init__(self, **kwargs):
        """insert at least a type"""
        pass
        
class Instrument(Node):
    element_type="Instrument"
    @node
    def __init__(self, **kwargs):
        pass
