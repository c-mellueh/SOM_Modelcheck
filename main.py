import datetime
import os

import ifcopenshell
from SOMcreator import Project

from modelcheck import check_all_elements
from output import create_issues
from powerbi import handle_definitions
from sql import create_tables


def import_project(project_path):
    proj = Project("Test")
    proj.clear()
    proj.open(project_path)
    return proj


def check_file(file_path, proj, ag, bk, db_name, add_zero_width, project_name):
    file_name, extension = os.path.splitext(file_path)
    if extension.lower() != ".ifc":
        return

    file = os.path.split(file_path)[1]

    ifc = ifcopenshell.open(file_path)
    check_all_elements(proj, ifc, file, db_name, ag, bk, add_zero_width, project_name)


def main(file_paths, som_path, db_path, ag, bk, issue_path, project_name, add_zero_width=False, power_bi_path=None):
    proj = import_project(som_path)
    if power_bi_path is not None:
        handle_definitions(proj, power_bi_path)
    create_tables(db_path)

    if not isinstance(file_paths, list):
        if not isinstance(file_paths, str):
            return
        if not os.path.isfile(file_paths):
            return
        check_file(file_paths, proj, ag, bk, db_path, add_zero_width, project_name)
        return

    for path in file_paths:
        if os.path.isdir(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                check_file(file_path, proj, ag, bk, db_path, add_zero_width, project_name)
        else:
            check_file(path, proj, ag, bk, db_path, add_zero_width, project_name)

    create_issues(db_path, issue_path)


if __name__ == "__main__":
    project_name = "Studernheimer Kurve"  # Project Name
    ifc_path = "C:/Users/ChristophMellueh/OneDrive - Deutsche Bahn/Projekte/Studernheimer Kurve/Modelchecking/23_05_31/test.ifc"
    main_property_set = "Allgemeine Eigenschaften"
    main_attribute = "bauteilKlassifikation"
    database = f"databases/{'Auswertung'}.db"
    semantic_object_model = "data/23-04-28-SOM-StuKu.SOMjson"
    excel_path = os.path.join("Issues_StuKu", f"{datetime.date.today()}_{project_name}.xlsx")
    fp = [ifc_path]
    main(fp, semantic_object_model, database, main_property_set, main_attribute, excel_path, project_name, False)
