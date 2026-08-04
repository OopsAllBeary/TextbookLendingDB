from db import init_database
from import_csv import import_applications

init_database()

import_applications("incoming/test.csv")