import requests

headers = {'Accept': 'application/json'}



i = 0
while True:
    r = requests.get('http://localhost:8000/ec2_cpu_utilization_5f5533/' + str(i), headers=headers)
    print(r.json()['cpu_usage'])
    i += 1