## DNCBotty:

A quick script to the dnc emails leaked by wikileak 
[WikiLeaks](https://wikileaks.org/dnc-emails) 

How to use:

* pip install -r requirements.txt

### BASIC USAGE:

* To request all the emails you dont have in your data-dir use:
python dnc_emails.py --use-missing

* If you would like to use a range of emailids use:
python dnc_emails.py --start [START] end --end [END]

* the script creates a directory "dnc_emails/emails" where it stores are the
json emails. Use --data-dir to specify thee full path to a different location

### ADVANCED USAGE:
* For aysnc requests use --async. Note that if you do use --async then you will not be able to recover the requests that failed in a particular session.

NO warrenty or guarantee. Use at your own risk and all that jazz.

