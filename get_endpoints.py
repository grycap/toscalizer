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
from utils import get_node_endpoints, final_function_result, find_host_node


class GetEndPoints:

    def __init__(self, tosca_template):
        template = yaml.safe_load(open(tosca_template))
        self.tosca = ToscaTemplate(yaml_dict_tpl=template)

    def get_ports(self):
        endpoints = {}

        for node in self.tosca.nodetemplates:
            host_node = find_host_node(node, self.tosca.nodetemplates)
            if host_node:
                if host_node.name not in endpoints:
                    endpoints[host_node.name] = []
                endpoints[host_node.name].extend(get_node_endpoints(node, self.tosca.nodetemplates))

        ports = {}

        for node_name, node_endpoints in endpoints.items():
            for endpoint in node_endpoints:
                cap_props = endpoint.get_properties()
                if cap_props and "ports" in cap_props:
                    node_ports = final_function_result(self.tosca, cap_props["ports"].value, node)
                    if node_ports:
                        if node_name not in ports:
                            ports[node_name] = []
                        ports[node_name].extend(list(node_ports.values()))

        return ports


if __name__ == "__main__":
    import sys
    ports = GetEndPoints(sys.argv[1]).get_ports()
    print(ports)
