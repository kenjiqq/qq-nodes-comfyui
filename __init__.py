import os, shutil
import folder_paths
from .nodes import NODE_CLASS_MAPPINGS

module_js_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")
application_root_directory = os.path.dirname(folder_paths.__file__)
application_web_extensions_directory = os.path.join(application_root_directory, "web", "extensions", "qq-nodes")

shutil.copytree(module_js_directory, application_web_extensions_directory, dirs_exist_ok=True)