import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse('New_Funder.xml')
root = tree.getroot()

# Iterate over all organizationType elements
for org_type in root.findall('.//organizationType'):
    org_type.text = 'FUNDER'

# Overwrite the original file
tree.write('New_Funder.xml', encoding='utf-8', xml_declaration=True)
