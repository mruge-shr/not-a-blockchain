from chain import *

mychain = Chain()

user1 = User()
user2 = User()
asset1 = Asset()

mychain.add_block([
    (asset1.id, asset1.id, dict(url='mygitrepo/tag', sha='AAABBBCCCDDD')),
    (user1.id, asset1.id, Action.CREATED)
])
mychain.add_block([
    (user2.id, asset1.id, Action.USED)
])


output(mychain)

output(mychain, mode='graph', filename='graph.dot')
output(mychain, mode='chain', filename='chain.dot')
