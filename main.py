import configParser as cr
from imapclient import IMAPClient
import datetime
import time
import email
from EmailErrorMsg import EmailErrorMsg

def getMsgContent(client, msgid):
    content = list()
    fetch_data = client.fetch(msgid, ['RFC822'])
    msg = email.message_from_bytes(fetch_data[msgid][b'RFC822'])
    for part in msg.walk():
            #print(part.get_content_type())
            if part.get_content_type() == 'text/plain' or part.get_content_type()== 'text/html': # ignore attachments/html  text/plain
                body = part.get_payload(decode=True)
                content.append(body.decode('utf-8'))
                '''
                #leave this part just incase in the future we want to save the msg into file
                save_string = str("./Dumpgmailemail_" + error_since_date.strftime ("%Y-%m-%d %H:%M:%S") + ".eml")
                # location on disk
                myfile = open(save_string, 'a')
                myfile.write(body.decode('utf-8'))
                # body is again a byte literal
                myfile.close()
                '''
            else:
                continue
    return content

def isErrorOrWarning(subject):
    if 'Cron <root@yay161>' in subject or 'Airflow alert:' in subject:
        return True
    else:
        return False

def oncallDays():
    '''
    @return the oncall first day
    '''
    pass
 

def main():
    config = cr.readConfig('./emailconfig.txt')
    last_N_days = 7 #need to have a function to decide the time
    error_since_date = datetime.datetime.now() -  datetime.timedelta(days = last_N_days) + datetime.timedelta(hours = 10)
    error_dict = dict()
    # email_msgs_list = list()
    error_dict['cron_error'] = list()
    error_dict['hadoop_hive_hpark_error'] = list()
    error_dict['flink_error'] = list()
    error_dict['flume_error'] = list()
    error_dict['presto_error'] = list()
    error_dict['promertheus_error'] = list()
    error_dict['jenkins_error'] = list()
    error_dict['airflow_error'] = list()
    
    with IMAPClient(host=config['imap'],  use_uid=True) as client:
        client.login(config['username'], config['password'])
        select_info = client.select_folder('INBOX', readonly=True)
        #print(select_info)
        #print('%d messages in INBOX' % select_info[b'EXISTS'])
        #dataops_msg = client.search(['FROM', 'data-ops@tantan.com'])
        dataops_msg = client.search(['FROM', 'data-ops@tantan.com', 'SINCE',error_since_date])
        crontab_msg = client.search(['FROM', 'root@yay161.bjs.p1staff.com', 'SINCE',error_since_date])
        msg = dataops_msg + crontab_msg
        print("{0} cron_tab messages from data-ops@tantan.com From {1} To {2}".format(len(dataops_msg), error_since_date.strftime ("%Y-%m-%d %H:%M:%S"), datetime.datetime.now().strftime ("%Y-%m-%d %H:%M:%S")))
        print("{0} airflow git messages from data-ops@tantan.com From {1} To {2}".format(len(crontab_msg), error_since_date.strftime ("%Y-%m-%d %H:%M:%S"), datetime.datetime.now().strftime ("%Y-%m-%d %H:%M:%S")))
        #print(dataops_msg)
        
        for msgid, data in client.fetch(msg, ['ENVELOPE']).items():
            envelope = data[b'ENVELOPE']
            contentList = getMsgContent(client, msgid)
            msgContent = ''.join(contentList)
            
            if isErrorOrWarning(envelope.subject.decode()):
                errObj = EmailErrorMsg(msgid, msgContent, envelope.subject.decode(), envelope.date)
                #errObj.display()
                #email_msgs_list.append(errObj)
                if errObj.message_type == 'Error':
                    if errObj.error_type == 'Cron_job_failed':
                        error_dict['cron_error'].append(errObj)
                    elif errObj.error_type == 'Hadoop/Hive/Spark':
                        error_dict['hadoop_hive_hpark_error'].append(errObj)
                    elif errObj.error_type == 'Flink':
                        error_dict['flink_error'].append(errObj)
                    elif errObj.error_type == 'Flume':
                        error_dict['flume_error'].append(errObj)
                    elif errObj.error_type == 'Presto':
                        error_dict['presto_error'].append(errObj)
                    elif errObj.error_type == 'Promertheus':
                        error_dict['promertheus_error'].append(errObj)
                    elif errObj.error_type == 'Jenkins':
                        error_dict['jenkins_error'].append(errObj)
                    elif errObj.error_type == 'Airflow':
                        error_dict['airflow_error'].append(errObj)
    for errorType, errorList in error_dict.items():
        print('{0} Error Occured: {1} time(s)'.format(errorType ,len(error_dict[errorType])))
        if len(error_dict[errorType])>0:
            print('Error Message Digest:')
            count = 0
            for err in errorList:
                count += 1
                print('               [{0}] {1}'.format(count, err.getOneSummary()))
            print('\n') 
        print('\n')
            # if 'Airflow alert:' in envelope.subject.decode():
            #     print('ID #%d: "%s" received %s' % (msgid, envelope.subject.decode(), envelope.date))
            #     i = get_msg_content(client, msgid)
            #     print(i)
            #     print('\n\n\n\n\n\n')
            # if 'Cron <root@yay161>' in envelope.subject.decode():
            #     print('ID #%d: "%s" received %s' % (msgid, envelope.subject.decode(), envelope.date))
            #     i = get_msg_content(client, msgid)
            #     print(i)
            #     print('\n\n\n\n\n\n')
    


if __name__ == "__main__":
    main()
    