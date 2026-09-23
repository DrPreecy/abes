#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11+ should provide this.
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
ABES_START = "<!-- ABES:START -->"
ABES_END = "<!-- ABES:END -->"
MANAGED_MARKER = "<!-- ABES:MANAGED -->"
MANIFEST_LANGUAGE_MAP = {
    "package.json": "JavaScript/TypeScript",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "pom.xml": "Java",
    "build.gradle": "Java/Kotlin",
    "Gemfile": "Ruby",
}
COMMON_MANIFESTS = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
    "Gemfile",
    "Makefile",
    "docker-compose.yml",
    "Dockerfile",
}
EXCLUDED_DIR_NAMES = {
    ".abes",
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    ".yarn",
    ".pnpm-store",
    "__pycache__",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    "coverage",
}
SOURCE_DIR_NAMES = {"src", "app", "lib", "cmd", "server", "client"}
TEST_DIR_NAMES = {"tests", "test", "__tests__", "spec"}
DOC_DIR_NAMES = {"docs"}
LEGACY_MANAGED_FILES = (
    ".abes/project/identity.md",
    ".abes/project/architecture.md",
    ".abes/project/goals.md",
    ".abes/memory/opportunities.md",
)


@dataclass
class Detection:
    manifests: List[str]
    languages: List[str]
    source_locations: List[str]
    test_locations: List[str]
    doc_locations: List[str]
    commands: List[str]
    readme_signal: str
    initial_observation: str
    initial_inference: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize ABES in a target repository.")
    parser.add_argument("target", nargs="?", default=".", help="Target repository path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files")
    return parser.parse_args()


def detect_repo_name(target: Path) -> str:
    return target.resolve().name or "project"


def relative_list(paths: Iterable[Path], target: Path) -> List[str]:
    return sorted({str(path.relative_to(target)) for path in paths})


def walk_repository(target: Path) -> tuple[List[Path], List[Path], List[Path], List[Path]]:
    manifests: List[Path] = []
    source_locations: List[Path] = []
    test_locations: List[Path] = []
    doc_locations: List[Path] = []

    for root, dirs, files in os.walk(target, topdown=True, followlinks=False):
        root_path = Path(root)
        kept_dirs: List[str] = []
        for directory in dirs:
            candidate = root_path / directory
            if directory in EXCLUDED_DIR_NAMES or candidate.is_symlink():
                continue
            kept_dirs.append(directory)
            if directory in SOURCE_DIR_NAMES:
                source_locations.append(candidate)
            if directory in TEST_DIR_NAMES:
                test_locations.append(candidate)
            if directory in DOC_DIR_NAMES:
                doc_locations.append(candidate)
        dirs[:] = kept_dirs

        for filename in files:
            candidate = root_path / filename
            if candidate.is_symlink():
                continue
            if filename in COMMON_MANIFESTS:
                manifests.append(candidate)
            if filename == "README.md":
                doc_locations.append(candidate)

    return manifests, source_locations, test_locations, doc_locations


def detect_manifests(target: Path) -> List[Path]:
    manifests, _, _, _ = walk_repository(target)
    return manifests


