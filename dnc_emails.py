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
ASYNC = False
MAX_FAIL = 10
MAX_EMAILS = 19252 # source : https://wikileaks.org/dnc-emails/


def detect_missing():

	""" return a generator of all the ids that are not in the emails directory """
	try:
		f = os.walk(DNC_DIR).next()
		# assumes file names are "x.json" where x can be coerced to an int
	except IOError:
		return 
	else:
		collected = set(int(x.split(".")[0]) for x in f[2])
	return (ident for ident in xrange(1, MAX_EMAILS) if ident not in collected)



def main():
	

	parser = argparse.ArgumentParser(description="GET DNC EMAILS.")
	parser.add_argument("--start", dest="start", default=START,
						help="emailid to start the crawl at")
	parser.add_argument("--end", dest="end", default= MAX_EMAILS,
						help="emailid to end the crawl at")
	parser.add_argument("--async", dest="async", const=1, nargs="?", default=ASYNC, 
						help="1, 0 for use of async request or not respectively."
						"Use this if you dont care about the order of the requests")
	parser.add_argument("--data-dir", dest=DNC_DIR, default=DNC_DIR,
						help="Give te directory of where to store the emails")
	parser.add_argument("--use-missing", dest="use_missing", default=True, const=1, nargs="?",
						help="True or False. find the ID of the missing emails from data-dir and"\
							"request those. --start and --end options will be ignored")

	args = parser.parse_args()

	# being polite : we"ll let wikileaks know who we are and where they can find more info.
	s = requests.session()
	s.headers.update({"User-Agent": "Requests-- DNCBotty: A Collecting emails" 
						"for a quick project. https://github.com/DNCBotty"})
	try:
		if not os.path.exists(DNC_DIR):
			os.makedirs(DNC_DIR)
	except OSError:
		print("OSError while trying to create %s. Quitting" %DNC_DIR)
		sys.exit(1)
	
	#
	# create async requests using grequests
	# using map instead of imap so I can match the response to the emailid
	# NOTE ( if aysnc then you can't (that i know of) recover which requests failed
	# by matching the file name to the emailID. grequests.map makes it possible becasuse request are sequential. )
	#
	#

	# try to detect that user wants range warn that user range will trump --use-missing
	if args.use_missing & args.end < MAX_EMAILS:
		print("WARNING: Seems like your specifing a range and --use-missing. Using specified range.")

	if args.use_missing & args.async:
		raise TypeError("can't gaurentee the order of results with async. So missing will be devilishly deceitful")
	elif args.use_missing  & ( not args.async ):
		missing = detect_missing()
	else:
		if args.end < MAX_EMAILS:
			max_emails = args.end
		if args.start:
			start = args.start
		missing = xrange(start, max_emails+1)

	rs = (grequests.get(u, session=s) for u in (URL + str(i) for i in missing))
	# async requests with grequests.imap, if user wants.
	if not args.async:
		resp = grequests.map(rs, size=POOL_SIZE)
	else:
		resp = grequests.imap(rs, size=POOL_SIZE)

	# loop through responses
	for (i, r) in zip(missing, resp):
		if r.ok:
			# reset fail_count if responses are "ok" and fail_count < MAX_FAIL
			fail_count = 0
			json.dump({"data" : r.text}, open(os.path.join(DNC_DIR,  str(i) + ".json"), "w"))
		else:
			# simply write the emailID of the request that failed to failed_emails.txt file as backup
			try:
				print("Failed to get email with email id {}".format(i), 
					file=open(os.path.join(DNC_DIR, "failed_emails.txt"), "w"))
				# .. if  being throttled ??
				fail_count+=1
				if fail_count > MAX_FAIL: 
					sys.exit("responses failed %s consecutive times..Quitting" %MAX_FAIL)
			except Exception as e:
				print(e)
			finally:
				# back-0ff for courtesy 
				if (i % CHUNK_TO_SLEEP) & (i != 0):
					time.sleep(SLEEP)


if __name__ == "__main__":
	main()