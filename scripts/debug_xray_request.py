"""
Debug script - simulates the Xray import request locally.
Prints the exact XML and request that would be sent, without hitting any API.
"""
import sys
import xml.etree.ElementTree as ET
import urllib.parse

INPUT_FILE = "results/ToscaCIResults.xml"
OUTPUT_FILE = "results/ToscaCIResults_fixed.xml"
PROJECT_KEY = "YOUR_PROJECT_KEY"
SUMMARY = "WAVE_6 - Opella Italy O2C Regression"
ENVIRONMENT = "SAP_FIORI_ITALY"
REVISION = "WAVE_6"

# ── Step 1: Parse and fix the XML ──────────────────────────────────────────────
print("=" * 70)
print("STEP 1 — Parse original XML")
print("=" * 70)

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

print(f"Root tag      : {root.tag}")
print(f"Root attribs  : {root.attrib}")
print()

testsuites = root.findall('testsuite')
print(f"Testsuites found: {len(testsuites)}")
for ts in testsuites:
    print(f"  <testsuite name='{ts.get('name')}' tests='{ts.get('tests')}' "
          f"failures='{ts.get('failures')}' time='{ts.get('time')}'>")
    testcases = ts.findall('testcase')
    print(f"  Testcases found: {len(testcases)}")
    for tc in testcases:
        print(f"    <testcase name='{tc.get('name')}' "
              f"classname='{tc.get('classname')}' "
              f"time='{tc.get('time')}'>")
        # Check for failure elements
        failures = tc.findall('failure')
        if failures:
            print(f"      -> FAILURE: {failures[0].get('message', '')}")
        else:
            print(f"      -> PASSED")

# ── Step 2: Add classname ──────────────────────────────────────────────────────
print()
print("=" * 70)
print("STEP 2 — Add classname attribute to testcases")
print("=" * 70)

count = 0
log_removed = 0
for testsuite in root.findall('testsuite'):
    testsuite.attrib.pop('log', None)
    testsuite.attrib.pop('id', None)
    suite_name = testsuite.get('name', 'UNKNOWN')
    for testcase in testsuite.findall('testcase'):
        if not testcase.get('classname'):
            testcase.set('classname', suite_name)
            count += 1
        if 'log' in testcase.attrib:
            testcase.attrib.pop('log')
            log_removed += 1

print(f"classname added to {count} testcases (value: '{suite_name}')")
print(f"log attribute removed from {log_removed} testcases")

# ── Step 3: Write fixed XML ────────────────────────────────────────────────────
tree.write(OUTPUT_FILE, encoding='unicode', xml_declaration=True)

# Show first 5 testcases of fixed XML
print()
print("Fixed XML — first 3 testcases:")
fixed_tree = ET.parse(OUTPUT_FILE)
fixed_root = fixed_tree.getroot()
for i, tc in enumerate(fixed_root.find('testsuite').findall('testcase')):
    if i >= 3:
        print("  ...")
        break
    print(f"  <testcase classname='{tc.get('classname')}' "
          f"name='{tc.get('name')}' "
          f"time='{tc.get('time')}'>")

# ── Step 4: Build the exact curl request ──────────────────────────────────────
print()
print("=" * 70)
print("STEP 3 — Exact curl request that would be sent to Xray")
print("=" * 70)

encoded_summary = urllib.parse.quote(SUMMARY)
url = (f"https://xray.cloud.getxray.app/api/v2/import/execution/junit"
       f"?projectKey={PROJECT_KEY}"
       f"&testExecSummary={encoded_summary}"
       f"&testEnvironments={ENVIRONMENT}"
       f"&revision={REVISION}")

print(f"""
curl -X POST \\
  "{url}" \\
  -H "Authorization: Bearer <TOKEN>" \\
  -F "file=@{OUTPUT_FILE}"
""")

# ── Step 5: File stats ─────────────────────────────────────────────────────────
import os
original_size = os.path.getsize(INPUT_FILE)
fixed_size = os.path.getsize(OUTPUT_FILE)
print("=" * 70)
print("STEP 4 — File stats")
print("=" * 70)
print(f"Original XML size : {original_size:,} bytes ({original_size / 1024:.1f} KB)")
print(f"Fixed XML size    : {fixed_size:,} bytes ({fixed_size / 1024:.1f} KB)")

# ── Step 6: Validate structure ─────────────────────────────────────────────────
print()
print("=" * 70)
print("STEP 5 — Validation checks")
print("=" * 70)

errors = []
warnings = []

for ts in fixed_root.findall('testsuite'):
    if not ts.get('name'):
        errors.append("testsuite missing 'name' attribute")
    for tc in ts.findall('testcase'):
        if not tc.get('name'):
            errors.append(f"testcase missing 'name': {tc.attrib}")
        if not tc.get('classname'):
            errors.append(f"testcase missing 'classname': {tc.get('name')}")
        if not tc.get('time'):
            warnings.append(f"testcase missing 'time': {tc.get('name')}")

if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  ✗ {e}")
else:
    print("✓ No structural errors found")

if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ⚠ {w}")
else:
    print("✓ No warnings")

print()
print("Done.")
