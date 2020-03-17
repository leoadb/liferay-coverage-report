#!/usr/bin/python3

import os
import config
import shutil
import clean_report

class_names = []

path = os.path.join(config.LIFERAY_HOME, config.LIFERAY_MODULE)

# r=root, d=directories, f=files
for r, d, f in os.walk(path):
    for file in f:
        for bundle in config.LIFERAY_BUNDLES:
            if os.path.join(bundle, 'src/main/java') in r:
                name = file.split('.')[0]
                with open(os.path.join(r, file)) as of:
                    if 'class {}'.format(name) in of.read():
                        class_names.append(name)
                break

print(','.join(map(str, class_names)))

result = -1

shutil.rmtree(os.path.join(config.LIFERAY_HOME, 'jacoco'), ignore_errors=True)

if config.UNIT_TEST_ENABLED:
    result = os.system(os.path.join(config.LIFERAY_HOME, 'gradlew -p {} test -Djunit.code.coverage=true'.format(path)))

if config.INTEGRATION_TEST_ENABLED:
    result = os.system(os.path.join(config.LIFERAY_HOME, 'gradlew -p {} testIntegration -Dapp.server.start.executable.arg.line="jacoco run"'.format(path)))

if result == 0:
    result = os.system('ant -f {} generate-code-coverage-report -Dclass.names={}'.format(config.LIFERAY_HOME, ','.join(map(str, class_names))))

print(result)

clean_report.report_clean()
clean_report.report_sum()
clean_report.report_percentages()