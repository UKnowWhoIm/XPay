#!/bin/sh

echo "#!/usr/bin/env python3

import subprocess
import re

print(\"Running pre-commit hook for pylint......\\\n\")

changed_files = subprocess.run([\"git\", \"--no-pager\", \"diff\", \"--name-only\", \"HEAD\"], capture_output=True)

changed_files = changed_files.stdout.decode(\"utf-8\").split(\"\\\n\")

target_files = [file.replace(\"server\", \"/app\") for file in changed_files if re.match(r\"^server/app/.+\.py\", file)]

if len(target_files) == 0:
    exit(0)

lint = subprocess.run([\"docker-compose\", \"run\", \"--rm\", \"server\", \"pylint\", *target_files], capture_output=True)

if lint.returncode != 0:
    print(\"ERRORS FOUND\\\n\\\n\\\n\")

print(lint.stdout.decode(\"utf-8\"))

exit(lint.returncode)
" > .git/hooks/pre-commit

chmod +x .git/hooks/pre-commit