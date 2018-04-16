import os
import sys

configFile = './emailconfig.txt'

#check configFilePath
if not os.path.isfile(configFile):
    sys.exit('Config file not found...')

with open(configFile, 'r') as f:
    lines = f.readlines()

if not lines:
    sys.exit('Config file is empty')

config = dict()
config['imap'] = lines[0].replace('IMAP','').replace(' ', '').rstrip()
config['imap_port'] = lines[1].replace('imap_port','').replace(' ', '').rstrip()
config['smtp'] = lines[2].replace('SMTP','').replace(' ', '').rstrip()
config['smtp_port'] = lines[3].replace('smtp_port','').replace(' ', '').rstrip()
config['username'] = lines[4].replace('username','').replace(' ', '').rstrip()
config['password'] = lines[5].replace('password','').replace(' ', '').rstrip()

#print(config)

