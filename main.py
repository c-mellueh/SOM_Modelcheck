import os
import ifcopenshell
from SOMcreator import Project
from powerbi import handle_definitions
from sql import create_tables
from modelcheck import check_all_elements
from output import create_issues
import datetime

def import_project(project_path):
    proj = Project("Test", "ChristophMellueh")
    proj.clear()
    proj.open(project_path)
    return proj

def check_file(file_path,proj,ag,bk,db_name,add_zero_width):
    file_name, extension = os.path.splitext(file_path)
    if extension.lower() != ".ifc":
        return
    ifc = ifcopenshell.open(file_path)
    file = os.path.split(file_path)[1]
    check_all_elements(proj, ifc, file, db_name, ag, bk,add_zero_width)

def main(file_paths,som_path, db_path, ag, bk,issue_path,add_zero_width = False,power_bi_path = None):
    proj = import_project(som_path)
    if power_bi_path is not None:
        handle_definitions(proj,power_bi_path)
    create_tables(db_path)

    if not isinstance(file_paths,list):
        if not isinstance(file_paths,str):
            return
        if not os.path.isfile(file_paths):
            return
        check_file(file_paths, proj, ag, bk, db_path,add_zero_width)
        return

    for path in file_paths:
        if os.path.isdir(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                check_file(file_path, proj, ag, bk, db_path,add_zero_width)
        else:
            check_file(path, proj, ag, bk, db_path,add_zero_width)

    create_issues(db_path,issue_path)

if __name__ == "__main__":
    projekt_kuerzel = "WiSi"
    path_1 = "C:/Users/ChristophMellueh/OneDrive - Deutsche Bahn/Projekte/Wilferdingen Singen/IFC/23-05-15_Modelle"
    alg = "Allgemeine Eigenschaften"
    bauk = "bauteilKlassifikation"
    dbp = f"databases/{datetime.date.today()}_{projekt_kuerzel}.db"
    sp = "data/23-05-09-WiSi.SOMjson"
    issue_path = os.path.join("Issues",f"{datetime.date.today()}_{projekt_kuerzel}.xlsx")
    pbip =   "C:/Users/ChristophMellueh/Deutsche Bahn/I.NI-SW-M-H - Dokumente/MA/PA1/04 Z-Akte/Themenakte/PowerBI/definitions.xlsx"
    fp = [path_1]
    main(fp,sp,dbp,alg,bauk,issue_path,False,pbip)