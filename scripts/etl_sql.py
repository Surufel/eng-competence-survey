#! env python3
import argparse
import csv
from sqlalchemy.schema import MetaData
from collections import defaultdict

from lib import *


parser = argparse.ArgumentParser(description="Map surveygizmo to SQL")
parser.add_argument('mapper', type=argparse.FileType('r'), help='The mapping file')
parser.add_argument('datafile', type=argparse.FileType('r'), help='The raw surveygizmo file')
parser.add_argument('destination', help='The directory you want me to generate files in')
parser.add_argument('--public', action='store_true', help='Scrub the data of everyone who asked that their data not be shared')
args = parser.parse_args()

# --- setup
destdir = Path(args.destination)
destfilename = destdir.joinpath("results{}.db".format('_public' if args.public else ''))

# this makes sure all the paths are present and deletes any old files if necessary
reset_files_if_necessary(destdir, destfilename, args.public)

# sqlalchemy setup
metadata = MetaData()
engine = create_engine("sqlite:///{}/{}".format(destdir.resolve(), destfilename.name))

# --- end setup

CSV_FIELD_MAPPING = {}
SOFTWARE_ENG_TRAITS_MAPPING = {}

# --- create empty db
mapperfile = csv.DictReader(args.mapper)

# this just walks down the mapping file, and builds a list of database tables + columns
current_table_name = None
columns = []

for row in mapperfile:
  row_csv_fieldname = row[COL_CSV_FIELDNAME]
  row_table_name = row[COL_TABLE]
  row_column_name = row[COL_COLUMN]
  row_type = row[COL_TYPE]

  if current_table_name == row_table_name:
    columns.append(extract_column_info(row))
  else:
    # tablename changed, that means
    if current_table_name:
      add_table(metadata, current_table_name, columns)

    current_table_name = row_table_name
    columns = [extract_column_info(row)]

  # i should probably put this in a different file but fuckit
  if row_table_name == SOFTWARE_ENG_TRAITS_TABLENAME:
    SOFTWARE_ENG_TRAITS_MAPPING[row[COL_ORIGINAL_ANSWER]] = row_column_name

  # map csv fieldname to table/col
  CSV_FIELD_MAPPING[row_csv_fieldname] = {
    'table': row_table_name,
    'column': row_column_name,
    'datatype': row_type or "str"
  }

# don't forget to add the last one :)
add_table(metadata, current_table_name, columns)

# this actually creates the database
metadata.create_all(engine)
metadata.reflect(bind=engine)

print("Created empty db at {}".format(destfilename.resolve()))
# -- end create empty db

# -- start db load
print("Starting load from {}".format(args.datafile))

datafile = csv.DictReader(args.datafile)

conn = engine.connect()

for row in datafile:
  sql_data = defaultdict(defaultdict)

  for fieldname in datafile.fieldnames:
    if fieldname in CSV_FIELD_MAPPING:
      tablename = CSV_FIELD_MAPPING[fieldname]['table']
      column = CSV_FIELD_MAPPING[fieldname]['column']
      datatype = CSV_FIELD_MAPPING[fieldname]['datatype']
      value = cast_string_to(row[fieldname], datatype)

      sql_data[tablename][column] = value

  for tablename in sql_data.keys():
    data = sql_data[tablename]
    conn.execute(table.insert(), data)

print("done!")

