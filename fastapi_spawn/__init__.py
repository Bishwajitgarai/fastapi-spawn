"""fastapi-spawn — Production-ready FastAPI project scaffolding CLI."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("fastapi-spawn")
except PackageNotFoundError:
    __version__ = "0.4.37"  # Fallback

__author__ = "Bishwajit Garai"
__email__ = "bishwajitgarai@gmail.com"
__license__ = "MIT"
__description__ = "Production-ready FastAPI project scaffolding — with every integration you need."
