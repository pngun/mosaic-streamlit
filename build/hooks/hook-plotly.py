from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

datas = collect_data_files(
    'plotly',
    include_py_files=True,
    includes=['**/*.py', 'package_data/**/*.*']
)
_, binaries, hiddenimports = collect_all('plotly')
hiddenimports += collect_submodules('plotly.graph_objs')
