from db import init_database
from import_csv import import_csv

init_database()

import_csv("incoming/test.csv")