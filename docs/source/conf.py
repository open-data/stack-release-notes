# -*- coding: utf-8 -*-
import json
import re
import os
import subprocess
import requests

STACK = {
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
    'https://github.com/open-data/goodtables.git'               : 'canada',
}

FRONTEND_VERSION_PREFIX = 'v.'

FIX_TYPES = [
    'fix',
    'bugfix',
    'hotfix',
]
FIX_LABEL = 'Bugfixes'

FEATURE_TYPES = [
    'feature',
    'misc'
]
FEATURE_LABEL = 'Features'

CHANGES_TYPES = [
    'changes',
]
CHANGES_LABEL = 'Changes'

MIGRATION_TYPES = [
    'migration',
]
MIGRATION_LABEL = 'Migrations'

REMOVAL_TYPES = [
    'removal',
]
REMOVAL_LABEL = 'Removals'


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
html_theme_display_version = True
html_static_path = ['_static']
html_css_files = [
    'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v4_1_0/wet-boew/css/theme.min.css',
    'css/canada_theme.css',
]
html_js_files = [
    'js/canada.js',
]
html_show_sphinx = False
html_logo = 'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v4_1_0/wet-boew/assets/sig-spl.svg'
html_favicon = 'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v4_1_0/wet-boew/assets/favicon.ico'

# -- Custom options -------------------------------------------------

def get_release_tags(order='v:refname', latest=False):
    if latest:
        # force order for latest
        order = '-v:refname'

    git_tags = subprocess.check_output(
        ['git', 'tag', '-l', '--sort=%s' % order], stderr=subprocess.STDOUT).decode('utf8')

    git_tags = git_tags.split()

    release_tags = [tag.split('/')[1] for tag in git_tags if tag.startswith('release/')]

    if not release_tags:
        return None

    if latest:
        return release_tags[0]

    return release_tags


def get_latest_commit_hash(remote, branch):
    latest_hash = subprocess.check_output(
        ['git', 'ls-remote', remote, 'refs/heads/%s' % branch], stderr=subprocess.STDOUT).decode('utf8')

    latest_hash = re.split(r'\t+', latest_hash)[0]

    print("Gathering info from %s" % remote)

    assert latest_hash

    return latest_hash


def get_release_hashes():

    release_hashes = {}

    release = get_release_tags(latest=True)

    print("Gathering release information for %s" % release)

    for repo, branch in STACK.items():

        latest_hash = get_latest_commit_hash(repo, branch)
        repo_uri = repo.replace('.git', '')
        repo_name = repo_uri.split('/')[-1]

        release_hashes[repo_name] = {
            'uri': repo_uri,
            'hash': latest_hash,
        }

    return release_hashes


def create_release_json_file():
    release = get_release_tags(latest=True)

    if not release:
        print("No release tags found, skipping...")
        return

    filename = '_release_builds/releases/%s.json' % release

    if os.path.isfile(filename):
        print("File already exists for release %s, skipping..." % release)
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        data = get_release_hashes()
        json.dump(data, f, ensure_ascii=False, indent=4)

# create a new json file name with the release info.
# this file should contain the commit hashes of the stack at
# the time the tag is added to this repository.
create_release_json_file()


