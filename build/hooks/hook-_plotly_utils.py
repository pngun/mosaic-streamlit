from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('_plotly_utils')
