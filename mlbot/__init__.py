"""Jupyter server extension for version control"""

from .handlers import ChangeVersionHandler, SaveLocallyHandler
from notebook.utils import url_path_join


def load_jupyter_server_extension(nbapp):
    """Load and initialise the server extension."""
    webapp = nbapp.web_app
    base_url = webapp.settings['base_url']

    change_version_handler = (url_path_join(base_url, '/selectversion'), ChangeVersionHandler)
    save_locally_handler = (url_path_join(base_url, '/savelocally'), SaveLocallyHandler)
    webapp.add_handlers(".*$", [change_version_handler, save_locally_handler])


def _jupyter_server_extension_paths():
    return [{
        'module': __name__
    }]
    
    
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="static",
        dest="mlbot",
        require="mlbot/main")]

