import json
import os
import shutil
from typing import Any, Callable, Dict, List


def _get_inner_vscode_cmd() -> List[str]:
    return [
        "code-server",
        "--auth",
        "none",
        "--disable-telemetry",
    ]


def _get_inner_openvscode_cmd() -> List[str]:
    return [
        "openvscode-server",
        "--without-connection-token",
        "--telemetry-level",
        "off",
    ]


_CODE_EXECUTABLE_INNER_CMD_MAP: Dict[str, Callable] = {
    "code-server": _get_inner_vscode_cmd,
    "openvscode-server": _get_inner_openvscode_cmd,
}


def _get_cmd_factory(executable: str) -> Callable:
    if executable not in _CODE_EXECUTABLE_INNER_CMD_MAP:
        raise KeyError(
            f"'{executable}' is not one of {_CODE_EXECUTABLE_INNER_CMD_MAP.keys()}."
        )

    get_inner_cmd = _CODE_EXECUTABLE_INNER_CMD_MAP[executable]

    def _get_cmd(port: int) -> List[str]:
        if not shutil.which(executable):
            raise FileNotFoundError(f"Can not find {executable} in PATH")

        # Start vscode in CODE_WORKINGDIR env variable if set
        # If not, start in 'current directory', which is $REPO_DIR in mybinder
        # but /home/jovyan (or equivalent) in JupyterHubs
        working_dir = os.getenv("CODE_WORKINGDIR", ".")
        working_dir = os.path.join(working_dir, "python-ecology-lesson")
        try:
            os.mkdir(working_dir)
        except FileExistsError:
            pass

        # Add .vscode settings file to working directory
        vscode_dir = os.path.join(working_dir, ".vscode")
        try:
            os.mkdir(vscode_dir)
        except FileExistsError:
            pass
        with open(os.path.join(vscode_dir, "settings.json"), "w") as f:
            json.dump(
                {
                    "editor.rulers": [88],
                    "notebook.lineNumbers": "on",
                    "workbench.colorTheme": "Default Dark Modern",
                },
                f,
                indent=4,
            )

        # Create default notebook
        with open(os.path.join(working_dir, "test.ipynb"), "w") as f:
            json.dump(
                {
                    "cells": [
                        {
                            "cell_type": "markdown",
                            "id": "cf7207e5",
                            "metadata": {},
                            "source": [
                                "# Test notebook\n",
                                "\n",
                                "This notebook tests that the environment required for the lesson is configured properly. It also provides the URLs required to access the files needed for the lesson.",
                            ],
                        },
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "id": "cf7207e5",
                            "metadata": {},
                            "outputs": [],
                            "source": ["import pandas as pd\n", "import plotly"],
                        },
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "id": "e5089d99",
                            "metadata": {},
                            "outputs": [],
                            "source": [
                                "# URLs for data used in the lesson\n",
                                'surveys = pd.read_csv("https://figshare.com/ndownloader/files/10717177")\n',
                                'species = pd.read_csv("https://figshare.com/ndownloader/files/3299483")\n',
                                'plots = pd.read_csv("https://figshare.com/ndownloader/files/3299474")',
                            ],
                        },
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "id": "6d409e01",
                            "metadata": {},
                            "outputs": [],
                            "source": [],
                        },
                    ],
                    "metadata": {
                        "language_info": {
                            "name": "python",
                        },
                    },
                    "nbformat": 4,
                    "nbformat_minor": 5,
                },
                f,
                indent=4,
            )

        extensions_dir = os.getenv("CODE_EXTENSIONSDIR", None)

        cmd = get_inner_cmd()

        cmd.append("--port=" + str(port))

        if extensions_dir:
            cmd += ["--extensions-dir", extensions_dir]

        cmd.append(working_dir)
        return cmd

    return _get_cmd


def setup_vscode() -> Dict[str, Any]:
    executable = os.environ.get("CODE_EXECUTABLE", "code-server")
    icon = "code-server.svg" if executable == "code-server" else "vscode.svg"
    return {
        "command": _get_cmd_factory(executable),
        "timeout": 300,
        "new_browser_tab": True,
        "launcher_entry": {
            "title": "VS Code",
            "icon_path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "icons", icon
            ),
        },
    }
