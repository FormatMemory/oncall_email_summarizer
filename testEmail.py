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
config['imap'] = lines[0].replace('IMAP:','').replace(' ', '').rstrip()
config['imap_port'] = lines[1].replace('imap_port:','').replace(' ', '').rstrip()
config['smtp'] = lines[2].replace('SMTP:','').replace(' ', '').rstrip()
config['smtp_port'] = lines[3].replace('smtp_port:','').replace(' ', '').rstrip()
config['username'] = lines[4].replace('username:','').replace(' ', '').rstrip()
config['password'] = lines[5].replace('password:','').replace(' ', '').rstrip()

#print(config)

from imapclient import IMAPClient
with IMAPClient(host=config['imap'],  use_uid=True) as client:
#server = IMAPClient(config['imap'], use_uid=True)
#server.login(config['username'], config['password'])
    client.login(config['username'], config['password'])
    select_info = client.select_folder('INBOX')

#select_info = server.select_folder('INBOX')
    print('%d messages in INBOX' % select_info[b'EXISTS'])

    messages = client.search(['FROM', 'data-ops@tantan.com'])
    print("%d messages from data-ops@tantan.com" % len(messages))
    print(messages)
    sys.exit("aaa")
    for msgid, data in client.fetch(messages, ['ENVELOPE']).items():
        envelope = data[b'ENVELOPE']
        #envelope.
        print('ID #%d: "%s" received %s' % (msgid, envelope.subject.decode(), envelope.date))

#server.logout()
