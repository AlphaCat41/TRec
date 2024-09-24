from cx_Freeze import setup, Executable

# Define the file to be converted and the additional options
setup(
    name="TRec",
    version="1.0.0",
    description="TRec",
    executables=[Executable("main.py")],
)
