from cx_Freeze import setup, Executable

base = None

executables = [Executable("main.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages': packages,
    },
}
setup(
    name="Reetm",
    options=options,
    version="1.0",
    description='Reetm is a game',
    executables=executables
)
