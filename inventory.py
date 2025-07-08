#!/usr/bin/python
import os
import re
import json
from collections import defaultdict
import subprocess
from sys import argv


CONFIG_FILE = os.path.expanduser("~/.ssh/config")

hostvars = defaultdict(dict)
grouped = defaultdict(dict)
grouped['no_user'] = {'hosts' : [], 'vars' : {'ansible_user': 'root'}}
grouped['_meta'] = {'hostvars': hostvars}


with open(CONFIG_FILE) as f:
# Parse each line of file
    host, distro, user, tags = ("", "", "", [])
    for line in f:
        # Look for lines that not start with # and contain Host key
        if re.search("^([^#|\\s])*Host\\s+[^*]", line):
            # Save previously found record
            if host:
                for g in ['all', distro] + tags:
                    grouped[g].setdefault('hosts', []).append(host)
                # In case there is no user for this record
                if user:
                    passwd = subprocess.run(f'pass servers/{host}'.split(),
                                            text=True,
                                            capture_output=True,
                                            check=True).stdout.splitlines()[0]
                    hostvars[host]['ansible_become_password'] = passwd
                else:
                    grouped['no_user']['hosts'].append(host)
            # Reset fields
            distro, user, tags = ("", "", [])
            host = line.split()[1]
            # Look for distro metavar, throw error if not found
            match = re.search("distro=([^\\s]+)", line)
            if not match:
                raise SyntaxError(f"Entry '{host}' doesnt have distro")
            else:
                distro = match.group(1)
            # Look for tags, no error if not found
            match = re.search("tags=([^\\s]+)", line)
            if match:
                tags = match.group(1).split(",")
        if re.search("^([^#]|\\s)*User\\s+[\\w]+", line):
            user = line.split()[1]
    # To process the last record
    if host:
        for g in ['all', distro] + tags:
            grouped[g].setdefault('hosts', []).append(host)
        # In case there is no user for this record
        if user:
            passwd = subprocess.run(f'pass servers/{host}'.split(),
                                    text=True,
                                    capture_output=True,
                                    check=True).stdout.splitlines()[0]
            hostvars[host]['ansible_become_password'] = passwd
        else:
            grouped['no_user']['hosts'].append(host)
            passwd = subprocess.run(f'pass servers/{host}/root'.split(),
                                    text=True,
                                    capture_output=True,
                                    check=True).stdout.splitlines()[0]
            hostvars[host]['ansible_password'] = passwd




if len(argv) < 2:
    print('Script requires either "--list" or "--host [hostname] arguments')
    exit(2)
elif argv[1] == '--list':
    print(json.dumps(grouped, indent=2))
elif argv[1] == '--host':
    try:
        print(hostvars[argv[2]])
    except IndexError as e:
        print(e)
        exit(2)
else:
    print('Script requires either "--list" or "--host [hostname] arguments')
    exit(2)
