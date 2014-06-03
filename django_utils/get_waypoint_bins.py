import uuid

from django.db import transaction
from phidb.db.backends.postgresql_psycopg2.base import *

from django.db import connection

def waypoint_bins():
    with server_side_cursors(connection):
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM waypoint_od_bins LIMIT 10")
        for row in cursor:
            print row

    return None