def parsed_release_hashses():
    parsed_release_hashses = {}

    release_tags = get_release_tags()

    if not release_tags:
        print("No release tags found, skipping...")
        return parsed_release_hashses

    print("Building release notes...")

    prev_release = None

    for release in release_tags:

        print("Building from release tag: %s" % release)

        diff_filename = '_release_builds/differences/%s.json' % release
        release_filename = '_release_builds/releases/%s.json' % release

        if not os.path.isfile(release_filename):
            print("File does not exist for release %s, skipping..." % release)
            continue

        if prev_release:
            print("Previous release is %s" % prev_release)

        if os.path.isfile(diff_filename):
            # we already have a diff file, load from that.

            print("Gathering from diff file for release %s" % release)

            with open(diff_filename, 'r') as f:
                parsed_release_hashses[release] = json.load(f)

            prev_release = release

        else:
            # generate the parsed objects and save to a diff file.

            print("Generating diff file for release %s" % release)

            if prev_release:
                prev_release_filename = '_release_builds/releases/%s.json' % prev_release

            # check between releases for commit hash differences.
            # if the hash is different, then there are code changes
            # that are in the release.
            release_dict = {}
            with open(release_filename, 'r') as f:
                release_dict = json.load(f)

            prev_release_dict = {}
            if prev_release:
                with open(prev_release_filename, 'r') as f:
                    prev_release_dict = json.load(f)

            if release_dict:
                if release not in parsed_release_hashses:
                    parsed_release_hashses[release] = {}

                if prev_release_dict:

                    for repo, info in prev_release_dict.items():
                        # a repo in the previous release is no longer in
                        # the next release. Consider this a removal.
                        if repo not in release_dict:
                            parsed_release_hashses[release][repo] = 'Removed'

                    for repo, info in release_dict.items():
                        # the repo was not in the previous release,
                        # consider it an initial release for that repo.
                        if repo not in prev_release_dict:
                            parsed_release_hashses[release][repo] = 'Initial Release'
                        # the commit hash between the releases is different,
                        # so this is a code release.
                        elif info['hash'] != prev_release_dict[repo]['hash']:
                            parsed_release_hashses[release][repo] = {
                                'uri': info['uri'],
                                'prev': prev_release_dict[repo]['hash'],
                                'head': info['hash'],
                            }

            # save object to diff file.
            os.makedirs(os.path.dirname(diff_filename), exist_ok=True)
            with open(diff_filename, 'w', encoding='utf-8') as f:
                json.dump(parsed_release_hashses[release], f, ensure_ascii=False, indent=4)

            prev_release = release

        # fetch comparision from github API, and save to a file.
        # fetch any added change log files, and sace to a file.
        if release in parsed_release_hashses:
            github_filename = '_release_builds/github/%s.json' % release
            github_compare_dicts = {}

            if os.path.isfile(github_filename):
                # we already have a github api compare file, load from that.

                print("Gathering info from compare file for release %s" % release)

                with open(github_filename, 'r') as f:
                    github_compare_dicts = json.load(f)

            else:
                # fetch from github API and save to compare file.

                print("Fetching info from GitHub API for release %s" % release)

                for repo, info in parsed_release_hashses[release].items():
                    endpoint = info['uri'].replace('https://github.com', 'https://api.github.com/repos')
                    endpoint += '/compare/%s...%s' % (info['prev'], info['head'])
                    response = requests.get(endpoint)
                    github_compare_dicts[repo] = json.loads(response.content)

                # save object to compare file.
                os.makedirs(os.path.dirname(github_filename), exist_ok=True)
                with open(github_filename, 'w', encoding='utf-8') as f:
                    json.dump(github_compare_dicts, f, ensure_ascii=False, indent=4)

            # add github compare API info to parsed object for front-end.
            if github_compare_dicts:
                for repo, compare_dict in github_compare_dicts.items():
                    if repo in parsed_release_hashses[release]:
                        parsed_release_hashses[release][repo]['github'] = compare_dict

            # check file diffs for any new changelog files.
            changelog_filename = '_release_builds/change_logs/%s.json' % release
            changelog_dicts = {}
            if os.path.isfile(changelog_filename):
                # we already parsed the changelogs, load from that.

                print("Gathering change logs from local files for release %s" % release)

                with open(changelog_filename, 'r') as f:
                    changelog_dicts = json.load(f)

            else:

                print("Fetching new change logs from GitHub for release %s" % release)

                for repo, compare_dict in github_compare_dicts.items():
                    for file in compare_dict.get('files', []):
                        # look only for filenames that are in `changes/` directory.
                        if 'changes/' not in file['filename']:
                            continue
                        # look only for files that have been added.
                        if not file['status'] == 'added':
                            continue
                        if repo not in changelog_dicts:
                            changelog_dicts[repo] = {}

                        response = requests.get(file['raw_url'])

                        change_type = file['filename'].split('.')[-1]

                        # human readable labels.
                        if change_type in FIX_TYPES:
                            change_type = FIX_LABEL
                        elif change_type in FEATURE_TYPES:
                            change_type = FEATURE_LABEL
                        elif change_type in CHANGES_TYPES:
                            change_type = CHANGES_LABEL
                        elif change_type in MIGRATION_TYPES:
                            change_type = MIGRATION_LABEL
                        elif change_type in REMOVAL_TYPES:
                            change_type = REMOVAL_LABEL

                        if change_type not in changelog_dicts[repo]:
                            changelog_dicts[repo][change_type] = []

                        changelog_dicts[repo][change_type].append({
                            'canada_only': '.canada.' in file['filename'],
                            'backport': '.backport.' in file['filename'],
                            'change_log': response.content.decode('utf8'),
                            'hash': file['sha'],
                        })

                # save object to change log file.
                os.makedirs(os.path.dirname(changelog_filename), exist_ok=True)
                with open(changelog_filename, 'w', encoding='utf-8') as f:
                    json.dump(changelog_dicts, f, ensure_ascii=False, indent=4)

            # add github compare API info to parsed object for front-end.
            if changelog_dicts:
                for repo, changelog_dict in changelog_dicts.items():
                    if repo in parsed_release_hashses[release]:
                        parsed_release_hashses[release][repo]['change_logs'] = changelog_dict

    sorted_dict = dict(reversed(parsed_release_hashses.items()))
    parsed_release_hashses = sorted_dict

    print("Release notes built!")

    return parsed_release_hashses


html_context = {
    'release_tags': get_release_tags(order='-v:refname')[:-1],
    'release_hashes': parsed_release_hashses(),
    'version_prefix': FRONTEND_VERSION_PREFIX,
}