def normalize_json_object(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def flatten_dependency_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        for package_name, package_value in value.items():
            if isinstance(package_name, str):
                names.add(package_name.lower())
            names.update(flatten_dependency_names(package_value))
    elif isinstance(value, list):
        for entry in value:
            names.update(flatten_dependency_names(entry))
    elif isinstance(value, str):
        package_name = re.split(r"[\s<>=!~\[\];,]", value.strip(), maxsplit=1)[0]
        if package_name:
            names.add(package_name.lower())
    return names


def detect_pyproject_commands(pyproject: Path) -> List[str]:
    if tomllib is None:
        return ["inspect Python project test/lint commands before assuming any"]

    try:
        parsed = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return ["inspect Python project test/lint commands before assuming any"]

    project = parsed.get("project")
    project_section = project if isinstance(project, dict) else {}
    dependencies = flatten_dependency_names(project_section.get("dependencies"))
    dependencies.update(flatten_dependency_names(project_section.get("optional-dependencies")))
    dependencies.update(flatten_dependency_names(parsed.get("dependency-groups")))
    build_system = parsed.get("build-system")
    if isinstance(build_system, dict):
        dependencies.update(flatten_dependency_names(build_system.get("requires")))

    tool = parsed.get("tool")
    tool_section = tool if isinstance(tool, dict) else {}

    commands: List[str] = []
    if "pytest" in dependencies or "pytest" in tool_section:
        commands.append("python -m pytest")
    if "ruff" in dependencies or "ruff" in tool_section:
        commands.append("ruff check .")
    return commands or ["inspect Python project test/lint commands before assuming any"]


def detect_commands(target: Path) -> List[str]:
    commands: List[str] = []

    package_json = target / "package.json"
    if package_json.exists() and not package_json.is_symlink():
        try:
            parsed = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            parsed = {}
        data = normalize_json_object(parsed)
        scripts = data.get("scripts")
        script_map = scripts if isinstance(scripts, dict) else {}
        for key in ("test", "lint", "build", "dev", "start"):
            if isinstance(script_map.get(key), str):
                commands.append(f"npm run {key}")

    pyproject = target / "pyproject.toml"
    if pyproject.exists() and not pyproject.is_symlink():
        commands.extend(detect_pyproject_commands(pyproject))

    makefile = target / "Makefile"
    if makefile.exists() and not makefile.is_symlink():
        makefile_text = makefile.read_text(encoding="utf-8")
        make_targets = {
            match.group(1)
            for match in re.finditer(r"^([A-Za-z0-9_.-]+):", makefile_text, flags=re.MULTILINE)
        }
        for target_name in ("test", "lint", "build"):
            if target_name in make_targets:
                commands.append(f"make {target_name}")

    if (target / "go.mod").exists():
        commands.append("go test ./...")

    if (target / "Cargo.toml").exists():
        commands.append("cargo test")

    unique: List[str] = []
    for command in commands:
        if command not in unique:
            unique.append(command)
    return unique or ["inspect repository-specific build/test commands before assuming any"]


def detect_languages(manifests: List[str]) -> List[str]:
    detected = []
    for manifest in manifests:
        label = MANIFEST_LANGUAGE_MAP.get(Path(manifest).name)
        if label and label not in detected:
            detected.append(label)
    return detected or ["undetermined from common manifests"]


def detect_readme_signal(target: Path) -> str:
    readme = target / "README.md"
    if not readme.exists() or readme.is_symlink():
        return "no root README summary detected during bootstrap"

    text = readme.read_text(encoding="utf-8").strip()
    if not text:
        return "root README exists but does not yet describe the project"

    heading = ""
    paragraph_lines: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if paragraph_lines:
                break
            continue
        if line.startswith("#") and not heading:
            heading = line.lstrip("#").strip()
            continue
        if line.startswith("#"):
            break
        paragraph_lines.append(line)
    summary = " ".join(paragraph_lines).strip()
    if heading and summary:
        return f'root README describes "{heading}" as: {summary}'
    if heading:
        return f'root README names the project "{heading}" but does not yet describe it further'
    if summary:
        return f"root README summary: {summary}"
    return "root README exists but did not yield a clear summary during bootstrap"


def detect_surface(target: Path) -> Detection:
    manifests_raw, source_raw, test_raw, doc_raw = walk_repository(target)
    manifests = relative_list(manifests_raw, target) or ["none detected from common manifest set"]
    source_locations = relative_list(source_raw, target) or ["not detected"]
    test_locations = relative_list(test_raw, target) or ["not detected"]
    doc_locations = relative_list(doc_raw, target) or ["not detected"]
    languages = detect_languages(manifests)
    commands = detect_commands(target)
    readme_signal = detect_readme_signal(target)

    observation = (
        "bootstrap produced a conservative repository inventory from static files only; runtime behavior is still unverified"
        if manifests != ["none detected from common manifest set"]
        else "bootstrap found very little machine-detectable structure; early human clarification is likely required"
    )
    inference = (
        "the repository likely has enough visible structure for an agent to start useful work after a brief verification pass"
        if source_locations != ["not detected"] or manifests != ["none detected from common manifest set"]
        else "the repository may be early-stage, non-standard, or intentionally lightweight"
    )

    return Detection(
        manifests=manifests,
        languages=languages,
        source_locations=source_locations,
        test_locations=test_locations,
        doc_locations=doc_locations,
        commands=commands,
        readme_signal=readme_signal,
        initial_observation=observation,
        initial_inference=inference,
    )


def render(template_text: str, replacements: Dict[str, str]) -> str:
    for key, value in replacements.items():
        template_text = template_text.replace(f"{{{{{key}}}}}", value)
    return template_text


def bulletize(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def assert_safe_output_path(target: Path, path: Path) -> None:
    target = target.resolve()
    try:
        path.relative_to(target)
    except ValueError as error:
        raise RuntimeError(f"refusing to write outside target: {path}") from error

    current = target
    for part in path.relative_to(target).parts[:-1]:
        current = current / part
        if current.exists():
            if current.is_symlink():
                raise RuntimeError(f"refusing to use symlinked directory: {current}")
            if not current.is_dir():
                raise RuntimeError(f"expected directory while preparing output path: {current}")

    if path.exists() or path.is_symlink():
        if path.is_symlink():
            raise RuntimeError(f"refusing to overwrite symlinked file: {path}")
        if not path.is_file():
            raise RuntimeError(f"refusing to overwrite non-regular file: {path}")


def write_file(target: Path, path: Path, content: str, force: bool) -> None:
    assert_safe_output_path(target, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not force:
            return
        existing = path.read_text(encoding="utf-8")
        if MANAGED_MARKER not in existing:
            return
    path.write_text(content, encoding="utf-8")


def cleanup_legacy_managed_files(target: Path) -> None:
    for legacy_relpath in LEGACY_MANAGED_FILES:
        legacy_path = target / legacy_relpath
        assert_safe_output_path(target, legacy_path)
        if not legacy_path.exists():
            continue
        existing = legacy_path.read_text(encoding="utf-8")
        if MANAGED_MARKER in existing:
            legacy_path.unlink()


def update_agents(target: Path, force: bool) -> None:
    template = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8").strip()
    managed_block = f"{ABES_START}\n{template}\n{ABES_END}\n"
    agents_path = target / "AGENTS.md"
    assert_safe_output_path(target, agents_path)

    if not agents_path.exists():
        agents_path.write_text(managed_block, encoding="utf-8")
        return

    existing = agents_path.read_text(encoding="utf-8")
    pattern = re.compile(rf"{re.escape(ABES_START)}.*?{re.escape(ABES_END)}\n?", re.DOTALL)
    if pattern.search(existing):
        agents_path.write_text(pattern.sub(managed_block, existing), encoding="utf-8")
        return

    if force:
        agents_path.write_text(managed_block + "\n" + existing.lstrip(), encoding="utf-8")
        return

    agents_path.write_text(managed_block + "\n" + existing, encoding="utf-8")


def bootstrap(target: Path, force: bool = False) -> None:
    detection = detect_surface(target)
    replacements = {
        "PROJECT_NAME": detect_repo_name(target),
        "TARGET_PATH": str(target.resolve()),
        "GENERATED_AT": datetime.now(timezone.utc).isoformat(),
        "MANIFEST_LIST": bulletize(detection.manifests),
        "LANGUAGE_LIST": bulletize(detection.languages),
        "SOURCE_LIST": bulletize(detection.source_locations),
        "TEST_LIST": bulletize(detection.test_locations),
        "DOC_LIST": bulletize(detection.doc_locations),
        "COMMAND_LIST": bulletize(detection.commands),
        "README_SIGNAL": detection.readme_signal,
        "INITIAL_OBSERVATION": detection.initial_observation,
        "INITIAL_INFERENCE": detection.initial_inference,
    }

    cleanup_legacy_managed_files(target)
    update_agents(target, force)

    files = {
        ".abes/project/brief.md": "templates/.abes/project/brief.md",
        ".abes/project/inventory.md": "templates/.abes/project/inventory.md",
        ".abes/state/current.md": "templates/.abes/state/current.md",
        ".abes/memory/decisions.md": "templates/.abes/memory/decisions.md",
        ".abes/memory/conventions.md": "templates/.abes/memory/conventions.md",
        ".abes/artifacts/README.md": "templates/.abes/artifacts/README.md",
    }

    for output, template_rel in files.items():
        template_text = (ROOT / template_rel).read_text(encoding="utf-8")
        content = render(template_text, replacements)
        write_file(target, target / output, content, force)


def main() -> None:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    try:
        if target.exists():
            if not target.is_dir():
                raise ValueError(f"Target path is not a directory: {target}")
        else:
            target.mkdir(parents=True)
        bootstrap(target, force=args.force)
    except (OSError, RuntimeError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print(f"ABES initialized in {target}")


if __name__ == "__main__":
    main()
