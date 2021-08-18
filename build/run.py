import os
import socket
import sys
from contextlib import closing


def find_a_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


if __name__ == "__main__":

    GUI_FRONTEND_RUNNING = os.getenv("MOSAIC_STREAMLIT_GUI_RUNNING", "false") == "true"
    launchdir = os.path.dirname(sys.argv[0])

    if launchdir == "":
        launchdir = ".."

    # streamlit can take a while to import
    from streamlit import cli as stcli

    port = find_a_port()

    sys.argv = ["streamlit", "run", f"{launchdir}/insights/app.py", "--global.developmentMode=false"]
    if GUI_FRONTEND_RUNNING:
        sys.argv += [
            f"--server.port={port}",
            "--server.headless=true",
            "--server.fileWatcherType=none",
            "--server.maxUploadSize=10240",
            "--theme.primaryColor=#54B4D4",
            "--theme.backgroundColor=#FFFFFF",
            "--theme.secondaryBackgroundColor=#F0F2F6",
            "--theme.textColor=#262730",
            "--theme.font=sans serif",
        ]

    sys.exit(stcli.main())
