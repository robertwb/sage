##############################################################################
#
#  DSAGE: Distributed SAGE
#
#       Copyright (C) 2006, 2007 Yi Qiang <yqiang@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#
##############################################################################

from twisted.python import log

def optimize_sqlite(con):
    """
    Sets some pragma settings that are supposed to optimize SQLite.
    Settings taken from:
    http://web.utk.edu/~jplyon/sqlite/SQLite_optimization_FAQ.html

    """

    cur = con.cursor()
    cur.execute("pragma cache_size=4000") # Use double the default cache_size
    cur.execute("pragma synchronous=off") # do not wait for disk writes
    cur.execute("pragma temp_store=2") # store temporary results in memory

    return con

def table_exists(con, tablename):
    """
    Check if a given table exists.
    If the below query is not None, then the table exists

    """

    query = """SELECT name FROM sqlite_master
    WHERE type = 'table' AND name = ?;
    """

    cur = con.cursor()
    cur.execute(query, (tablename,))
    result = cur.fetchone()

    return result

def create_table(con, tablename, query):
    """
    Creates a table given the connection.

    """

    log.msg('Creating table %s...' % tablename)
    con.execute(query)

def fields(cursor):
    """
    Given a DB API 2.0 cursor object that has been executed, returns
    a dictionary that maps each field name to a column index, 0 and up.

    """

    results = {}
    for column, desc in enumerate(cursor.description):
        results[desc[0]] = column

    return results

def add_trigger(con, trigger):
    con.execute(trigger)