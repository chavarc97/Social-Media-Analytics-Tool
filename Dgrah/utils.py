import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_dict(d):
    for key in d.keys():
        print(key, '--', d[key])