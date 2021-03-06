from pathlib import Path

import nox

PROGRAM_DIR = Path(__file__).parent / "fuzzy"


def parse_requirements(path):
    with open(path, mode="r", encoding="utf-8") as f:
        deps = (d.strip() for d in f.readlines())
        return [d for d in deps if not d.startswith(("#", "-r"))]


DEPS = {
    name: install
    for name, install in (
        r.split("~=") for r in parse_requirements("./requirements-dev.txt")
    )
}


@nox.session(reuse_venv=True)
def check_formatting(session):
    session.install(f"black~={DEPS['black']}")
    session.run("black", ".", "--check")


@nox.session(reuse_venv=True)
def check_imports(session):
    session.install(f"flake8~={DEPS['flake8']}", f"isort~={DEPS['isort']}")
    # flake8 doesn't use the gitignore so we have to be explicit.
    session.run(
        "flake8",
        "nusex",
        "tests",
        "--select",
        "F4",
        "--extend-ignore",
        "E,F,W",
        "--extend-exclude",
        "__init__.py",
    )
    session.run("isort", ".", "-cq", "--profile", "black")


@nox.session(reuse_venv=True)
def check_line_lengths(session):
    session.install(f"len8~={DEPS['len8']}")
    session.run("len8", "nusex")
    session.run("len8", "tests")


@nox.session(reuse_venv=True)
def check_licensing(session):
    missing = []

    for p in PROGRAM_DIR.rglob("*.py"):
        with open(p) as f:
            if not f.read().startswith("# Copyright (c)"):
                missing.append(p)

    if missing:
        session.error(
            f"\n{len(missing):,} file(s) are missing their licenses:\n"
            + "\n".join(f" - {file}" for file in missing)
        )
