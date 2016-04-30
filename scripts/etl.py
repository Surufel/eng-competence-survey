#! env python3
"""

This script is for my own use - it takes the raw CSV as surveygizmo outputs it, cleans the data to remove
personal information like IP addresses and such, and creates a SQLite db for Jupyter use.

"""

import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser(description="Process raw surveygizmo file into a usable format")
parser.add_argument('source', type=argparse.FileType('r'), help='The raw surveygizmo file')
parser.add_argument('destination', help='The directory you want me to generate files in')
parser.add_argument('--public', action='store_true', help='Scrub the data of everyone who asked that their data not be shared')
args = parser.parse_args()


destdir = Path(args.destination)
project_dir = Path("..") # eh

if not destdir.exists():
  if input("The directory {} doesn't exist. Should I create it? (y/n)".format(destdir)).lower() == 'y':
    destdir.mkdir(parents=True, exist_ok=False)
  else:
    raise SystemExit("ok, quitting")

destfilename = destdir.joinpath("output{}.csv".format('_public' if args.public else ''))

if destfilename.exists():
  if input("The file {} already exists. Imma gonna delete it, that ok? (y/n)".format(destfilename)).lower() == 'y':
    destfilename.unlink()
  else:
    raise SystemExit("ok, quitting")

# check we're not writing private data to a potentially public place
if not args.public and str(project_dir.resolve()) in str(destdir.resolve()):
  raise SystemExit("Hey, don't save private data inside the git repo, you might accidentally commit it. ")

if args.public:
  print("Writing public data")


sourcefile = csv.DictReader(args.source)

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

IS_PUBLIC = "36: Can I include your responses in a public data set, so that others can analyze this data too? (I’ll take out all personally identifiable information.)"
YES_IS_PUBLIC = "Yes, please include them"


with open(str(destfilename), 'w') as destfile:
    OUTPUT_FIELDNAMES = [fieldname for fieldname in sourcefile.fieldnames if fieldname not in DISCARD_COLUMNS]
    writer = csv.DictWriter(destfile, fieldnames=OUTPUT_FIELDNAMES)

    writer.writeheader()

    for row in sourcefile:
      if args.public and sourcefile[IS_PUBLIC] != YES_IS_PUBLIC:
        continue

      writer.writerow({field: row[field] for field in OUTPUT_FIELDNAMES})


print("done!")
