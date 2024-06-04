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
from get_endpoints import GetEndPoints


@click.group()
def toscalizer_cli():
    pass


@click.command()
@click.argument('tosca_template', type=click.Path(exists=True))
@click.option('--json', '-j', help='Output the result in JSON format', is_flag=True)
def analyze(tosca_template, json):
    res = {}
    res["images"] = GetImages(tosca_template).get_container_images()
    res["ports"] = GetEndPoints(tosca_template).get_ports()
    res["tosca_type"] = "OpenStack"
    if res["images"]:
        res["tosca_type"] = "Kubernetes"

    if json:
        print(json_dumps.dumps(res, indent=2))
    else:
        print("Tosca type: %s" % res["tosca_type"])
        for image in res["images"]:
            print("Images:")
            print(image)
        for node in res["ports"].keys():
            print("Node: %s" % node)
            for port in res["ports"][node]:
                print("Ports:")
                print("%s: %s" % (port['protocol'], port['source']))


toscalizer_cli.add_command(analyze)


if __name__ == '__main__':
    toscalizer_cli()
