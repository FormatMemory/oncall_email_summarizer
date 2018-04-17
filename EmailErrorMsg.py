class EmailErrorMsg:
    '''
    EmailErrorMsg contains message id,
    message type
    message content
    message time
    '''
    msg_id = 0                      #email id
    content = ''                    #email content
    time = ''                       #email time and error time
    message_type = ''               #message type, can be error or warning
    error_type = ''                 #error type: cron job erro; Hadoop/Hive/Spark; Flink; Flume; Presto; Airflow; Promertheus; Jenkins;
    subject = ''                    #email subject
    digest_content = ''              #email error digest 

    def __init__(self, id, msgcontent, subject, time):
        def isErrorOrWarning(self, subject):
            if 'Cron <root@yay161>' in subject or 'Airflow alert:' in subject:
                return True
            else:
                return False
        def findErrorType(self):
            if 'Cron <root@yay161>' in self.subject:
                ret_err_type = 'Cron job failed'
            elif 'Hadoop' in self.content or 'Hive' in self.content or 'Spark' in self.content:
                ret_err_type = 'Hadoop/Hive/Spark'
            elif 'Flink' in self.content:
                ret_err_type = 'Flink'
            elif 'Flume' in self.content:
                ret_err_type = 'Flume'
            elif 'Presto' in self.content:
                ret_err_type = 'Presto'
            elif 'Promertheus' in self.content:
                ret_err_type = 'Promertheus'
            elif 'Jenkins' in self.content:
                ret_err_type = 'Jenkins'
            else:
                ret_err_type = 'Airflow'
            return ret_err_type

            

        if isErrorOrWarning(self, subject):
            self.msg_id = id
            self.content = msgcontent
            self.subject = subject
            self.time = time
            self.error_type = findErrorType(self)
            if 'Cron <root@yay161>' in subject:
                self.message_type = 'Error'
                self.digest_content = self.content.split('\n')[0]
            else:
                self.digest_content = subject
                if '[up_for_retry]' in subject:
                    self.message_type = 'Warning'
                else:
                    self.message_type = 'Error'
                
        else:
            return
    
    def display(self):
        print('| Time:{0} | Type:{1}| Subject:{2} | Id:{3} |'.format(self.time, self.message_type, self.subject, self.msg_id))
    
    def displayErrorContent(self):
        print('Id:{0} Error Content: {1}'.format(self.msg_id, self.content))
    
    def displayDigestContent(self):
        print('Id:{0} Digest Content: {1}'.format(self.msg_id, self.digest_content))