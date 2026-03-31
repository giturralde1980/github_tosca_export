import sys
import xml.etree.ElementTree as ET

input_file = sys.argv[1]
output_file = sys.argv[2]

tree = ET.parse(input_file)
root = tree.getroot()

count = 0
for testsuite in root.findall('testsuite'):
    # Remove log attribute from testsuite (not needed by Xray)
    testsuite.attrib.pop('log', None)
    testsuite.attrib.pop('id', None)

    suite_name = testsuite.get('name', 'UNKNOWN')
    for testcase in testsuite.findall('testcase'):
        # Add classname if missing
        if not testcase.get('classname'):
            testcase.set('classname', suite_name)
            count += 1
        # Remove log attribute (huge, not needed by Xray)
        testcase.attrib.pop('log', None)

tree.write(output_file, encoding='unicode', xml_declaration=True)
print(f"Done: {count} testcases updated with classname='{suite_name}'")
