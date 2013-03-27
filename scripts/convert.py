#!/usr/bin/env python

# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Open Source Robotics Foundation, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Open Source Robotics Foundation, Inc. nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import urllib2
import yaml

from rosdistro.loader import load_url
from rosdistro.release_file import ReleaseFile


BASE_SRC_URL = 'https://raw.github.com/ros/rosdistro/master'


def get_targets():
    url = BASE_SRC_URL + '/releases/targets.yaml'
    print('Load "%s"' % url)
    yaml_str = load_url(url)
    data = yaml.load(yaml_str)
    targets = {}
    for d in data:
        targets[d.keys()[0]] = d.values()[0]
    return targets


def convert_release(dist_name, targets):
    url = BASE_SRC_URL + '/releases/%s.yaml' % dist_name
    print('Load "%s"' % url)
    yaml_str = load_url(url)
    input_ = yaml.load(yaml_str)

    # improve conversion performance by reusing results from last run
    last_dist = None
    if os.path.exists(dist_name + '.yaml'):
        with open(dist_name + '.yaml', 'r') as f:
            last_data = yaml.load(f.read())
            last_dist = ReleaseFile(dist_name, last_data)

    output = {}
    output['gbp-repos'] = {'You must update to a newer rosdep version by calling..sudo apt-get update && sudo apt-get install python-rosdep (make sure to uninstall the pip version on Ubuntu': None}
    output['type'] = 'release'
    output['version'] = 1
    output['platforms'] = targets[dist_name]
    output['repositories'] = {}

    for repo_name in sorted(input_['repositories']):
        input_repo = input_['repositories'][repo_name]
        output_repo = {}
        output_repo['url'] = input_repo['url']
        output_repo['version'] = input_repo['version']
        pkg_name = repo_name
        if 'packages' in input_repo:
            output_repo['packages'] = {}
            for pkg_name in input_repo['packages']:
                if len(input_repo['packages']) == 1 and pkg_name == repo_name and input_repo['packages'][pkg_name] is None:
                    del output_repo['packages']
                    break
                output_repo['packages'][pkg_name] = None
                if input_repo['packages'][pkg_name] is not None:
                    output_repo['packages'][pkg_name] = {'subfolder': input_repo['packages'][pkg_name]}
        output['repositories'][repo_name] = output_repo

        if output_repo['version'] is not None:
            tag_template = _get_tag_template(dist_name, output_repo, pkg_name, last_dist.repositories[repo_name] if last_dist and repo_name in last_dist.repositories else None)
            output_repo['tags'] = {'release': tag_template}

    yaml_str = yaml.dump(output, default_flow_style=False)
    yaml_str = yaml_str.replace(': null', ':')
    with open(dist_name + '.yaml', 'w') as f:
        f.write(yaml_str)


def _get_tag_template(dist_name, repo, pkg_name, last_repo=None):
    # reuse tag template if fetched before for the same repo and version
    if last_repo and last_repo.version == repo['version']:
        if 'release' in last_repo.tags:
            return last_repo.tags['release']

    assert 'github.com' in repo['url']
    release_tag = 'release/{0}/{1}/{2}'.format(dist_name, pkg_name, repo['version'])
    url = _github_raw_url(repo['url'], release_tag)
    try:
        try:
            urllib2.urlopen(url).read()
            return 'release/%s/{package}/{version}' % dist_name
        except Exception:  # TODO: catch the correct Exception here, let others raise
            # try alternative tag
            upstream_version = repo['version'].split('-')[0]
            release_tag = 'release/{0}/{1}'.format(pkg_name, upstream_version)
            url = _github_raw_url(repo['url'], release_tag)
            urllib2.urlopen(url).read()
            return 'release/{package}/{upstream_version}'
    except Exception as e:  # TODO: catch the correct Exception here, let others raise
        raise RuntimeError('Could not determine tag using %s, %s, %s: %s' % (dist_name, repo, pkg_name, e))


def _github_raw_url(url, tag):
    url = url.replace('.git', '/tree/%s/' % tag)
    url = url.replace('git://', 'https://')
    #url = url.replace('https://', 'https://raw.')
    return url


def convert_test(dist_name):
    url = BASE_SRC_URL + '/releases/%s-devel.yaml' % dist_name
    print('Load "%s"' % url)
    yaml_str = load_url(url)
    input_ = yaml.load(yaml_str)

    output = {}
    output['type'] = 'test'
    output['version'] = 1
    output['repositories'] = {}

    for repo_name in sorted(input_['repositories']):
        input_repo = input_['repositories'][repo_name]
        output_repo = {}
        output_repo['type'] = input_repo['type']
        output_repo['url'] = input_repo['url']
        output_repo['version'] = input_repo['version']
        if 'packages' in input_repo:
            output_repo['packages'] = {}
            for pkg_name in input_repo['packages']:
                output_repo['packages'][pkg_name] = None
                if input_repo['packages'][pkg_name] is not None:
                    output_repo['packages'][pkg_name] = {'subfolder': input_repo['packages'][pkg_name]}
        output['repositories'][repo_name] = output_repo

    yaml_str = yaml.dump(output, default_flow_style=False)
    yaml_str = yaml_str.replace(': null', ':')
    with open(dist_name + '-devel.yaml', 'w') as f:
        f.write(yaml_str)


if __name__ == '__main__':
    targets = get_targets()
    for distro in ['groovy', 'hydro']:
        convert_release(distro, targets)
        convert_test(distro)
