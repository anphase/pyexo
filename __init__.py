try:
    import api
except ImportError:
    from .api import *
try:
    import auth
except ImportError:
    from .auth import *
try:
    import basemanager
except ImportError:
    from .basemanager import *
try:
    from vumeda_api import settings
except ImportError:
    from .basemanager import *
try:
    import exceptions
except ImportError:
    from .exceptions import *
try:
    import manager
except ImportError:
    from .manager import *
try:
    import utils
except ImportError:
    from .utils import *

__version__ = "0.1"
