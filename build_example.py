from uuid import uuid4

from chain import *

mychain = Chain()
pending = []

def add_thing(name, ty='thing'):
    global pending
    uid = uuid4().hex
    t = Transaction(uid, uid, {'name': name,'type': ty})
    pending += [t]
    return uid

def get(name, ty='thing'):
    uid = mychain.get_id(name)
    if uid: 
        return uid 
    for t in pending:
        if t.isGenesis and t.c.get('name','') == name:
            return t.a
    return add_thing(name,ty)

def add(a,b,c):
    global pending
    aid = get(a)
    bid = get(b, ty='Action')
    cid = get(c)
    pending += [Transaction(aid,cid,bid)]

def commit():
    global pending 
    global mychain
    mychain.add_block(transactions=pending)
    pending = []


add('John','CommitsTo','Repo1')
add('Jane','CommitsTo','Repo1')
add('John','WorksFor','Org1' )
add('Jane','WorksFor','Org1' )
add('Jane','Supervises','John')
add('Cluster1','BuiltFrom','Repo1')
add('Org1','Manages','Cluster1')
add('App1','OperatesOn','Cluster1')
add('App1','BuiltFrom','Repo2')
commit()

add('SSP1','Documents','Cluster1')
add('CyberAuthority','Approves','SSP1')
add('Org3', 'Deploys', 'App1')
add('Org1', '!Manages', 'Cluster1')
add('Org2', 'Manages', 'Cluster1')
commit()

add('Org4', 'Evaluates', 'App1')
add('Vulnerability', 'Affects', 'Cluster1')
commit()

print(toYaml(mychain))