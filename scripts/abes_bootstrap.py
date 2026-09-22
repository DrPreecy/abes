#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List


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
COMMON_MANIFESTS = [
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
]


@dataclass
class Detection:
    manifests: List[str]
    languages: List[str]
    source_locations: List[str]
    test_locations: List[str]
    doc_locations: List[str]
    commands: List[str]
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


def find_files(target: Path, patterns: Iterable[str]) -> List[Path]:
    results: List[Path] = []
    for pattern in patterns:
        results.extend(target.glob(pattern))
    filtered: List[Path] = []
    for path in results:
        if not path.exists():
            continue
        if path == target:
            filtered.append(path)
            continue
        relative = path.relative_to(target)
        if relative.parts and relative.parts[0] == ".abes":
            continue
        filtered.append(path)
    return filtered


def named_directory_patterns(names: Iterable[str]) -> List[str]:
    patterns: List[str] = []
    for name in names:
        patterns.append(name)
        patterns.append(f"**/{name}")
    return patterns


def named_file_patterns(names: Iterable[str]) -> List[str]:
    patterns: List[str] = []
    for name in names:
        patterns.append(name)
        patterns.append(f"**/{name}")
    return patterns


def detect_manifests(target: Path) -> List[Path]:
    return find_files(target, named_file_patterns(COMMON_MANIFESTS))


def detect_commands(target: Path) -> List[str]:
    commands: List[str] = []

    package_json = target / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        scripts = data.get("scripts") or {}
        for key in ("test", "lint", "build", "dev", "start"):
            if key in scripts:
                commands.append(f"npm run {key}")

    pyproject = target / "pyproject.toml"
    if pyproject.exists():
        pyproject_text = pyproject.read_text(encoding="utf-8").lower()
        if "pytest" in pyproject_text:
            commands.append("python -m pytest")
        if "ruff" in pyproject_text:
            commands.append("ruff check .")
        if "pytest" not in pyproject_text and "ruff" not in pyproject_text:
            commands.append("inspect Python project test/lint commands before assuming any")

    makefile = target / "Makefile"
    if makefile.exists():
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


def detect_surface(target: Path) -> Detection:
    manifests = relative_list(detect_manifests(target), target) or ["none detected from common manifest set"]

    source_locations = relative_list(
        find_files(target, named_directory_patterns(["src", "app", "lib", "cmd", "server", "client"])),
        target,
    ) or ["not detected"]
    test_locations = relative_list(
        find_files(target, named_directory_patterns(["tests", "test", "__tests__", "spec"])),
        target,
    ) or ["not detected"]
    doc_locations = relative_list(
        find_files(target, [*named_directory_patterns(["docs"]), "README.md", "**/README.md"]),
        target,
    ) or ["not detected"]
    languages = detect_languages(manifests)
    commands = detect_commands(target)

    observation = (
        "bootstrap found a repository surface and created durable context files, but it has not validated runtime behavior"
        if manifests != ["none detected from common manifest set"]
        else "bootstrap found very little machine-detectable structure; human clarification is likely needed early"
    )
    inference = (
        "the project likely has enough visible structure for an agent to form an initial working model"
        if source_locations != ["not detected"] or manifests != ["none detected from common manifest set"]
        else "the project may be early-stage, non-standard, or documentation-light"
    )

    return Detection(
        manifests=manifests,
        languages=languages,
        source_locations=source_locations,
        test_locations=test_locations,
        doc_locations=doc_locations,
        commands=commands,
        initial_observation=observation,
        initial_inference=inference,
    )


def render(template_text: str, replacements: Dict[str, str]) -> str:
    for key, value in replacements.items():
        template_text = template_text.replace(f"{{{{{key}}}}}", value)
    return template_text


def bulletize(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_file(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not force:
            return
        existing = path.read_text(encoding="utf-8")
        if MANAGED_MARKER not in existing:
            return
    path.write_text(content, encoding="utf-8")


def update_agents(target: Path, force: bool) -> None:
    template = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8").strip()
    managed_block = f"{ABES_START}\n{template}\n{ABES_END}\n"
    agents_path = target / "AGENTS.md"

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
        "INITIAL_OBSERVATION": detection.initial_observation,
        "INITIAL_INFERENCE": detection.initial_inference,
    }

    update_agents(target, force)

    files = {
        ".abes/project/identity.md": "templates/.abes/project/identity.md",
        ".abes/project/architecture.md": "templates/.abes/project/architecture.md",
        ".abes/project/goals.md": "templates/.abes/project/goals.md",
        ".abes/state/current.md": "templates/.abes/state/current.md",
        ".abes/memory/decisions.md": "templates/.abes/memory/decisions.md",
        ".abes/memory/conventions.md": "templates/.abes/memory/conventions.md",
        ".abes/memory/opportunities.md": "templates/.abes/memory/opportunities.md",
        ".abes/artifacts/README.md": "templates/.abes/artifacts/README.md",
    }

    for output, template_rel in files.items():
        template_text = (ROOT / template_rel).read_text(encoding="utf-8")
        content = render(template_text, replacements)
        write_file(target / output, content, force)


def main() -> None:
    args = parse_args()
    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    bootstrap(target, force=args.force)
    print(f"ABES initialized in {target}")


if __name__ == "__main__":
    main()
