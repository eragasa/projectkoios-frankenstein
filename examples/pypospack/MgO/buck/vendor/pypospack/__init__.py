"""PyPosPack research software package.

Locally modified to compose this partial, provenance-bound package with the
remaining modules supplied by the exact pinned PyPosPack installation.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
__version__ = "0.1.0"
