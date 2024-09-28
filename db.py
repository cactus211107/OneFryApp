import sqlite3,json,re
from os import PathLike

_db:str = ''
def initDB(database:str|PathLike):
    global _db
    _db = database
    print(f'Initialized database "{_db}"')
class DBOBJECT:
    def __init__(self,o:object):
        self.error=type(o) == DBERROR
        self.o=o
    def fetchone(self)->tuple:
        try:return self.o[0]
        except:return tuple([])
    def fetchmany(self,size:int=1)->list[tuple]:
        try:return self.o[:size]
        except:return [tuple([])]
    def fetchall(self)->list[tuple]:return self.o
class DBERROR:
    def __init__(self,e) -> None:
        self.error=e
    # maybe add these
    # def fetchone(self):
    #     return self
    # def fetchall(self):
    #     return self
    # def fetchmany(self,s):
    #     return self

def execute(sql:str,params:tuple|None = None)->DBOBJECT:
    global _db
    with sqlite3.connect(_db) as conn:
        r=None #return value
        db=conn.cursor()
        if not _db: # check if database exists
            raise Exception('Database not initialized.')
        try:
            r=DBOBJECT(db.execute(sql,params).fetchall() if params else db.execute(sql).fetchall())
        except sqlite3.Error as e:
            print(f"Error executing statement: {sql}")
            print(e)
            return DBERROR(DBERROR(e))
        conn.commit()
    return r
def executeFile(path:str|PathLike):
    with open(path, 'r') as sql_file:
        sql_statements = sql_file.read()
    statements = re.sub(r'--.*','',sql_statements)
    statements=statements.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement:  # Skip empty statements
            try:
                execute(statement,None)
            except sqlite3.Error as e:
                print(f"Error executing statement: {statement}")
                raise e
def isError(o):return o is DBERROR or not o