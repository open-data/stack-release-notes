# -*- coding: utf-8 -*-
import json
import re
import os
import subprocess
import requests
import copy
from markupsafe import Markup
from markdown import markdown
from bleach import clean as bleach_clean, ALLOWED_TAGS, ALLOWED_ATTRIBUTES

MARKDOWN_TAGS = set([
    'del', 'dd', 'dl', 'dt', 'h1', 'h2',
    'h3', 'img', 'kbd', 'p', 'pre', 's',
    'sup', 'sub', 'strike', 'br', 'hr',
    'ul', 'ol', 'li',
]).union(ALLOWED_TAGS)

MARKDOWN_ATTRIBUTES = copy.deepcopy(ALLOWED_ATTRIBUTES)
MARKDOWN_ATTRIBUTES.setdefault('img', []).extend(['src', 'alt', 'title'])

# find all tags but ignore < in the strings so that we can use it correctly in markdown
RE_MD_HTML_TAGS = re.compile('<[^><]*>')

class literal(Markup):
    """
    Represents an HTML literal.
    """
    __slots__ = ()

    @classmethod
    def escape(cls, s):
        if s is None:
            return Markup("")
        return super(literal, cls).escape(s)

STACK = {
    'ckan': {
        'https://github.com/open-data/ckan.git'                     : 'canada-v2.10',
        'https://github.com/ckan/ckanapi.git'                       : 'master',
        'https://github.com/open-data/ckanext-canada.git'           : 'canada-v2.10',
        'https://github.com/open-data/ckanext-cloudstorage.git'     : 'canada-v2.10',
        'https://github.com/open-data/ckanext-csrf-filter.git'      : 'canada-py3',  # MARK: discontinued
        'https://github.com/open-data/ckanext-dcat.git'             : 'canada-v2.10',
        'https://github.com/ckan/ckanext-dsaudit.git'               : 'master',
        'https://github.com/ckan/ckanext-excelforms.git'            : 'main',
        'https://github.com/ckan/ckanext-fluent.git'                : 'master',
        'https://github.com/open-data/ckanext-gcnotify.git'         : 'master',
        'https://github.com/open-data/ckanext-openapiview.git'      : 'main',
        'https://github.com/open-data/ckanext-power-bi.git'         : 'main',
        'https://github.com/open-data/ckanext-recombinant.git'      : 'canada-v2.10',
        'https://github.com/ckan/ckanext-scheming.git'              : 'master',
        'https://github.com/open-data/ckanext-security.git'         : 'canada-v2.10',
        'https://github.com/open-data/ckanext-validation.git'       : 'canada-v2.10',
        'https://github.com/open-data/ckanext-xloader.git'          : 'canada-v2.10',
        'https://github.com/ckan/ckantoolkit.git'                   : 'master',
        'https://github.com/open-data/goodtables.git'               : 'canada-py3',  # MARK: discontinued
        'https://github.com/open-data/frictionless-py.git'          : 'canada-v2.10',
    },
    'django': {
        'https://github.com/open-data/oc_search.git'                : 'master',
        # Not included for now.
        # 'https://github.com/open-data/SolrClient.git'               : 'master',
        # 'https://github.com/open-data/oc_searches.git'              : 'main',
    },
    'drupal': {
        'https://github.com/open-data/opengov.git'                  : 'master',
        'https://github.com/open-data/og.git'                       : 'master',
        'https://github.com/open-data/gcweb_bootstrap.git'          : 'master',
    },
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

RELEASE_TYPES = [
    'release',
]
RELEASE_LABEL = 'Releases'

LABEL_MAP = [RELEASE_LABEL, FEATURE_LABEL, FIX_LABEL, REMOVAL_LABEL, CHANGES_LABEL, MIGRATION_LABEL]
LABEL_ICONS = {
    RELEASE_LABEL: 'fa-tag',
    FEATURE_LABEL: 'fa-code-fork',
    FIX_LABEL: 'fa-wrench',
    REMOVAL_LABEL: 'fa-trash',
    CHANGES_LABEL: 'fa-code',
    MIGRATION_LABEL: 'fa-database',
}


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Open Government Canada Stack'
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
    'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v5_0_1/wet-boew/css/theme.min.css',
    'css/canada_theme.css',
    'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
]
html_js_files = [
    'js/canada.js',
]
html_show_sphinx = False
html_logo = 'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v5_0_1/wet-boew/assets/sig-spl.svg'
html_favicon = 'https://www.canada.ca/etc/designs/canada/cdts/gcweb/v5_0_1/wet-boew/assets/favicon.ico'

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

    for project_name, project_stack in STACK.items():

        if project_name not in release_hashes:
            release_hashes[project_name] = {}

        for repo, branch in project_stack.items():

            latest_hash = get_latest_commit_hash(repo, branch)
            repo_uri = repo.replace('.git', '')
            repo_name = repo_uri.split('/')[-1]

            release_hashes[project_name][repo_name] = {
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

                    for project_name, prev_project_stack in prev_release_dict.items():

                        if project_name not in release_dict:
                            print("Project %s no longer exists in the stack. Skipping..." % project_name)
                            continue

                        if project_name not in parsed_release_hashses[release]:
                            parsed_release_hashses[release][project_name] = {}

                        for repo, info in prev_project_stack.items():
                            # a repo in the previous release is no longer in
                            # the next release. Consider this a removal.
                            if repo not in release_dict[project_name]:
                                parsed_release_hashses[release][project_name][repo] = {
                                    'message': 'Repository discontinued',
                                }

                        for repo, info in release_dict[project_name].items():
                            # the repo was not in the previous release,
                            # consider it an initial release for that repo.
                            if repo not in prev_project_stack:
                                parsed_release_hashses[release][project_name][repo] = {
                                    'message': 'Repository added',
                                }
                            # the commit hash between the releases is different,
                            # so this is a code release.
                            elif info['hash'] != prev_project_stack[repo]['hash']:
                                parsed_release_hashses[release][project_name][repo] = {
                                    'uri': info['uri'],
                                    'prev': prev_project_stack[repo]['hash'],
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

                for project_name, project_stack in parsed_release_hashses[release].items():

                    if project_name not in github_compare_dicts:
                        github_compare_dicts[project_name] = {}

                    for repo, info in project_stack.items():
                        endpoint = info['uri'].replace('https://github.com', 'https://api.github.com/repos')
                        endpoint += '/compare/%s...%s' % (info['prev'], info['head'])
                        response = requests.get(endpoint)
                        github_compare_dicts[project_name][repo] = json.loads(response.content)

                # save object to compare file.
                os.makedirs(os.path.dirname(github_filename), exist_ok=True)
                with open(github_filename, 'w', encoding='utf-8') as f:
                    json.dump(github_compare_dicts, f, ensure_ascii=False, indent=4)

            # add github compare API info to parsed object for front-end.
            if github_compare_dicts:
                for project_name, project_stack in github_compare_dicts.items():
                    for repo, compare_dict in project_stack.items():
                        if repo in parsed_release_hashses[release][project_name]:
                            parsed_release_hashses[release][project_name][repo]['github'] = compare_dict

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

                for project_name, project_stack in github_compare_dicts.items():

                    if project_name not in changelog_dicts:
                        changelog_dicts[project_name] = {}

                    for repo, compare_dict in project_stack.items():
                        for file in compare_dict.get('files', []):
                            # look only for filenames that are in `changes/` directory.
                            if 'changes/' not in file['filename']:
                                continue
                            # look only for files that have been added.
                            if not file['status'] == 'added':
                                continue
                            if repo not in changelog_dicts[project_name]:
                                changelog_dicts[project_name][repo] = {}

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
                            elif change_type in RELEASE_TYPES:
                                change_type = RELEASE_LABEL

                            if change_type not in changelog_dicts[project_name][repo]:
                                changelog_dicts[project_name][repo][change_type] = []

                            changelog_dicts[project_name][repo][change_type].append({
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
                for project_name, project_stack in changelog_dicts.items():
                    for repo, changelog_dict in project_stack.items():
                        if repo in parsed_release_hashses[release][project_name]:
                            sorted_dict = {}
                            for _key in LABEL_MAP:
                                if _key in changelog_dict:
                                    sorted_dict[_key] = changelog_dict[_key]
                            parsed_release_hashses[release][project_name][repo]['change_logs'] = sorted_dict

    sorted_dict = dict(reversed(parsed_release_hashses.items()))
    parsed_release_hashses = sorted_dict

    print("Release notes built!")

    return parsed_release_hashses


def get_filled_releases():
    release_tags = get_release_tags(order='-v:refname')
    release_hashes = parsed_release_hashses()

    filled_release_hashes = {}

    for release, project in release_hashes.items():
        release_has_diffs = False
        for project_name, repos in project.items():
            if repos:
                release_has_diffs = True
                if release not in filled_release_hashes:
                    filled_release_hashes[release] = {}
                filled_release_hashes[release][project_name] = repos
        if not release_has_diffs:
            release_tags.remove(release)

    return release_tags, filled_release_hashes


def render_markdown(data):
    """
    Returns the data as rendered markdown

    :param auto_link: Should ckan specific links be created e.g. `group:xxx`
    :type auto_link: bool
    :param allow_html: If True then html entities in the markdown data.
        This is dangerous if users have added malicious content.
        If False all html tags are removed.
    :type allow_html: bool
    """
    #FIXME: sublists
    if not data:
        return ''
    markdown_lists = [
        '\n  -',
        '\n  *',
        '\n  +',
        '\n  1.',
    ]
    for match in markdown_lists:
        if match in data:
            data = data.replace(match, '\n%s' % match)
    data = RE_MD_HTML_TAGS.sub('', data.strip())
    data = bleach_clean(
        markdown(data), strip=True,
        tags=MARKDOWN_TAGS, attributes=MARKDOWN_ATTRIBUTES)
    return literal(data)


release_tags, release_hashes = get_filled_releases()
html_context = {
    'release_tags': release_tags,
    'release_hashes': release_hashes,
    'type_icons': LABEL_ICONS,
    'version_prefix': FRONTEND_VERSION_PREFIX,
    'render_markdown': render_markdown,
}
