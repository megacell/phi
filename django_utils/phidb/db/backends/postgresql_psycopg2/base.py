import uuid

from django.db import transaction
from django.db.backends.postgresql_psycopg2.base import *
from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as BaseDatabaseWrapper

class CursorWrapper(object):
    """
    A thin wrapper around MySQLdb's normal cursor class so that we can catch
    particular exception instances and reraise them with the right types.

    Implemented as a wrapper, rather than a subclass, so that we aren't stuck
    to the particular underlying representation returned by Connection.cursor().
    """
    codes_for_integrityerror = (1048,)

    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, args=None):
        try:
            # args is None means no string interpolation
            return self.cursor.execute(query, args)
        except Database.OperationalError as e:
            # Map some error codes to IntegrityError, since they seem to be
            # misclassified and Django would prefer the more logical place.
            if e.args[0] in self.codes_for_integrityerror:
                six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
            raise

    def executemany(self, query, args):
        try:
            return self.cursor.executemany(query, args)
        except Database.OperationalError as e:
            # Map some error codes to IntegrityError, since they seem to be
            # misclassified and Django would prefer the more logical place.
            if e.args[0] in self.codes_for_integrityerror:
                six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
            raise

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Ticket #17671 - Close instead of passing thru to avoid backend
        # specific behavior.
        self.close()

class server_side_cursors(object):
    """
    With block helper that enables and disables server side cursors.
    """
    def __init__(self, qs_or_using_or_connection, itersize=None):
        from django.db import connections
        from django.db.models.query import QuerySet
        
        self.itersize = itersize
        if isinstance(qs_or_using_or_connection, QuerySet):
            self.connection = connections[qs_or_using_or_connection.db]
        elif isinstance(qs_or_using_or_connection, basestring):
            self.connection = connections[qs_or_using_or_connection]
        else:
            self.connection = qs_or_using_or_connection
    
    def __enter__(self):
        self.connection.server_side_cursors = True
        self.connection.server_side_cursor_itersize = self.itersize
        self.ac = transaction.get_autocommit()
        transaction.set_autocommit(False)
    
    def __exit__(self, type, value, traceback):
        transaction.commit()
        transaction.set_autocommit(self.ac)
        self.connection.server_side_cursors = False
        self.connection.server_side_cursor_itersize = None

class DatabaseWrapper(BaseDatabaseWrapper):
    """
    Psycopg2 database backend that allows the use of server side cursors.
    
    Usage:
    
    qs = Model.objects.all()
    with server_side_cursors(qs, itersize=x):
        for item in qs.iterator():
            item.value
    
    """
    def __init__(self, *args, **kwargs):
        self.server_side_cursors = False
        self.server_side_cursor_itersize = None
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
    
    def _cursor(self):
        """
        Returns a unique server side cursor if they are enabled, 
        otherwise falls through to the default client side cursors.
        """
        if self.server_side_cursors:
            # intialise the connection if we haven't already
            # this will waste a client side cursor, but only on the first call
            if self.connection is None:
                super(DatabaseWrapper, self)._cursor()
            
            # give the cursor a unique name which will invoke server side cursors
            cursor = self.connection.cursor(name='cur%s' % str(uuid.uuid4()).replace('-', ''))
            cursor.tzinfo_factory = None
            
            if self.server_side_cursor_itersize is not None:
                cursor.itersize = self.server_side_cursor_itersize
            
            return CursorWrapper(cursor)
        
        return super(DatabaseWrapper, self)._cursor()
