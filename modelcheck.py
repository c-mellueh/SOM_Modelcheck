import re
import sqlite3
import time

import SOMcreator
import tqdm
import datetime
from SOMcreator import Project
from SOMcreator import constants as SOMconstants
from ifcopenshell.util import element as ifc_el

import issues
from sql import db_create_entity,remove_existing_issues

GROUP = "Gruppe"
ELEMENT = "Element"


def check_format(cursor, value, attribute, guid, element_type, add_zero_width):
    is_ok = False
    for form in attribute.value:
        if re.match(form, value) is not None:
            is_ok = True
    if not is_ok:
        issues.format_issue(cursor, guid, attribute, value, element_type, add_zero_width)


def check_list(cursor, value, attribute, guid, element_type, add_zero_width):
    if not attribute.value:
        return
    if value not in attribute.value:
        issues.list_issue(cursor, guid, attribute, value, element_type, add_zero_width)


def check_range(cursor, value, attribute, guid, element_type, add_zero_width):
    is_ok = False
    for possible_range in attribute:
        if min(possible_range) <= value <= max(possible_range):
            is_ok = True
    if not is_ok:
        issues.range_issue(cursor, guid, attribute, value, element_type, add_zero_width)


def check_values(cursor, value, attribute: SOMcreator.Attribute, guid, element_type, add_zero_width):
    check_dict = {SOMconstants.LIST: check_list, SOMconstants.RANGE: check_range,
                  SOMconstants.FORMAT: check_format}
    func = check_dict[attribute.value_type]
    func(cursor, value, attribute, guid, element_type, add_zero_width)


def check_for_attributes(cursor, element, pset_dict, obj: SOMcreator.Object, element_type, add_zero_width):
    guid = element.GlobalId
    for property_set in obj.property_sets:
        pset_name = property_set.name
        if pset_name not in pset_dict:
            issues.property_set_issue(cursor, guid, pset_name, element_type, add_zero_width)
            continue

        for attribute in property_set.attributes:
            attribute_name = attribute.name
            if attribute.name not in pset_dict[pset_name]:
                issues.attribute_issue(cursor, guid, pset_name, attribute_name, element_type, add_zero_width)
                continue

            value = pset_dict[pset_name][attribute_name]
            check_values(cursor, value, attribute, guid, element_type, add_zero_width)


def gruppe_zu_pruefen(cursor, el, ag, bk, add_zero_width):
    bauteilklass = ifc_el.get_pset(el, ag, bk)
    if bauteilklass is None:
        issues.ident_issue(cursor, el.GlobalId, bk, ag, GROUP, add_zero_width)
        return False
    sub_bks = set()
    for relationship in getattr(el, "HasAssignments", []):
        if not relationship.is_a('IfcRelAssignsToGroup'):
            continue

        parent = relationship.RelatingGroup
        parent_bk = ifc_el.get_pset(parent, ag, bk)
        if parent_bk == bauteilklass:
            return True

    for relationship in getattr(el, "IsGroupedBy", []):
        for sub in relationship.RelatedObjects:
            sub_bk = ifc_el.get_pset(sub, ag, bk)
            sub_bks.add(sub_bk)

    if {bauteilklass} != sub_bks:
        issues.subgroup_issue(cursor, el.GlobalId, add_zero_width)

    return False


def check_group(group, sub_group, ag, bk, ident_dict):
    bauteilk = ifc_el.get_pset(group, ag, bk)
    subbauteilk = ifc_el.get_pset(sub_group, ag, bk)
    parent_obj = ident_dict.get(bauteilk)
    child_obj = ident_dict.get(subbauteilk)
    if child_obj is None:
        print(f"Achtung Subbauteilklasse '{subbauteilk}' nicht bekannt")
        return False
    child_aggregations = child_obj.aggregation_representations
    for parent_aggregation in parent_obj.aggregation_representations:
        if parent_aggregation.children.intersection(child_aggregations):
            return True
    return False


def check_element(element, ag, bk, cursor, file_name, ident_dict, element_type, add_zero_width, project_name):
    guid = element.GlobalId
    psets = ifc_el.get_psets(element)
    ag_pset = psets.get(ag)
    group_assignment = [assignment for assignment in getattr(element, "HasAssignments", []) if assignment.is_a("IfcRelAssignsToGroup")]
    if not group_assignment:
        issues.no_group_issue(cursor,element,add_zero_width)

    if ag_pset is None:
        issues.ident_pset_issue(cursor, guid, ag, element_type, add_zero_width)
        db_create_entity(element, cursor,project_name, file_name, "", add_zero_width)
        return

    bauteil_klassifikation = ag_pset.get(bk)
    if bauteil_klassifikation is None:
        issues.ident_issue(cursor, guid, ag, bk, element_type, add_zero_width)
        db_create_entity(element, cursor,project_name, file_name, "", add_zero_width)
        return
    obj_rep = ident_dict.get(bauteil_klassifikation)
    db_create_entity(element, cursor,project_name, file_name, bauteil_klassifikation, add_zero_width)
    if obj_rep is None:
        issues.ident_unknown(cursor, guid, ag, bk, element_type, bauteil_klassifikation, add_zero_width)
        return

    check_for_attributes(cursor, element, psets, obj_rep, element_type, add_zero_width)


def check_all_elements(proj: Project, ifc, file_name, db_name, ag, bk, add_zero_width,project_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    remove_existing_issues(cursor,project_name,datetime.date.today(),file_name)

    ident_dict = {obj.ident_value: obj for obj in proj.objects}
    for element in tqdm.tqdm(ifc.by_type("IfcElement"), desc=f"[{ELEMENT}] {file_name}"):
        check_element(element, ag, bk, cursor, file_name, ident_dict, ELEMENT, add_zero_width,project_name)

    for element in tqdm.tqdm(ifc.by_type("IfcGroup"), desc=f"[{GROUP}] {file_name}"):
        relationships = getattr(element, "IsGroupedBy", [])
        if gruppe_zu_pruefen(cursor, element, ag, bk, add_zero_width):
            check_element(element, ag, bk, cursor, file_name, ident_dict, GROUP, add_zero_width,project_name)
            if not relationships:
                issues.empty_group_issue(cursor, element, add_zero_width)

            for relationship in relationships:
                for sub_element in relationship.RelatedObjects:
                    allowed = check_group(element, sub_element, ag, bk, ident_dict)
                    if not allowed:
                        issues.parent_issue(cursor, element, sub_element, add_zero_width)

    time.sleep(0.1)
    print()
    conn.commit()
    conn.close()
