import sys
import xml.etree.ElementTree as ET

input_file = sys.argv[1]
output_file = sys.argv[2]

tree = ET.parse(input_file)
root = tree.getroot()

count = 0
for testsuite in root.findall('testsuite'):
    suite_name = testsuite.get('name', 'UNKNOWN')
    for testcase in testsuite.findall('testcase'):
        if not testcase.get('classname'):
            testcase.set('classname', suite_name)
            count += 1

tree.write(output_file, encoding='unicode', xml_declaration=True)
print(f"Done: {count} testcases updated with classname='{suite_name}'")
