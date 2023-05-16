import sql

ATTRIBUTE_VALUE_ISSUES = 7
ATTRIBUTE_EXIST_ISSUE = 6
PROPERTY_SET_ISSUE = 5
IDENT_ATTRIBUTE_UNKNOWN = 3
IDENT_ATTRIBUTE_ISSUE = 2
IDENT_PROPERTY_SET_ISSUE = 1
PARENT_ISSUE = 8
SUBGROUP_ISSUE = 9  # Gruppe besitzt verschiedene Untergruppen
EMPTY_GROUP_ISSUE = 10
NO_GROUP_ISSUE = 11
GUID_ISSUE = 4

def format_issue(cursor, guid, attribute, value, element_type, add_zero_width):
    description = f"{element_type} besitzt nicht das richtige Format für {attribute.property_set.name}:{attribute.name} (Wert ist: {value})"
    issue_nr = ATTRIBUTE_VALUE_ISSUES
    sql.add_issues(cursor, guid, description, issue_nr, attribute, add_zero_width)


def list_issue(cursor, guid, attribute, value, element_type, add_zero_width):
    description = f"{element_type} besitzt nicht den richtigen Wert für {attribute.property_set.name}:{attribute.name} (Wert ist: {value})"
    issue_nr = ATTRIBUTE_VALUE_ISSUES
    sql.add_issues(cursor, guid, description, issue_nr, attribute, add_zero_width)


def range_issue(cursor, guid, attribute, value, element_type, add_zero_width):
    description = f"{element_type}  {attribute.property_set.name}:{attribute.name} ist nicht in den vorgegebenen Wertebereichen (Wert ist: {value})"
    issue_nr = ATTRIBUTE_VALUE_ISSUES
    sql.add_issues(cursor, guid, description, issue_nr, attribute, add_zero_width)


def property_set_issue(cursor, guid, pset_name, element_type, add_zero_width):
    description = f"{element_type} besitzt nicht das PropertySet {pset_name}"
    issue_nr = PROPERTY_SET_ISSUE
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width, pset_name=pset_name)


def attribute_issue(cursor, guid, pset_name, attribute_name, element_type, add_zero_width):
    description = f"{element_type} besitzt nicht das Attribute {pset_name}:{attribute_name}"
    issue_nr = ATTRIBUTE_EXIST_ISSUE
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width, pset_name=pset_name,
                   attribute_name=attribute_name)


def ident_issue(cursor, guid, pset_name, attribute_name, element_type, add_zero_width):
    description = f"{element_type} besitzt nicht das Zuweisungsattribut {pset_name}:{attribute_name}"
    issue_nr = IDENT_ATTRIBUTE_ISSUE
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width, pset_name=pset_name,
                   attribute_name=attribute_name)


def ident_pset_issue(cursor, guid, pset_name, element_type, add_zero_width):
    description = f"{element_type}  besitzt nicht das PropertySet {pset_name}"
    issue_nr = IDENT_PROPERTY_SET_ISSUE
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width, pset_name=pset_name)


def ident_unknown(cursor, guid, pset_name, attribute_name, element_type, value, add_zero_width):
    description = f"{element_type} Zuweisungsattribut {pset_name}:{attribute_name}={value} konnte nicht in SOM gefunden werden"
    issue_nr = IDENT_ATTRIBUTE_UNKNOWN
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width, pset_name=pset_name,
                   attribute_name=attribute_name)

def guid_issue(cursor, guid, file1, file2, add_zero_width):
    description = f'GUID kommt in Datei "{file1}" und "{file2}" vor'
    issue_nr = GUID_ISSUE
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width)
### GROUP ISSUES

def subgroup_issue(cursor, guid, add_zero_width):
    description = f"Gruppensammler besitzt verschiedene Untergruppen"
    issue_nr = IDENT_ATTRIBUTE_ISSUE
    sql.add_issues(cursor, guid, description, issue_nr, None, add_zero_width)


def empty_group_issue(cursor, element, add_zero_width):
    description = f"Gruppe {element.name} besitzt keine Subelemente "
    issue_nr = EMPTY_GROUP_ISSUE
    sql.add_issues(cursor, element.GlobalId, description, issue_nr, None, add_zero_width)


def parent_issue(cursor, element, sub_element, add_zero_width):
    description = f"Gruppe {element.Name} besitzt die falsche Kindklasse ({sub_element.Name})"
    issue_nr = PARENT_ISSUE
    sql.add_issues(cursor, element.GlobalId, description, issue_nr, None, add_zero_width)

def no_group_issue(cursor, element, add_zero_width):
    description = f"Element hat keine Gruppenzuweisung"
    issue_nr = NO_GROUP_ISSUE
    sql.add_issues(cursor, element.GlobalId, description, issue_nr, None, add_zero_width)