import os
import sys

if __name__ == "__main__":

    GUI_FRONTEND_RUNNING = os.getenv("MOSAIC_STREAMLIT_GUI_RUNNING", "false") == "true"
    launchdir = os.path.dirname(sys.argv[0])

    if launchdir == "":
        launchdir = ".."

    # streamlit can take a while to import
    from streamlit import cli as stcli

    sys.argv = ["streamlit", "run", f"{launchdir}/src/app.py", "--global.developmentMode=false"]
    if GUI_FRONTEND_RUNNING:
        sys.argv += [
            "--server.port=10000",
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
