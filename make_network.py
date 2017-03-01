import os
import json
from collections import defaultdict
import re
from bs4 import BeautifulSoup

import pdb
import sys

EMAILS = os.path.join(os.path.expanduser("~"), "dnc_emails", "emails")
def read_emails(files):
    for g in files:
        with open(EMAILS + "/" + g) as js:
            data = json.loads(js.read())
            text = BeautifulSoup(data["data"], "lxml").find(id="content")
            if not text:
                continue
            words = text.text
#             print(text)
            yield re.findall(r'From:\s?.*?Subject:\s', words, re.S)



def get_from_to_date(samp):
    for x in samp:
        y = re.sub(r'[\t\n]{1,}', ' ', x)
        y = re.sub(r'From:\s{1,}', 'From:', y)
        y = re.sub(r'To:\s{1,}', 'To:', y)
        y = re.sub(r'Date:\s{1,}', 'Date:', y)
        y = re.sub(r'Sent:\s{1,}', 'Sent:', y)
        fm = re.match(r'(From.*?(?=(To|Sent|Date)))', y)
        if fm:
            sender = fm.group().strip()
        else:
            sender = None
        to = re.search(r'To.*?(?=(Date|Sent|Subject))', y)
        if to:
            receive = to.group().strip()
        else:
            recieve = None
        date = re.search(r'(Date|Sent).*?(?=(Subject|To))', y)
        if date:
            sent = date.group().strip()
        else:
            sent = None
        yield (sender, receive, sent)

def splitter(data):

    origin = data.next()
    if origin[0]:
        origin_from = origin[0].split(":")[1].strip().lower() # from sender
        origin_to = [t.strip().lower() for t in origin[1].split(":")[1].split(",")] # get original receiver(s)
        yield origin_from, origin_to
    for x in data:
        if x[0]:
            s = x[0].split(":")[1]
            senders = [se.strip().lower() for se in s.split(";")]
            receivers = [y.strip().lower() for e in x[1].split(":")[1:] for y in e.split(";")]
        else:
            senders, receivers = None, None
        yield senders, receivers


def main():
    f = os.walk(EMAILS)
    files = f.next()[2]

    global graph
    graph = defaultdict(lambda: [])
    # process each email in a stram
    emails = read_emails(files)
    for email in emails:
        unclean = get_from_to_date(email)
        clean = splitter(unclean)
        for x in clean:
            print(x)
            print("-----------------------")
            if not x[0]:
                continue
            try:
                if len(x[0]) <2:
                    graph[x[0][0]].extend(x[1])
                else:
                    # handle case of multiple from (rate)
                    for y in x[0]:
                        graph[x[0][0]].extend(x[1])
            except IndexError:
                print(x[0])
                # sys.exit(1)
                continue


    json.dumps(graph)

if __name__ == "__main__":
    main()
