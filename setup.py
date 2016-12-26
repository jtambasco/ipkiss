#!/usr/bin/env python

import os
from distutils.core import setup

packages = [
            'ipkiss',
            'ipcore',
            'genericpdk',
            'technologies',
            'dependencies',
            'picazzo',
            'pysics',
            'pysimul',
            'samples',
            # 'testsuite',
            'descartes',
            ]

def list_folders(root):
  acc = []
  for f in os.listdir(root):
    if f != '_tests':
      full_name = os.path.join(root, f)
      if os.path.isdir(full_name):
        acc.append(full_name)
        acc += list_folders(full_name)
  return acc


def write_manifest(filename="MANIFEST.in"):
  with open(filename, 'w') as blah:
    for p in packages:
      blah.write("recursive-include ipkiss24\\%s \n" % p)

package_dir = {}
for p in packages:
  root = os.path.join("ipkiss24", p)
  package_dir[p] = root
  subpackages = list_folders(root)
  for s in subpackages:
    name = s.replace(os.sep,'.')
    if name.startswith("ipkiss24."):
      name = name.replace("ipkiss24.","",1)
    package_dir[name] = s


package_data = {}
for package in package_dir:
  package_data[package] = ['*.gds', '*.pyc', "*.xml"]

setup(name='IPKISS',
      version='2.4-ce',
      description='IPKISS Framework',
      author='Intec - Ugent',
      author_email='ipkiss@intec.ugent.be',
      url='www.ipkiss.org',
      license="GPL",
      extra_path="ipkiss24",
      packages=package_dir.keys(),
      package_dir=package_dir,
      package_data=package_data,
      data_files=[('ipkiss24', ['LICENSE.txt',]),]
     )

  