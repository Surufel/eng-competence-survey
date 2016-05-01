from sqlalchemy import *
from pathlib import Path
from datetime import datetime

COL_CSV_FIELDNAME = "Original CSV fieldname"
COL_TABLE = "Table"
COL_COLUMN = "Column Name"
COL_TYPE = "Type (if not str)"
COL_ORIGINAL_ANSWER = "Original answer"

TRUE_VALUES = ['Yes', 'Yes, please include them']
FALSE_VALUES = ['No', "No, keep them private", '']

BOOLEAN_TYPE = 'boolean'
DATETIME_TYPE = 'datetime'
INT_TYPE = 'int'
STR_TYPE = 'str'
TRUTHY_TYPE = 'truthy' # if there's any value at all, this resolves to true

DATE_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"

SOFTWARE_ENG_TRAITS_TABLENAME = 'q1_competent_software_engineer_traits'


def cast_to_sql_column_type(name, typename):
  if 'writein' in name:
    return Text()
  elif typename == BOOLEAN_TYPE:
    return Boolean()
  elif typename == DATETIME_TYPE:
    return DateTime()
  elif typename == INT_TYPE:
    return Integer()
  elif typename == TRUTHY_TYPE:
    return Boolean()
  else:
    return String(200)

def cast_string_to(string, typename):
  if typename == STR_TYPE:
    return string
  elif typename == INT_TYPE:
    return int(string)
  elif typename == DATETIME_TYPE:
    # todo is this pacific time??
    return datetime.strptime(string, DATE_FORMAT_STRING)
  elif typename == BOOLEAN_TYPE:
    if string in TRUE_VALUES:
      return True
    elif string in FALSE_VALUES:
      return False
    else:
      raise ValueError("I can't cast '{}' to boolean".format(string))
  elif typename == TRUTHY_TYPE:
    return bool(string)
  else:
    raise ValueError("I don't know how to handle type {}".format(typename))

def add_table(metadata, table_name, columns):
  args = [
    table_name,
    metadata,
    Column('id', Integer, primary_key=True),
    Column('request_id', Integer),
  ]

  for column in columns:
    column_name, column_typename = column
    column_type = cast_to_sql_column_type(column_name, column_typename)
    args.append(Column(column_name, column_type))

  # this magically registers the schema with the metadata object, so we can create it later
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

