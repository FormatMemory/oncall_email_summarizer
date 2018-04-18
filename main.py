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

def getOncallDays(endDay):
    '''
    To find how many days in the oncall period
    Currently oncall days: Monday 10:00 AM - Friday 10:00 AM And Friday 10:00 AM - Monday 10:00 AM
    @input the end day of an oncall period
    @return the number of oncall days in this period, if the input is not a typical oncall day, 0 will be returned
    '''
    oncallDays = 1
    weekday = endDay.weekday() #Sunday: 0, Monday: 1 etc.
    if weekday == 1:
        oncallDays = 5
    elif weekday == 5:
        oncallDays = 3
    return oncallDays

def getErrorDict(config, error_since_date, emailSenders):
    '''
    Read emails from specific email addresses and render error messages into a list of emailErrorMsg objects and return
    @Input config dictionary, error_since_date: the first day(time) of this oncall period, error msgs from which email address 
    @return a list of objects of EmailErrorMsg
    '''
    
    def getMsg(client, error_since_date, sender, SendType = 'From'):
        msg = client.search([SendType, sender, 'SINCE', error_since_date])
        print("{0} messages from {1} From {2} To {3}".format(len(msg), sender, error_since_date.strftime ("%Y-%m-%d %H:%M:%S"), datetime.datetime.now().strftime ("%Y-%m-%d %H:%M:%S")))
        return msg

    errorDict = dict()
    errorDict['cron_error'] = list()
    errorDict['hadoop_hive_hpark_error'] = list()
    errorDict['flink_error'] = list()
    errorDict['flume_error'] = list()
    errorDict['presto_error'] = list()
    errorDict['promertheus_error'] = list()
    errorDict['jenkins_error'] = list()
    errorDict['airflow_error'] = list()
    with IMAPClient(host=config['imap'],  use_uid=True) as client:
        client.login(config['username'], config['password'])
        select_info = client.select_folder('INBOX', readonly=True)
        #print(select_info)
        print('%d messages in INBOX' % select_info[b'EXISTS'])
        #dataops_msg = client.search(['FROM', 'data-ops@tantan.com'])
        msg = list()
        for sender in emailSenders:
            msg += getMsg(client, error_since_date, sender, 'From')
            msg += msg
        
        for msgid, data in client.fetch(msg, ['ENVELOPE']).items():
            envelope = data[b'ENVELOPE']
            contentList = getMsgContent(client, msgid)
            msgContent = ''.join(contentList)
            
            if isErrorOrWarning(envelope.subject.decode()):
                errObj = EmailErrorMsg(msgid, msgContent, envelope.subject.decode(), envelope.date)
                #errObj.display()
                
                if errObj.message_type == 'Error':
                    if errObj.error_type == 'Cron_job_failed':
                        errorDict['cron_error'].append(errObj)
                    elif errObj.error_type == 'Flink':
                        errorDict['flink_error'].append(errObj)
                    elif errObj.error_type == 'Flume':
                        errorDict['flume_error'].append(errObj)
                    elif errObj.error_type == 'Presto':
                        errorDict['presto_error'].append(errObj)
                    elif errObj.error_type == 'Promertheus':
                        errorDict['promertheus_error'].append(errObj)
                    elif errObj.error_type == 'Jenkins':
                        errorDict['jenkins_error'].append(errObj)
                    elif errObj.error_type == 'Hadoop/Hive/Spark':
                        errorDict['hadoop_hive_hpark_error'].append(errObj)
                    elif errObj.error_type == 'Airflow':
                        errorDict['airflow_error'].append(errObj)
    return errorDict

def getErrorReport(errorDict, errorSinceTime):
    report = '              Oncall Report: '+str(errorSinceTime)+' ~ '+str(datetime.datetime.now())+'\n'
    for errorType, errorList in errorDict.items():
        report += '* {0} Occured: {1} time(s)'.format(errorType ,len(errorDict[errorType])) + '\n'
        if len(errorDict[errorType])>0:
            report += '    Error Message Digest:' + '\n'
            count = 0
            for err in errorList:
                count += 1
                report +='               [{0}] {1}'.format(count, err.getOneSummary()) +'\n'
            report += '\n'
    return report

def main():
    config = cr.readConfig('./emailconfig.txt')
    last_N_days = getOncallDays(datetime.datetime.now()) #need to have a function to decide the time
    if last_N_days == 1:
        errorSinceTime = datetime.datetime.now() -  datetime.timedelta(days = last_N_days)
    else:
        errorSinceTime = datetime.datetime.now() -  datetime.timedelta(days = last_N_days) + datetime.timedelta(hours = 10)
    errorSource = ['root@yay161.bjs.p1staff.com', 'data-ops@tantan.com']
    errorDict = getErrorDict(config,errorSinceTime,errorSource)
    summaryReport = getErrorReport(errorDict, errorSinceTime)
    print(summaryReport)
    ##send email
    
    


if __name__ == "__main__":
    main()
    
