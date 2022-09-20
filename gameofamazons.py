"""
Jeu des amazons
ULB MATRICULE : 509461
Nom: Dua
Prenom: Harsh
"""


from sys import argv
from os.path import isfile

from gui import *
from guiGame import *



def check_file():
    if len(argv) < 2:
        print('Usage: python3 partie3.py <path>')
        return False
    if not isfile(argv[1]):
        print(f'{argv[1]} n\'est pas un chemin valide vers un fichier')
        return False
    return True

def main():
    app = QApplication(sys.argv)
    ex = Setup()
    app.exec_()
    if ex.start == True:
        loadedFile = copy.copy(ex.loadedFile[0])
        timeLimit = copy.copy(ex.sliderValue)
        playerHumanBoolTuple = copy.copy(ex.playersSettings)
        del ex
    try:
        ex = GameGUI(loadedFile, playerHumanBoolTuple, timeLimit)
    except NameError:
        pass

    else:
        app.exec_()
        del ex
        main()


if __name__ == '__main__':
    import random
    random.seed(0xCAFE)
    main()
