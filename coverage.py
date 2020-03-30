#!/usr/bin/python3

import os
import config
import shutil
import clean_report
import time

class_names = []

base_path = os.path.join(os.environ['LIFERAY_HOME'], os.pardir, 'liferay-portal')

tomcat_path = os.path.join(os.environ['LIFERAY_HOME'], 'liferay-portal', 'tomcat-9.0.33', 'bin')

path = os.path.join(base_path, config.LIFERAY_MODULE)

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

result = -1

shutil.rmtree(os.path.join(base_path, 'jacoco'), ignore_errors=True)

result = os.system(os.path.join(base_path, 'gradlew -p {} test -Djunit.code.coverage=true'.format(path)))
    
result = os.system(os.path.join(base_path, 'gradlew -p {} testIntegration -Dapp.server.start.executable.arg.line="jacoco run"'.format(path)))

if result == 0:
    result = os.system('ant -f {} generate-code-coverage-report -Dclass.names={}'.format(base_path, ','.join(map(str, class_names))))

clean_report.report_clean(base_path)
clean_report.report_sum(base_path)
clean_report.report_percentages(base_path)