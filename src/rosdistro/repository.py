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

from .status import valid_statuses


class Repository(object):

    def __init__(self, name, data):
        self.name = name
        self.type = data.get('type', 'git')
        self.url = data['url']
        self.version = data.get('version', None)
        if self.version is not None:
            assert 'tags' in data

        self.tags = {}
        if 'tags' in data:
            assert 'release' in data['tags']
            for tag_type in data['tags']:
                tag_data = data['tags'][tag_type]
                self.tags[tag_type] = str(tag_data)

        self.status = data.get('status', None)
        if self.status is not None:
            assert self.status in valid_statuses
        self.status_description = data.get('status_description', None)

        self.package_names = []
        if 'packages' in data:
            self.package_names = sorted(data['packages'].keys())

    def get_data(self):
        data = {}
        if self.type != 'git':
            data['type'] = str(self.type)
        data['url'] = str(self.url)
        data['version'] = self.version
        if self.version is not None and self.tags:
            data['tags'] = {}
            for tag in self.tags:
                data['tags'][tag] = str(self.tags[tag])
        if self.status is not None:
            data['status'] = str(self.status)
        if self.status_description is not None:
            data['status_description'] = str(self.status_description)
        return data
