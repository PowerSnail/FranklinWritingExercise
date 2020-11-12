from subprocess import run


def build_png():
    run("convert res/franklin-exercise.svg res/franklin-exercise.png", shell=True)

def build_qrc():
    run("pyrcc5 res/resources.qrc -o franklin_writing_exercise/resources.py", shell=True)


if __name__ == "__main__":
    build_png()
    build_qrc()