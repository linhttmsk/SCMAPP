import streamlit.web.cli as stcli
import os, sys


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd() + r"\\app", path))
    return resolved_path


if __name__ == "__main__":
    # print(resolve_path("🏠_Home.py"))
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("Home.py"),
        "--global.developmentMode=false",
        "--client.showSidebarNavigation=False",
        "--client.showErrorDetails=False"
    ]
    sys.exit(stcli.main())