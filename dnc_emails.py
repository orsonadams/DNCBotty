from __future__ import print_function
import requests
import pdb
import os
import sys
import urllib
import grequests
import json
import time
import argparse


POOL_SIZE  = 10
URL = "https://wikileaks.org/dnc-emails/emailid/"
HOME = os.path.expanduser("~")
DNC_DIR  = os.path.join(HOME, "dnc_emails", "emails")
SLEEP = 20
CHUNK_TO_SLEEP = 100

START = 1
ASYNC = 0
MAX_FAIL = 10


def main():

	# for some odd reason I cant define this with the other constants
	MAX_EMAILS = 3
	# using argparse to let use import start and end emailsids

	parser = argparse.ArgumentParser(description="GET DNC EMAILS.")
	parser.add_argument("--start", dest="start", default=START,
	                    help="emailid to start the crawl at")
	parser.add_argument("--end", dest="end", default= MAX_EMAILS,
						help="emailid to end the crawl at")
	parser.add_argument("--async", dest="async", default=ASYNC, 
						help="1, 0 for use of async request or not respectively."
						"Use this if you dont care about the order of the requests")
	parser.add_argument("---data-dir", dest=DNC_DIR, default=DNC_DIR,
						help="Give te directory of where to store the emails")

	args = parser.parse_args()
	# set user agent
	s = requests.session()
	# being polite : we"ll let wikileks know who we are and where thdey can find more info
	s.headers.update({"User-Agent": "Requests-- DNCBotty: A collecting emails" 
						"for a quick project. https://github.com/DNCBotty"})

		
	# create directory isit not exit
	try:
		if not os.path.exists(DNC_DIR):
			os.makedirs(DNC_DIR)
			# 
	except OSError:
		print("OSError")
		sys.exit(1)
	
	# create async requests using
	# using map instead of imap so I can match the response to the emailid
	# NOTE ( if aysnc then you can"t (that i know of) recover which requests failed )
	if args.end < MAX_EMAILS:
		MAX_EMAILS = args.end

	rs = (grequests.get(u, session=s) for  u in (URL + str(i) for i in xrange(START, MAX_EMAILS+1 )))
	# async requests with grequests.imap, if user wants.
	if args.async:
		resp = grequests.map(rs, size=POOL_SIZE)
	else:
		resp = grequests.imap(rs, size=POOL_SIZE)

	# loop through responses
	for (i, r) in zip(xrange(1, MAX_EMAILS+1), resp):
		if r.ok:
			# reset fail_count if responses are "ok" and fail_count > MAX_FAIL
			fail_count = 0
			json.dump({"data" : r.text}, open(os.path.join(DNC_DIR,  str(i) + ".json"), "w"))
		else:
			# simple write the emailID of the request that failed to failed_emails.txt file
			try:
				print("Failed to get email with email id {}".format(i), 
					file=open(os.path.join(DNC_DIR, "failed_emails.txt", "w")))
			except Exception as e:
				print(e)
				# if fail_count emails fail consecutively kill script
				fail_count+=1
				if fail_count > MAX_FAIL: 
					sys.exit("responses failed %s consecutive times..Quitinsg" %MAX_FAIL)
			finally:
				# back-0ff for courtesy 
				if (i % CHUNK_TO_SLEEP) & (i != 0):
						time.sleep(SLEEP)

if __name__ == "__main__":
	main()