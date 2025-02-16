import os

import nox

os.environ.update(PDM_IGNORE_SAVED_PYTHON="1", PDM_USE_VENV="1")


def _install(session: nox.Session, *, groups: list[str] | None = None) -> None:
    if groups is None:
        groups = []

    session.run("pdm", "install", *(f"--group={group}" for group in groups), external=True)


@nox.session(python=("3.12", "3.13"))
def test(session: nox.Session) -> None:
    _install(session, groups=["test"])
    session.run("pytest", "tests/")


@nox.session(python=("3.13",))
def mypy(session: nox.Session) -> None:
    _install(session, groups=["mypy"])
    session.run("mypy", ".")
