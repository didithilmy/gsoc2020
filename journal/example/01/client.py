import requests
from urllib3.exceptions import InsecureRequestWarning
import json

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

RUCIO_BASE_URI = 'https://rucio'

def authenticate(account, username, password):
    headers = {'X-Rucio-Account': account, 'X-Rucio-Username': username, 'X-Rucio-Password': password, 'X-Rucio-AppID': 'swan'}
    response = requests.get(url=f'{RUCIO_BASE_URI}/auth/userpass', headers=headers, verify=False)
    response_headers = response.headers

    auth_token = response_headers['X-Rucio-Auth-Token']
    expires = response_headers['X-Rucio-Auth-Token-Expires']

    return (auth_token, expires)

def get_replicas(token, scope, name):
    headers = {'X-Rucio-Auth-Token': token}
    response = requests.get(url=f'{RUCIO_BASE_URI}/replicas/{scope}/{name}', headers=headers, verify=False)
    return response.text

def get_files(token, scope, name):
    headers = {'X-Rucio-Auth-Token': token}
    response = requests.get(url=f'{RUCIO_BASE_URI}/dids/{scope}/{name}/files', headers=headers, verify=False)
    lines = response.text.splitlines()
    files = [json.loads(l) for l in lines]
    return files

def get_rule(token, rule_id):
    headers = {'X-Rucio-Auth-Token': token}
    response = requests.get(url=f'{RUCIO_BASE_URI}/rules/{rule_id}', headers=headers, verify=False)
    return response.text

def add_replication_rule(token, dids, copies, rse_expression, weight=None, lifetime=None, grouping='DATASET', account=None,
                             locked=False, source_replica_expression=None, activity=None, notify='N', purge_replicas=False,
                             ignore_availability=False, comment=None, ask_approval=False, asynchronous=False, priority=3,
                             meta=None):

    data = {'dids': dids, 'copies': copies, 'rse_expression': rse_expression,
                      'weight': weight, 'lifetime': lifetime, 'grouping': grouping,
                      'account': account, 'locked': locked, 'source_replica_expression': source_replica_expression,
                      'activity': activity, 'notify': notify, 'purge_replicas': purge_replicas,
                      'ignore_availability': ignore_availability, 'comment': comment, 'ask_approval': ask_approval,
                      'asynchronous': asynchronous, 'priority': priority, 'meta': meta}
    
    headers = {'X-Rucio-Auth-Token': token}
    response = requests.post(url=f'{RUCIO_BASE_URI}/rules/', headers=headers, json=data, verify=False)
    return response.text, response.status_code


auth_token, expires = authenticate('<account>', '<identity>', '<password')
dids = get_files(auth_token, 'test', 'f3.txt')
print("DIDs: ", dids)
print(add_replication_rule(auth_token, dids=dids, rse_expression='SWAN-EOS', copies=1))
print(get_replicas(auth_token, 'test', 'f3.txt'))
