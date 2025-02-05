import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re
import html

def parse_function_signature(signature):
    match = re.match(r"(\w+)\.(\w+)\((.*)\)", signature)
    if match:
        namespace, func_name, params = match.groups()
        param_list = [param.strip() for param in params.split(",") if param.strip()]
        return namespace, func_name, param_list
    return None, None, []

def extract_functions(file_path):
    functions_df = pd.read_excel(file_path, sheet_name="Functions", usecols=[0, 1, 2], names=["value", "name", "desc"], skiprows=1)
    functions = []
    
    for _, row in functions_df.iterrows():
        ret_type, signature, description = row["value"], row["name"], row["desc"]
        description = str(description) if pd.notna(description) else ""  # Ensure description is a string
        namespace, func_name, params = parse_function_signature(signature)
        if func_name:
            functions.append((func_name, ret_type, params, description))
    
    return functions

def extract_constants(file_path):
    # Load the relevant sheets
    constants_df = pd.read_excel(file_path, sheet_name="Constants", usecols=[1])  # Second column
    archetype_df = pd.read_excel(file_path, sheet_name="Archetype constants", usecols=[0])  # First column
    
    # Drop the header row
    constants = constants_df.iloc[1:, 0].dropna().tolist()
    archetypes = archetype_df.iloc[1:, 0].dropna().tolist()
    
    return constants + archetypes

def prettify_xml(element):
    rough_string = ET.tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def format_description(description, max_length=80):
    # Decode HTML entities
    description = html.unescape(description)
    
    # Split the description into lines of a maximum length
    lines = []
    while len(description) > max_length:
        # Find the last space before the max length
        break_point = description.rfind(' ', 0, max_length)
        if break_point == -1:
            break_point = max_length  # If no space, just break at max length
        lines.append(description[:break_point].strip())
        description = description[break_point:].strip()

    # Add the remaining part of the description
    if description:
        lines.append(description)

    # Return the formatted description, joined by a newline
    return '\n'.join(lines)

def generate_autocomplete_xml(functions, constants, output_file="notepadpp_autocomplete.xml"):
    root = ET.Element("NotepadPlus")
    autocomplete = ET.SubElement(root, "AutoComplete")

    # Add functions to XML
    for func_name, ret_type, params, description in functions:
        keyword = ET.SubElement(autocomplete, "KeyWord", name=func_name, func="yes")
        formatted_desc = format_description(description)
        overload = ET.SubElement(keyword, "Overload", retVal=ret_type, descr=formatted_desc)  # Added formatted description
        
        for param in params:
            ET.SubElement(overload, "Param", name=param)
    
    # Add constants to XML
    for constant in constants:
        ET.SubElement(autocomplete, "KeyWord", name=constant)
    
    formatted_xml = prettify_xml(root)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted_xml)



if __name__ == "__main__":
    file_path = "Bastion.xlsx"  # Update with the correct path if needed
    functions = extract_functions(file_path)
    constants = extract_constants(file_path)
    generate_autocomplete_xml(functions, constants)
    print(f"Auto-completion XML file generated successfully with {len(functions)} functions and {len(constants)} constants.")
