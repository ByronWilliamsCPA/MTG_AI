#!/usr/bin/env python3
"""Check that files using | union syntax have 'from __future__ import annotations'.

This script enforces a code quality standard to ensure that Python files using
the modern | union type syntax (introduced in Python 3.10) also include the
future annotations import for clarity and consistency.

NOTE: Python 3.14 deprecates 'from __future__ import annotations' (PEP 649),
but it will remain functional until at least Python 3.13 EOL in 2029. This
script will be updated when the ecosystem transitions to PEP 649's deferred
annotation evaluation. For now, continue using the future import for Python
3.10+ compatibility.

Usage:
    python scripts/check_type_hints.py [--fix]

Exit codes:
    0: All checks passed
    1: Violations found (or other errors)
"""

import argparse
import ast
import re
import sys
from pathlib import Path


class UnionSyntaxVisitor(ast.NodeVisitor):
    """AST visitor to detect | union syntax in type annotations."""

    def __init__(self) -> None:
        self.has_union_syntax = False

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Visit binary operations to detect | in type contexts."""
        if isinstance(node.op, ast.BitOr):
            # Check if this is likely a type annotation context
            # This is a heuristic - it will catch most cases
            self.has_union_syntax = True
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        """Visit function arguments with annotations."""
        if node.annotation:
            self.visit(node.annotation)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignments."""
        if node.annotation:
            self.visit(node.annotation)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions with return annotations."""
        if node.returns:
            self.visit(node.returns)
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation:
                self.visit(arg.annotation)
        if node.args.vararg and node.args.vararg.annotation:
            self.visit(node.args.vararg.annotation)
        if node.args.kwarg and node.args.kwarg.annotation:
            self.visit(node.args.kwarg.annotation)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self.visit_FunctionDef(node)  # type: ignore[arg-type]


def has_future_annotations_import(content: str) -> bool:
    """Check if file has 'from __future__ import annotations'."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                for alias in node.names:
                    if alias.name == "annotations":
                        return True
    return False


def has_union_pipe_syntax(content: str) -> bool:
    """Check if file uses | union syntax in type hints.

    Uses multiple detection methods:
    1. AST parsing to detect BinOp with BitOr in annotation contexts
    2. Regex pattern matching for common type hint patterns
    """
    # Method 1: AST-based detection
    try:
        tree = ast.parse(content)
        visitor = UnionSyntaxVisitor()
        visitor.visit(tree)
        if visitor.has_union_syntax:
            return True
    except SyntaxError:
        pass

    # Method 2: Regex patterns for common type hint usage
    # Match patterns like: ": int | str", "-> bool | None", "[int | float]"
    patterns = [
        r":\s*\w+\s*\|\s*\w+",  # : Type | Type
        r"->\s*\w+\s*\|\s*\w+",  # -> Type | Type
        r"\[\s*\w+\s*\|\s*\w+",  # [Type | Type
        r"=\s*\w+\s*\|\s*\w+",  # = Type | Type (in function params)
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            return True

    return False


def check_file(file_path: Path) -> tuple[bool, str]:
    """Check a single Python file for union syntax compliance.

    Returns:
        (is_compliant, message): Tuple indicating compliance and message
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Error reading file: {e}"

    has_union = has_union_pipe_syntax(content)
    has_import = has_future_annotations_import(content)

    if has_union and not has_import:
        return False, "Uses | union syntax without 'from __future__ import annotations'"

    return True, "OK"


def add_future_import(file_path: Path) -> bool:
    """Add 'from __future__ import annotations' to a file.

    Returns:
        True if the import was added, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        # Find the right place to insert the import
        # After shebang and module docstring, before other imports
        insert_index = 0

        # Skip shebang
        if lines and lines[0].startswith("#!"):
            insert_index = 1

        # Skip module docstring
        tree = ast.parse(content)
        if (
            tree.body
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
        ):
            # Find the line after the docstring
            docstring_end = tree.body[0].end_lineno or 0
            insert_index = max(insert_index, docstring_end)

        # Skip any existing __future__ imports
        for i, line in enumerate(lines[insert_index:], start=insert_index):
            if line.strip().startswith("from __future__ import"):
                continue
            if line.strip() and not line.strip().startswith("#"):
                insert_index = i
                break

        # Insert the import
        import_line = "from __future__ import annotations\n"
        if insert_index > 0 and not lines[insert_index - 1].strip():
            # If there's already a blank line, don't add another
            lines.insert(insert_index, import_line)
        else:
            # Add the import with a blank line after it
            lines.insert(insert_index, import_line)
            lines.insert(insert_index + 1, "\n")

        # Security: Validate file path is within expected directory
        if not file_path.resolve().is_relative_to(Path.cwd()):
            print(
                f"Security: Path {file_path} is outside current directory",
                file=sys.stderr,
            )
            return False

        file_path.write_text("".join(lines), encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error adding import to {file_path}: {e}", file=sys.stderr)
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check for | union syntax with future annotations import"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically add 'from __future__ import annotations' to files",
    )
    parser.add_argument(
        "--src-dir",
        type=Path,
        default=Path("src"),
        help="Source directory to check (default: src)",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Also check test files",
    )
    args = parser.parse_args()

    # Find all Python files
    python_files = []

    if args.src_dir.exists():
        python_files.extend(args.src_dir.rglob("*.py"))

    if args.include_tests:
        tests_dir = Path("tests")
        if tests_dir.exists():
            python_files.extend(tests_dir.rglob("*.py"))

    if not python_files:
        print(f"No Python files found in {args.src_dir}", file=sys.stderr)
        return 1

    violations = []
    fixed = []

    for file_path in python_files:
        # Skip __pycache__ and other generated files
        if "__pycache__" in str(file_path):
            continue

        is_compliant, message = check_file(file_path)

        if not is_compliant:
            if args.fix:
                if add_future_import(file_path):
                    fixed.append(file_path)
                    print(f"✓ Fixed: {file_path}")
                else:
                    violations.append((file_path, message))
                    print(f"✗ Failed to fix: {file_path}: {message}", file=sys.stderr)
            else:
                violations.append((file_path, message))
                print(f"✗ {file_path}: {message}", file=sys.stderr)

    # Print summary
    print()
    if violations:
        print(f"Found {len(violations)} violation(s):")
        for file_path, message in violations:
            print(f"  - {file_path}: {message}")
        print()
        print("Run with --fix to automatically add the import")
        return 1
    if fixed:
        print(f"Fixed {len(fixed)} file(s)")
        return 0
    print("All files compliant ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
