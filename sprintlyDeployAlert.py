#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
import argparse
import re
import sys
import logging
import urllib
import urllib2

# force utf-8 encoding
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig()
logger = logging.getLogger(__name__)

# constants
INDEX_SPRINTLY_DEPLOY_URL = 'https://sprint.ly/api/products/{}/deploys.json'
SPRINTLY_USER_ID = 'your.email@email.com'
SPRINTLY_USER_KEY = 'xxxxxxxxxxxxxxxxx'
DEPLOY_ENV = 'stage via Jenkins auto-deploy'

def process(productNumber, changeLogPath):
    commit_msg_file = open(changeLogPath, 'r')
    refs = set()
    for line in commit_msg_file:
      if contains_sprintly_number(line):
        refs = refs.union(set(re.findall('\d+', line)))
    if len(refs) != 0:
        send_update(set(refs), productNumber)


def contains_sprintly_number(changelog):
    """
    If the message contains (at any position) a sprint.ly
    keyword followed by a space, pound, number, then accept
    the message as is and return True.

    Otherwise, return false.
    """
    valid_keywords = ['close', 'closes', 'closed', 'fix', 'fixed', 'fixes', 'addresses', 're', 'ref', 'refs', 'references', 'see', 'breaks', 'unfixes', 'reopen', 'reopens', 're-open', 're-opens']
    logLower = changelog.lower()

    try:
        # match any keyword followed by a pound-number-(space or period)
        pattern = r'.*\b(' + '|'.join(valid_keywords) + r')\b\s(#[0-9]+([\.\s,]|$)).*'
        result = re.search(pattern, logLower)
        if result:
            return True

    except Exception as e:
        pass
    return False

def send_update(storynumbers, productNumber):
    values = {'environment' : DEPLOY_ENV,
              'numbers' : ','.join(storynumbers) }
    data = urllib.urlencode(values)
    url = INDEX_SPRINTLY_DEPLOY_URL.format(productNumber)
    req = urllib2.Request(url, data)
    base64string = base64.encodestring(
                '%s:%s' % (SPRINTLY_USER_ID, SPRINTLY_USER_KEY))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    response = urllib2.urlopen(req)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sends deploy commands to Sprint.ly')
    parser.add_argument('-p','--product', help='Sprintly product number', required=True)
    parser.add_argument('-c','--changelog', help='Path to the changelog xml file', required=True)
    args = parser.parse_args()
    process(args.product, args.changelog)
