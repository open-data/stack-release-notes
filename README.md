# Open Government Canada CKAN Stack Releases

This repository contains a Sphinx project that gathers information from various CKAN project repos, and stores their hashes in files. It also checks the difference of the hashes between this repo's release tags, and gathers change logs and comparison objects from the GitHub API.

## How to make a Stack Release

When you are ready to deploy the code relating to the Open Government Canada CKAN project, you can tag this repository with a new release tag.

The tag should **strictly** follow the following date based format:

```
release/2024.05.07

OR (for same day)

release/2024.05.07.a
release/2024.05.07.b
```

A GitHub workflow will run on tagging and generate the differences between all the CKAN related projects, compile the Sphinx project, and publish it to GitHub Pages.

### Tagging from GitHub

It is important to only tag from GitHub and not locally as pushing local tags may cause issues with syncing tags and the GitHub workflow.

1. [Create a new release](https://github.com/open-data/ckan-stack-release-notes/releases/new);
2. Under `Choose a tag` dropdown, make a new tag, following the above format;
3. Check `Set as pre-release` and `Publish release`;
4. We only want the tag really, and do not need the release ZIPs. So delete the release (the tag will remain).

![Create a new tag and pre-release.](https://github.com/open-data/ckan-stack-release-notes/blob/main/.github/images/make-release.png?raw=true)

![Delete the pre-release.](https://github.com/open-data/ckan-stack-release-notes/blob/main/.github/images/delete-release.png?raw=true)

### I made a mistake tagging

If you make a mistake tagging this repo, you can manually fix it by deleting the tag and the related files for the tag:

* `docs/source/_release_builds/change_logs/<tag>.json`
* `docs/source/_release_builds/differences/<tag>.json`
* `docs/source/_release_builds/github/<tag>.json`
* `docs/source/_release_builds/releases/<tag>.json`

Once you have done that, you can re-tag this repo and the GitHub Workflow should run again.
