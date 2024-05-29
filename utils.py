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
from toscaparser.functions import Function, is_function, get_function


def final_function_result(tosca, func, node):
    """
    Take a translator.toscalib.functions.Function and return the final result
    (in some cases the result of a function is another function)
    """
    if not isinstance(func, (Function, dict, list)):
        return func
    elif isinstance(func, Function):
        return func.result()
    else:
        if is_function(func):
            func = get_function(tosca, node, func)
            return func.result()
        else:  # a plain dict
            for k, v in func.items():
                func[k] = final_function_result(tosca, v, node)
            return func


def get_root_parent_type(node):
    """
    Get the root parent type of a node (just before the tosca.nodes.Root)
    """
    try:
        node_type = node.type_definition
    except AttributeError:
        node_type = node.definition

    while True:
        if node_type.parent_type is not None:
            if node_type.parent_type.type.endswith(".Root"):
                return node_type
            else:
                node_type = node_type.parent_type
        else:
            return node_type


def is_derived_from(rel, parent_type):
    """
    Check if a node is a descendant from a specified parent type
    """
    if isinstance(parent_type, list):
        parent_types = parent_type
    else:
        parent_types = [parent_type]
    while True:
        if rel.type in parent_types:
            return True
        else:
            if rel.parent_type:
                rel = rel.parent_type
            else:
                return False


def find_host_node(node, nodetemplates, base_root_type="tosca.nodes.Compute", node_type=None):
    """
    Select the node to host each node
    """
    if node_type and node.type == node_type:
        return node
    else:
        root_type = get_root_parent_type(node).type
        if root_type == base_root_type:
            return node

    if node.requirements:
        for r, n in node.relationships.items():
            # check for a HosteOn relation
            if is_derived_from(r, r.HOSTEDON) or is_derived_from(r, r.BINDSTO):
                root_type = get_root_parent_type(n).type
                if root_type == base_root_type:
                    return n
                else:
                    return find_host_node(n, nodetemplates, base_root_type, node_type)


def get_node_endpoints(node, nodetemplates):
    """ Get all endpoint associated with a node """
    endpoints = []

    # First add hosted nodes ones
    for other_node in nodetemplates:
        root_type = get_root_parent_type(other_node).type
        compute = None
        if root_type != "tosca.nodes.Compute":
            # Select the host to host this element
            compute = find_host_node(other_node, nodetemplates)

        if compute and compute.name == node.name:
            node_caps = other_node.get_capabilities()
            for cap in node_caps.values():
                root_type = get_root_parent_type(cap).type
                if root_type == "tosca.capabilities.Endpoint":
                    endpoints.append(cap)

    # Then add its own endpoints
    node_caps = node.get_capabilities()
    if node_caps:
        if "endpoint" in node_caps and node_caps["endpoint"]:
            endpoints.append(node_caps["endpoint"])

    return endpoints
