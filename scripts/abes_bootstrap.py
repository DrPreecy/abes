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
    return sorted(str(path.relative_to(target)) for path in paths)


def find_files(target: Path, patterns: Iterable[str]) -> List[Path]:
    results: List[Path] = []
    for pattern in patterns:
        results.extend(target.glob(pattern))
    return [path for path in results if path.exists()]


def detect_commands(target: Path) -> List[str]:
    commands: List[str] = []

    package_json = target / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
        except json.JSONDecodeError:
            data = {}
        scripts = data.get("scripts") or {}
        for key in ("test", "lint", "build", "dev", "start"):
            if key in scripts:
                commands.append(f"npm run {key}")

    pyproject = target / "pyproject.toml"
    if pyproject.exists():
        commands.extend(["python -m pytest", "python -m unittest", "ruff check ."])

    if (target / "Makefile").exists():
        commands.extend(["make test", "make lint", "make build"])

    if (target / "go.mod").exists():
        commands.extend(["go test ./...", "go vet ./..."])

    if (target / "Cargo.toml").exists():
        commands.extend(["cargo test", "cargo clippy"])

    unique: List[str] = []
    for command in commands:
        if command not in unique:
            unique.append(command)
    return unique or ["inspect repository-specific build/test commands before assuming any"]


def detect_languages(target: Path) -> List[str]:
    manifest_languages = {
        "package.json": "JavaScript/TypeScript",
        "pyproject.toml": "Python",
        "requirements.txt": "Python",
        "go.mod": "Go",
        "Cargo.toml": "Rust",
        "pom.xml": "Java",
        "build.gradle": "Java/Kotlin",
        "Gemfile": "Ruby",
    }
    detected = []
    for manifest, label in manifest_languages.items():
        if (target / manifest).exists() and label not in detected:
            detected.append(label)
    return detected or ["undetermined from common manifests"]


def detect_surface(target: Path) -> Detection:
    manifests = relative_list(
        find_files(
            target,
            [
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
            ],
        ),
        target,
    ) or ["none detected from common manifest set"]

    source_locations = relative_list(find_files(target, ["src", "app", "lib", "cmd", "server", "client"]), target) or ["not detected"]
    test_locations = relative_list(find_files(target, ["tests", "test", "__tests__", "spec"]), target) or ["not detected"]
    doc_locations = relative_list(find_files(target, ["docs", "README.md"]), target) or ["not detected"]
    languages = detect_languages(target)
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
    if path.exists() and not force:
        return
    path.write_text(content)


def update_agents(target: Path, force: bool) -> None:
    template = (TEMPLATES / "AGENTS.md").read_text().strip()
    managed_block = f"{ABES_START}\n{template}\n{ABES_END}\n"
    agents_path = target / "AGENTS.md"

    if not agents_path.exists():
        agents_path.write_text(managed_block)
        return

    existing = agents_path.read_text()
    pattern = re.compile(rf"{re.escape(ABES_START)}.*?{re.escape(ABES_END)}\n?", re.DOTALL)
    if pattern.search(existing):
        agents_path.write_text(pattern.sub(managed_block, existing))
        return

    if force:
        agents_path.write_text(managed_block + "\n" + existing.lstrip())
        return

    agents_path.write_text(managed_block + "\n" + existing)


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
        template_text = (ROOT / template_rel).read_text()
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
