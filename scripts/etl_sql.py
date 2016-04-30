#! env python3
import argparse
import csv
from sqlalchemy.schema import MetaData

from lib import *


parser = argparse.ArgumentParser(description="Map surveygizmo to SQL")
parser.add_argument('source', type=argparse.FileType('r'), help='The raw surveygizmo file')
parser.add_argument('destination', help='The directory you want me to generate files in')
parser.add_argument('--public', action='store_true', help='Scrub the data of everyone who asked that their data not be shared')
args = parser.parse_args()

# --- setup
destdir = Path(args.destination)
destfilename = destdir.joinpath("results{}.db".format('_public' if args.public else ''))

reset_files_if_necessary(destdir, destfilename, args.public)

metadata = MetaData()

# --- end setup


# --- create empty db
sourcefile = csv.DictReader(args.source)

table_name = None
columns = []

for row in sourcefile:

  if table_name == row[COL_TABLE]:
    columns.append(extract_column_info(row))
  else:
    # tablename changed,
    if table_name:
      add_table(metadata, table_name, columns)

    table_name = row[COL_TABLE]
    columns = [extract_column_info(row)]

add_table(metadata, table_name, columns)

engine = create_engine("sqlite:///{}/{}".format(destdir.resolve(), destfilename.name))
metadata.create_all(engine)

print("Created empty db at {}".format(destfilename.resolve()))
# -- end create empty db

# - 



print("done!")

