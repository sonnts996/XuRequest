import os


def current_dir():
    main = os.path.dirname(os.path.realpath(__file__))
    icon = os.path.join(main, "icons/it.svg")
    if os.path.exists(icon):
        return main
    else:
        project = os.path.dirname(os.path.dirname(main))
        return project
