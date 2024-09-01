from .nodes import NODE_CLASS_MAPPINGS

import os
import folder_paths

# In the past we installed the extension by copying the extensions.js file to the web/extensions/qq-nodes folder, so we need to delete it if it exists when users upgrade to the new version.
application_root_directory = os.path.dirname(folder_paths.__file__)
application_web_extensions_directory = os.path.join(application_root_directory, "web", "extensions", "qq-nodes")
file_to_delete = os.path.join(application_web_extensions_directory, "extension.js")
if os.path.exists(file_to_delete):
    os.remove(file_to_delete)

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "WEB_DIRECTORY"]
