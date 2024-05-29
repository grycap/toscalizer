#!/usr/bin/env python3
# Copyright (C) GRyCAP - I3M - UPV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import json as json_dumps

from get_images import GetImages


@click.group()
def toscalizer_cli():
    pass


@click.command()
@click.argument('tosca_template', type=click.Path(exists=True))
@click.option('--json', '-j', help='Output the result in JSON format', is_flag=True)
def get_images(tosca_template, json):
    images = GetImages(tosca_template).get_container_images()
    if json:
        print(json_dumps.dumps(images))
    else:
        for image in images:
            print(image)


toscalizer_cli.add_command(get_images)


if __name__ == '__main__':
    toscalizer_cli()
