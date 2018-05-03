class EmailErrorMsg:
    '''
    EmailErrorMsg
    '''
    msg_id = 0                      #email id
    content = ''                    #email content
    time = ''                       #email time and error time
    message_type = ''               #message type, can be error or warning
    error_type = ''                 #error type: cron job erro; Hadoop/Hive/Spark; Flink; Flume; Presto; Airflow; Promertheus; Jenkins;
    subject = ''                    #email subject
    digest_content = ''              #email error digest 

    def __init__(self, id, msgcontent, subject, time):

        def findErrorType(self):
            if 'Cron <root@' in self.subject or 'PHP Fatal' in msgcontent:
                ret_err_type = 'Cron_job_failed'
            elif '[FIRING' in self.subject:
                ret_err_type = 'Promertheus'
            elif 'flink' in self.content:
                ret_err_type = 'Flink'
            elif 'flume' in self.content:
                ret_err_type = 'Flume'
            elif 'presto' in self.content:
                ret_err_type = 'Presto'
            elif 'jenkins' in self.content:
                ret_err_type = 'Jenkins'
            elif 'hadoop' in self.content or 'hive' in self.content or 'spark' in self.content:
                ret_err_type = 'Hadoop/Hive/Spark'
            else:
                ret_err_type = 'Airflow'
            return ret_err_type

    
        self.msg_id = id
        self.content = msgcontent
        self.subject = subject
        self.time = time
        self.error_type = findErrorType(self)
        if 'Cron <root@' in subject or 'PHP Fatal' in msgcontent:
            self.message_type = 'Error'
            self.digest_content = self.content.split('\n')[0]
        else:
            self.digest_content = subject
            if 'failed' in subject or '[FIRING' in subject:
                self.message_type = 'Error'
            else:
                self.message_type = 'Warning'
    
    def display(self):
        print('| Id:{3} | Time:{0} | Type:{1}| Digest Content:{2} |'.format(self.time, self.message_type, self.digest_content, self.msg_id))
    
    def displayErrorContent(self):
        print('Id:{0} Error Content: {1}'.format(self.msg_id, self.content))
    
    def displayDigestContent(self):
        print('Id:{0} Digest Content: {1}'.format(self.msg_id, self.digest_content))
    
    def displayTime(self):
        print('Id:{0} Occur Time: {1}'.format(self.msg_id, self.time))

    def getOneSummary(self):
        return ' '+str(self.time)+' ||  '+ self.digest_content

    def getDigestContent(self):
        return self.digest_content
        
    def getErrorTime(self):
        return self.time