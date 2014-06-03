import uuid

from django.db import transaction
from phidb.db.backends.postgresql_psycopg2.base import *

from django.db import connection

def phi_generation_sql():
    with server_side_cursors(connection):
        cursor = connection.cursor()

        cursor.execute("SELECT r.summary, r.id FROM orm_route r LIMIT 2")
        for row in cursor:
            print row

    return None
