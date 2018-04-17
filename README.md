# Oncall email summarizer


This tool renders our oncall emails and do a summary then send the summary to a specific email address(group).


To use this, you need to have IMAPClient package installed:
```pip install imapclient```

You need to make one config file according to your own configuration follow the format below:

```
IMAP:********
imap_port:********
SMTP:********
smtp_port:********
username:********
password:********
```

