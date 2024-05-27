import yaml
import sys
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.functions import Function, is_function, get_function


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

    @staticmethod
    def _final_function_result(tosca, func, node):
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
                    func[k] = GetImages._final_function_result(v, node)
                return func

    def get_container_images(self):
        images = []

        for node in self.tosca.nodetemplates:
            if self._is_docker_app(node):
                artifacts = node.type_definition.get_value('artifacts', node.entity_tpl, True)

                for artifact in list(artifacts.values()):
                    if artifact.get('type') == 'tosca.artifacts.Deployment.Image.Container.Docker':
                        images.append(self._final_function_result(self.tosca, artifact.get('file'), node))

        return images


if __name__ == "__main__":
    images = GetImages(sys.argv[1]).get_container_images()
    for image in images:
        print(image)
