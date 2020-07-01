import subprocess
import json
from time import sleep

def login_az(params):
	auth = '''
	az login --service-principal -u {user} -p {password} --tenant {tenant} > /dev/null
	'''.format(**params)
	az_login = subprocess.call(auth, shell=True)
	return az_login

def logout_az():
	subprocess.call('az logout', shell=True)

def subscriptions_dict():
	subs_dict={}
	subscriptions = json.loads(subprocess.check_output('az account list --refresh', shell=True).decode('utf-8'))
	for sub in subscriptions:
		if sub['state'] == 'Enabled':
			subs_dict[sub['name']] = sub['id']
	return subs_dict

def switch_sub(sub_id):
	switch_cmd = 'az account set -s ' + sub_id
	subprocess.call(switch_cmd, shell=True)
#	subprocess.Popen(["az", "account", "set", "-s", sub_id], shell=True)
	sleep(3)
