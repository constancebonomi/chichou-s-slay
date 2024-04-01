import requests as rq
origin = input("Where are you now? ")
destination = input("Where are you going? ")
address = "http://transport.opendata.ch/v1/connections?from=" + origin + "&to=" + destination
print(address)
r = (rq.get(address)).json()
deptplatform = r["connections"][0]['from']['station']
