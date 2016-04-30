import argparse
import csv
import re

parser = argparse.ArgumentParser(description="Map surveygizmo to SQL")
parser.add_argument('source', type=argparse.FileType('r'), help='The raw surveygizmo file')
args = parser.parse_args()

DISCARD_COLUMNS = [
  'Status', # not interesting, all 'Completed'
  'Contact ID', # blank
  'Legacy Comments', # blank
  'SessionID', # idk what this is, but doesn't look interesting.
  'Language', # not interesting, all have same value (English)
  'Referer', 'Extended Referer', # data isn't interesting, it's literally all Medium and a couple FB links
  'Tags', # blank
  'Longitude', 'Latitude', # private, ignore until/unless we have a use for it
  'URL Redirect', # blank
  'IP Address', # don't think we need this. could -> uuid or something if we need it
]


sourcefile = csv.DictReader(args.source)

for fieldname in sourcefile.fieldnames:
  if fieldname not in DISCARD_COLUMNS:
    print(fieldname)

"""
for fieldname in sourcefile.fieldnames:
  if fieldname not in DISCARD_COLUMNS:
    match = re.search(r'^(\d+): (.+)$', fieldname)
    question_no = match.group(1) if match else ""
    question = match.group(2) if match else fieldname
    if ":" in question:
      answer, question = question.split(":")
    else:
      answer = ""
    print("{}\t{}\t{}".format(question_no, question, answer))

"""
