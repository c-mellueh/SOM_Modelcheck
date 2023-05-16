import re
import sqlite3
import issues
from ifcopenshell import entity_instance
guids = dict()

def create_tables(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    DROP TABLE IF EXISTS entities
    ''')
    c = conn.cursor()
    c.execute('''
    DROP TABLE IF EXISTS issues
    ''')
    c.execute('''
              CREATE TABLE IF NOT EXISTS entities
              ([GUID] CHAR(64) PRIMARY KEY, [ifc_type] TEXT,[x_pos] DOUBLE,[y_pos] DOUBLE,[z_pos] DOUBLE,[datei] TEXT,[bauteilKlassifikation] TEXT)
              ''')
    c.execute('''
              CREATE TABLE IF NOT EXISTS issues
              ([GUID] CHAR(64), [short_description] TEXT,[issue_type] INT,[PropertySet] TEXT, [Attribut] TEXT)
              ''')

    conn.commit()
    conn.close()


def add_issues(cursor, guid, description, issue_type, attribute, add_zero_width, pset_name="", attribute_name=""):
    guid = transform_guid(guid, add_zero_width)
    if attribute is not None:
        pset_name = attribute.property_set.name
        attribute_name = attribute.name
    cursor.execute(f'''
          INSERT INTO issues (GUID,short_description,issue_type,PropertySet,Attribut)
                VALUES
                ('{guid}','{description}',{issue_type},'{pset_name}','{attribute_name}')
          ''')


def transform_guid(guid: str, add_zero_width: bool):
    """Fügt Zero Width Character ein weil PowerBI (WARUM AUCH IMMER FÜR EIN BI PROGRAMM?????) Case Insensitive ist"""
    if add_zero_width:
        return re.sub(r"([A-Z])", lambda m: m.group(0) + u"\u200B", guid)
    else:
        return guid


def db_create_entity(element: entity_instance, cursor, file_name, bauteil_klasse, add_zero_width):
    guid = transform_guid(element.GlobalId, add_zero_width)
    ifc_type = element.is_a()
    center = [0, 0, 0]
    if guid in guids:
        issues.guid_issue(cursor,guid,file_name,guids[guid],add_zero_width)
        return
    else:
        guids[guid] = file_name
    cursor.execute(f'''
              INSERT INTO entities (GUID,ifc_type,x_pos,y_pos,z_pos,datei,bauteilKlassifikation)
                    VALUES
                    ('{guid}','{ifc_type}',{center[0]},{center[1]},{center[2]},'{file_name}','{bauteil_klasse}')
              ''')



def query_issues(cursor):
    return cursor.execute(
        "SELECT i.*, e.datei, e.bauteilKlassifikation FROM issues AS i JOIN entities e on i.GUID = e.GUID")
