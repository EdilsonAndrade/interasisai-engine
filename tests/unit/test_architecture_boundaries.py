import ast
from pathlib import Path


FORBIDDEN_IMPORTS = {
    "domain": {"fastapi", "starlette"},
}


def _imports_from_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_domain_layer_has_no_framework_imports() -> None:
    domain_dir = Path("domain")
    py_files = [p for p in domain_dir.rglob("*.py") if p.name != "__init__.py"]

    for file_path in py_files:
        imports = _imports_from_file(file_path)
        for forbidden in FORBIDDEN_IMPORTS["domain"]:
            assert forbidden not in imports, f"Forbidden import '{forbidden}' found in {file_path}"
