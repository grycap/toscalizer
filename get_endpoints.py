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
import yaml
from toscaparser.tosca_template import ToscaTemplate
from utils import get_node_endpoints, final_function_result


class GetEndPoints:

    def __init__(self, tosca_template):
        template = yaml.safe_load(open(tosca_template))
        self.tosca = ToscaTemplate(yaml_dict_tpl=template)

    def get_ports(self):
        endpoints = []

        for node in self.tosca.nodetemplates:
            node_endpoints = get_node_endpoints(node, self.tosca.nodetemplates)
            endpoints.extend(node_endpoints)

        ports = []

        for endpoint in endpoints:
            cap_props = endpoint.get_properties()
            if cap_props and "ports" in cap_props:
                node_ports = final_function_result(self.tosca, cap_props["ports"].value, node)
                if node_ports:
                    for p in node_ports.values():
                        ports.append(p)

        return ports


if __name__ == "__main__":
    import sys
    ports = GetEndPoints(sys.argv[1]).get_ports()
    for port in ports:
        print(port)
