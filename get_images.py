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
from utils import final_function_result


class GetImages:

    def __init__(self, tosca_template):
        template = yaml.safe_load(open(tosca_template))
        self.tosca = ToscaTemplate(yaml_dict_tpl=template)

    @staticmethod
    def _is_docker_app(node):
        """
        Check if this node is a docker application
        """
        try:
            node_type = node.type_definition
        except AttributeError:
            node_type = node.definition

        while node_type.parent_type is not None:
            if node_type.type == 'tosca.nodes.Container.Application.Docker':
                return True
            else:
                node_type = node_type.parent_type

        return False

    def get_container_images(self):
        images = []

        for node in self.tosca.nodetemplates:
            if self._is_docker_app(node):
                artifacts = node.type_definition.get_value('artifacts', node.entity_tpl, True)

                for artifact in list(artifacts.values()):
                    if artifact.get('type') == 'tosca.artifacts.Deployment.Image.Container.Docker':
                        images.append(final_function_result(self.tosca, artifact.get('file'), node))

        return images


if __name__ == "__main__":
    import sys
    images = GetImages(sys.argv[1]).get_container_images()
    for image in images:
        print(image)
