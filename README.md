# Oncall email summarizer


This tool renders and summarizes our oncall emails and then send the summary to a specific email address(group).


To use this, you need to have IMAPClient package installed:
```pip install imapclient```

You also need to make one config file according to your own configuration in the same folder as main.py follow the format below:

```
IMAP:********
imap_port:********
SMTP:********
smtp_port:********
username:********
password:********
```

