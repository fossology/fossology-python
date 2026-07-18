#!/usr/bin/env python3
"""Check Fossology REST API coverage by this Python wrapper.

Fetches the official OpenAPI spec from GitHub (or accepts a local file / live
server URL), then compares every path+method pair in the spec against the
``API Endpoint:`` annotations documented in this library's docstrings.

Usage::

    # Against the upstream spec on GitHub (default):
    python check_api_coverage.py

    # Against a local spec file:
    python check_api_coverage.py --spec /path/to/openapi.yaml

    # Against a running Fossology instance:
    python check_api_coverage.py --spec http://fossology/repo/api/v1/openapi

"""
import argparse
import re
import sys
import urllib.request
from pathlib import Path

import yaml

OPENAPI_URL = (
    "https://raw.githubusercontent.com/fossology/fossology/master"
    "/src/www/ui/api/documentation/openapi.yaml"
)
SOURCE_DIR = Path(__file__).parent.parent / "fossology"
HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}


def normalize_path(path: str) -> str:
    """Replace every ``{param_name}`` segment with ``{param}`` for comparison."""
    return re.sub(r"\{[^}]+\}", "{param}", path)


def fetch_spec(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source) as resp:  # noqa: S310
            return resp.read().decode()
    return Path(source).read_text()


def parse_spec_endpoints(yaml_text: str) -> set[tuple[str, str]]:
    """Return ``{(METHOD, /path), …}`` from an OpenAPI YAML document."""
    spec = yaml.safe_load(yaml_text)
    endpoints: set[tuple[str, str]] = set()
    for path, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in path_item:
            if method.lower() in HTTP_METHODS:
                endpoints.add((method.upper(), path))
    return endpoints


def parse_implemented_endpoints(source_dir: Path) -> set[tuple[str, str]]:
    """Return ``{(METHOD, /path), …}`` found in ``API Endpoint:`` docstring lines."""
    pattern = re.compile(
        r"API\s+[Ee]ndpoint:\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(/\S+)",
        re.IGNORECASE,
    )
    endpoints: set[tuple[str, str]] = set()
    for py_file in source_dir.glob("*.py"):
        for match in pattern.finditer(py_file.read_text()):
            endpoints.add((match.group(1).upper(), match.group(2).rstrip(".")))
    return endpoints


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--spec",
        default=OPENAPI_URL,
        metavar="URL_OR_FILE",
        help="OpenAPI YAML source: a URL or a local file path (default: GitHub upstream)",
    )
    args = parser.parse_args()

    print(f"Fetching OpenAPI spec from:\n  {args.spec}\n")
    try:
        yaml_text = fetch_spec(args.spec)
    except Exception as exc:
        print(f"ERROR: Could not fetch spec: {exc}", file=sys.stderr)
        sys.exit(1)

    spec_endpoints = parse_spec_endpoints(yaml_text)
    impl_endpoints = parse_implemented_endpoints(SOURCE_DIR)

    # Build normalised lookup tables
    norm_spec: dict[tuple[str, str], tuple[str, str]] = {
        (m, normalize_path(p)): (m, p) for m, p in spec_endpoints
    }
    norm_impl: dict[tuple[str, str], tuple[str, str]] = {
        (m, normalize_path(p)): (m, p) for m, p in impl_endpoints
    }

    covered = {k for k in norm_impl if k in norm_spec}
    not_implemented = sorted(v for k, v in norm_spec.items() if k not in norm_impl)
    not_in_spec = sorted(v for k, v in norm_impl.items() if k not in norm_spec)

    total = len(norm_spec)
    n_covered = len(covered)
    pct = n_covered / total * 100 if total else 0.0

    sep = "=" * 62
    print(sep)
    print("  Fossology REST API — Coverage Report")
    print(sep)
    print(f"  Spec endpoints    : {total}")
    print(f"  Implemented       : {n_covered}")
    print(f"  Coverage          : {pct:.1f}%")
    print(sep)

    if not_implemented:
        print(f"\nNot yet implemented ({len(not_implemented)} endpoints):")
        for method, path in not_implemented:
            print(f"  {method:<8} {path}")

    if not_in_spec:
        print(f"\nIn wrapper but not found in spec ({len(not_in_spec)} endpoints):")
        for method, path in not_in_spec:
            print(f"  {method:<8} {path}")

    print()


if __name__ == "__main__":
    main()
