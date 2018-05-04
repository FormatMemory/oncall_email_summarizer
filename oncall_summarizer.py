import configParser as cr
from imapclient import IMAPClient
import datetime
import time
import email
from EmailErrorMsg import EmailErrorMsg
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def getMsgContent(client, msgid):
    content = list()
    fetch_data = client.fetch(msgid, ['RFC822'])
    msg = email.message_from_bytes(fetch_data[msgid][b'RFC822'])
    for part in msg.walk():
            #print(part.get_content_type()) #uncommand this line if you want to check conten_type
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

def isErrorOrWarning(subject, content):
    msg = ''.join(content) + subject
    if 'Cron <root@yay161>' in msg or 'Airflow alert' in msg or '[FIRING' in msg or 'PHP Fatal' in msg or 'flume backup kafka data is abnormal' in msg:
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
    if weekday == 4:
        oncallDays = 4  
    elif weekday == 0:
        oncallDays = 3
    return oncallDays

def getErrorDict(config, error_since_date, emailSenders, currentTime):
    '''
    Read emails from specific email addresses and render error messages into a list of emailErrorMsg objects and return
    @Input config dictionary, error_since_date: the first day(time) of this oncall period, error msgs from which email address 
    @return a list of objects of EmailErrorMsg
    '''
    
    def getMsg(client, error_since_date, sender, SendType = 'From'):
        msg = client.search([SendType, sender, 'SINCE', error_since_date])
        print("{0} messages from {1} From {2} To {3}".format(len(msg), sender, error_since_date.strftime ("%Y-%m-%d %H:%M:%S"), currentTime.strftime ("%Y-%m-%d %H:%M:%S")))
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
    with IMAPClient(host=config['imap'],  port=config['imap_port'] ,use_uid=True, timeout=2000) as client:
        client.login(config['username'], config['password'])
        select_info = client.select_folder('INBOX', readonly=True)
        print('%d messages in INBOX' % select_info[b'EXISTS'])

        msg = list()
        for sender in emailSenders:
            msg += getMsg(client, error_since_date, sender, 'From')
            msg += msg
        
        for msgid, data in client.fetch(msg, ['ENVELOPE']).items():
            envelope = data[b'ENVELOPE']
            contentList = getMsgContent(client, msgid)
            msgContent = ''.join(contentList)
            if isErrorOrWarning(envelope.subject.decode('utf-8'), contentList):
                errObj = EmailErrorMsg(msgid, msgContent, envelope.subject.decode(), envelope.date)
                errObj.display()                #uncommand this line if you need to have every single errorObj printed             
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

def getErrorReport(errorDict, errorSinceTime, currentTime):
    report = '                                Oncall Report: '+errorSinceTime.strftime ("%Y-%m-%d %H:%M")+' ~ '+currentTime.strftime ("%Y-%m-%d %H:%M")+'\n\n\n'
    for errorType, errorList in errorDict.items():
        report += '* {0} occured: {1} time(s)'.format(errorType ,len(errorDict[errorType])) + '\n'
        if len(errorDict[errorType])>0:
            report += '     Error Message Digest:' + '\n'
            count = 0
            for err in errorList:
                count += 1
                report +='               [{0}] {1}'.format(count, err.getOneSummary()) +'\n'
            report += '\n'
    return report

