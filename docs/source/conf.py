# -*- coding: utf-8 -*-
from datetime import date
import re
import os
import subprocess

from packaging.version import parse as version_parse

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Open Government Canada CKAN Stack'
copyright = '2024 Open Government Initiative - Initiative sur le gouvernement ouvert'
author = ''
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v4_1_0/wet-boew/css/theme.min.css',
    'css/canada_theme.css',
]
html_show_sphinx = False
html_logo = 'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v4_1_0/wet-boew/assets/sig-spl.svg'
html_favicon = 'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v4_1_0/wet-boew/assets/favicon.ico'

# -- Custom options -------------------------------------------------
ckan_stack = {
    '2.9_py2': {
        'https://github.com/open-data/ckan.git'                     : 'canada-v2.9',
        'https://github.com/ckan/ckanapi.git'                       : 'master',
        'https://github.com/open-data/ckanext-canada.git'           : 'master',
        'https://github.com/open-data/ckanext-cloudstorage.git'     : 'canada-v2.9',
        'https://github.com/open-data/ckanext-csrf-filter.git'      : 'canada-v2.9',
        'https://github.com/open-data/ckanext-dcat.git'             : 'canada-v2.9',
        'https://github.com/ckan/ckanext-dsaudit.git'               : 'master',
        'https://github.com/ckan/ckanext-excelforms.git'            : 'main',
        'https://github.com/ckan/ckanext-fluent.git'                : 'master',
        'https://github.com/open-data/ckanext-gcnotify.git'         : 'master',
        'https://github.com/open-data/ckanext-openapiview.git'      : 'main',
        'https://github.com/open-data/ckanext-power-bi.git'         : 'main',
        'https://github.com/open-data/ckanext-recombinant.git'      : 'master',
        'https://github.com/ckan/ckanext-scheming.git'              : 'master',
        'https://github.com/open-data/ckanext-security.git'         : 'canada-v2.9',
        'https://github.com/open-data/ckanext-validation.git'       : 'canada-v2.9',
        'https://github.com/open-data/ckanext-xloader.git'          : 'canada-v2.9',
        'https://github.com/ckan/ckantoolkit.git'                   : 'master',
        'https://github.com/open-data/goodtables.git'               : 'master',
    },
    '2.9_py3': {
        'https://github.com/open-data/ckan.git'                     : 'canada-py3',
        'https://github.com/ckan/ckanapi.git'                       : 'master',
        'https://github.com/open-data/ckanext-canada.git'           : 'canada-py3',
        'https://github.com/open-data/ckanext-cloudstorage.git'     : 'canada-v2.9',
        'https://github.com/open-data/ckanext-csrf-filter.git'      : 'canada-v2.9',
        'https://github.com/open-data/ckanext-dcat.git'             : 'canada-py3',
        'https://github.com/ckan/ckanext-dsaudit.git'               : 'master',
        'https://github.com/ckan/ckanext-excelforms.git'            : 'main',
        'https://github.com/ckan/ckanext-fluent.git'                : 'master',
        'https://github.com/open-data/ckanext-gcnotify.git'         : 'master',
        'https://github.com/open-data/ckanext-openapiview.git'      : 'main',
        'https://github.com/open-data/ckanext-power-bi.git'         : 'main',
        'https://github.com/open-data/ckanext-recombinant.git'      : 'canada-py3',
        'https://github.com/ckan/ckanext-scheming.git'              : 'master',
        'https://github.com/open-data/ckanext-security.git'         : 'canada-py3',
        'https://github.com/open-data/ckanext-validation.git'       : 'canada-py3',
        'https://github.com/open-data/ckanext-xloader.git'          : 'canada-v2.9',
        'https://github.com/ckan/ckantoolkit.git'                   : 'master',
        'https://github.com/open-data/goodtables.git'               : 'master',
    },
}


def get_latest_commit_hash(remote, branch):
    latest_hash = subprocess.check_output(
        ['git', 'ls-remote', remote, 'refs/heads/%s' % branch], stderr=subprocess.STDOUT).decode('utf8')

    latest_hash = re.split(r'\t+', latest_hash)[0]

    return latest_hash


releases = {}

for ver, repos in ckan_stack.items():
    releases[ver] = {}
    for repo, branch in repos.items():
        latest_hash = get_latest_commit_hash(repo, branch)
        repo_uri = repo.replace('.git', '')
        repo_name = repo_uri.split('/')[-1]
        releases[ver][repo_name] = {
            'uri': repo_uri,
            'hash': latest_hash,
        }

html_context = {
    'releases': releases,
}
