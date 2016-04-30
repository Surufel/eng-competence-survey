from sqlalchemy import *
from pathlib import Path

COL_CSV_FILENAME = "Original CSV fieldname"
COL_TABLE = "Table"
COL_COLUMN = "Column Name"
COL_TYPE = "Type (if not str)"


def determine_column_type(name, typename):
  if 'writein' in name:
    return Text()
  elif typename == "boolean":
    return Boolean()
  elif typename == "datetime":
    return DateTime()
  else:
    return String(200)


def add_table(metadata, table_name, columns):
  args = [
    table_name,
    metadata,
    Column('id', Integer, primary_key=True),
    Column('request_id', Integer),
  ]

  for column in columns:
    column_name, column_typename = column
    column_type = determine_column_type(column_name, column_typename)
    args.append(Column(column_name, column_type))

  Table(*args)

def extract_column_info(row):
  name = row[COL_COLUMN]

  if row[COL_TYPE] == "" or not row[COL_TYPE]:
    type = "str"
  else:
    type = row[COL_TYPE]

  return (name, type,)


def reset_files_if_necessary(destdir, destfilename, is_public):
  project_dir = Path("..") # eh magic


  if not destdir.exists():
    if input("The directory {} doesn't exist. Should I create it? (y/n)".format(destdir)).lower() == 'y':
      destdir.mkdir(parents=True, exist_ok=False)
    else:
      raise SystemExit("ok, quitting")


  if destfilename.exists():
    if input("The file {} already exists. Imma gonna delete it, that ok? (y/n)".format(destfilename)).lower() == 'y':
      destfilename.unlink()
    else:
      raise SystemExit("ok, quitting")

  # check we're not writing private data to a potentially public place
  if not is_public and str(project_dir.resolve()) in str(destdir.resolve()):
    raise SystemExit("Hey, don't save private data inside the git repo, you might accidentally commit it. ")