def getHtmlErrorReport(errorDict, errorSinceTime, currentTime):
    '''
    Save error report into html format
    'Oncall Report: 2018-04-28 10:00 ~ 2018-04-29 10:00'
    header = ["Error Type", "Occured Times", "Occured Time", "Error Message Digest"]
    '''
    htmlReport = ''
    for errorType, errorList in errorDict.items():
        errFirstLine = True
        if not errorList:
            curline = '<tr>'
            curline += '<td>' + errorType + '</td>'
            curline += '<td  width="30"  align="center">' + '0' + '</td>'
            curline += '<td align="center">' + 'X' + '</td>'
            curline += '<td align="center">' + '' + '</td>'
            curline += '</tr>'
            htmlReport += curline
        else:
            for err in errorList:
                if errFirstLine:
                    curline = '<tr>'
                    curline += '<td>' + errorType + '</td>'
                    curline += '<td  width="30"  align="center">' + str(len(errorDict[errorType])) + '</td>'
                    curline += '<td align="center">' + str(err.getErrorTime()) + '</td>'
                    curline += '<td>' + err.getDigestContent() + '</td>'
                    curline += '</tr>'
                    errFirstLine = False
                else:
                    curline = '<tr>'
                    curline += '<td>' + ' ' + '</td>'
                    curline += '<td width="30"  align="center">' + ' ' + '</td>'
                    curline += '<td align="center">' + str(err.getErrorTime()) + '</td>'
                    curline += '<td>' + err.getDigestContent() + '</td>'
                    curline += '</tr>'
                htmlReport += curline
    html = '''
    <html>
        <head></head>
        <body>
            <h1 align="center">Oncall Report: ''' + 'Oncall Summery From {0} To {1}'.format(errorSinceTime.strftime("%Y-%m-%d %H:%M"),currentTime.strftime("%Y-%m-%d %H:%M"))+ '''</h1>
            <table border="1">
                <tr>
                    <td align="center"><strong>Error Type</strong></td>
                    <td width="30"  align="center"><strong>Occured Times</strong></td>
                    <td align="center"><strong>Occured Time</strong></td>
                    <td align="center"><strong>Error Message Digest</strong></td>
                </tr>
                '''+htmlReport+'''
            </table>
        </body>
    </html>
    '''
    ret = html
    print(ret)
    return ret

def sendEmail(config, from_addr, to_addr, errorSinceTime, currentTime, summaryReport, isHTML = False):
    '''
    send email from address 
    '''
    with smtplib.SMTP(host=config['smtp'],port=config['smtp_port'], timeout=2000) as sender:
        sender.ehlo_or_helo_if_needed()
        sender.starttls()
        sender.login(config['username'], config['password'])
        sendMsg = MIMEMultipart()
        sendMsg['Subject'] = 'Oncall Summery From {0} To {1}'.format(errorSinceTime.strftime ("%Y-%m-%d %H:%M"),currentTime.strftime ("%Y-%m-%d %H:%M"))
        sendMsg['From'] = from_addr
        sendMsg['To'] = to_addr
        if isHTML:
             emailContent = MIMEText(summaryReport, 'html')
        else:
             emailContent = MIMEText(summaryReport, 'plain')
        sendMsg.attach(emailContent)
        text = sendMsg.as_string()
        sender.sendmail(from_addr, to_addr, text)
        sender.quit()
    print('Email sent...')
    
def main():
    config = cr.readConfig('./data_black_hole.txt')
    #config = cr.readConfig('./emailconfig.txt')
    currentTime = datetime.datetime.now()
    last_N_days = getOncallDays(currentTime)

    # if last_N_days == 1:
    #     errorSinceTime = currentTime -  datetime.timedelta(days = last_N_days)
    # else:
    #     errorSinceTime = currentTime -  datetime.timedelta(days = last_N_days) + datetime.timedelta(hours = 10)
    errorSinceTime = currentTime -  datetime.timedelta(days = last_N_days) - datetime.timedelta(days = 5)
    errorSource = ['root@yay161.bjs.p1staff.com', 'data-ops@tantan.com','prometheus@p1.com']
    errorDict = getErrorDict(config,errorSinceTime,errorSource,currentTime)
    #summaryReport = getErrorReport(errorDict, errorSinceTime, currentTime)
    summaryReport2 = getHtmlErrorReport(errorDict, errorSinceTime, currentTime)
    print(summaryReport2)
    #print(summaryReport)
    if last_N_days == 1:
        sendEmail(config, 'data-eng-blackhole@p1.com', 'david@p1.com', errorSinceTime, currentTime, summaryReport2,isHTML = True)
        #sendEmail(config, 'david@p1.com', 'david@p1.com', errorSinceTime, currentTime, summaryReport2)
        #print('Done...')
    else:
        sendEmail(config, 'data-eng-blackhole@p1.com', 'david@p1.com', errorSinceTime, currentTime, summaryReport2, isHTML = True)  #uncommand this line if you want to send an email for only one day's report
        print('Email not send...')


if __name__ == "__main__":
    main()
    
