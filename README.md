# Oncall email summarizer

To run this program: ```python oncall_summarizer.py```

Python 3.6 or above is needed

This tool renders and summarizes our oncall emails and then sends the summary to a specific email address(group).

To use this, you need to have IMAPClient package installed:
```pip install imapclient```

You also need to make one config file according to your own configuration follow the format below:

```
IMAP:********
imap_port:********
SMTP:********
smtp_port:********
username:********
password:********
```

