# test_import.py: checks that the compressor_agent package can be imported.
# It fails if the package is missing, misnamed, or has a broken __init__.py.
# This is the only test in Stage 0; real tests arrive with real modules.
import importlib


def test_package_imports() -> None:
    module = importlib.import_module("compressor_agent")
    assert module.__name__ == "compressor_agent"
