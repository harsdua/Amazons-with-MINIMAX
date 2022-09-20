
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, QAction,QSlider, QComboBox,QLabel, QPushButton, QGraphicsScene, QGraphicsItem, QGraphicsView, QFileDialog)

from PyQt5.QtCore import Qt,QRect, QSize, QDir, QTimer

from amazons import read_file

class Setup(QWidget):
    """
    Classe qui lance le Setup partie de GUI
    """
    def __init__(self):
        """
        initialization de la fenetre
        """
        super().__init__()
        self.title = 'SETUP - Jeu des amazons '
        self.width = 700
        self.height = 400
        self.initUI()
        self.show()



    def initUI(self):
        """
        Methode qui initialize le UI
        """
        self.left = 100
        self.top = 50
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.initPlayerSelection()
        self.initLoadFile()
        self.startButton()
        self.initSlider()

    def initPlayerSelection(self):
        """
        ComboBox pour selectioner Joueur 1 et Joueur 2
        :return:
        """
        ## Init player 1
        self.player1CB = QComboBox(self)
        self.player1CB.move(142, 50)
        self.player1CB.addItem("Humain")
        self.player1CB.addItem("IA")
        self.player1Label = QLabel("Joueur 1:", self)
        self.player1Label.setGeometry(QRect(64, 35, 50, 50))

        ## Init player 2
        self.player2CB = QComboBox(self)
        self.player2CB.move(142, 100)
        self.player2CB.addItem("Humain")
        self.player2CB.addItem("IA")
        self.player2Label = QLabel("Joueur 2:", self)
        self.player2Label.setGeometry(QRect(64, 85, 50, 50))

    def initSlider(self):
        """
        Initialization de le slider pour le delai de l'IA
        :return:
        """
        self.slider = QSlider(Qt.Horizontal,self)
        self.slider.setGeometry(QRect(200, 145, 400, 25))
        self.slider.setTickInterval(2)
        self.slider.setTickPosition(2)
        self.slider.setMinimum(2)
        self.slider.valueChanged.connect(self.changedSliderValue)
        self.sliderValue = 2
        #self.slider.valueChanged.connect(None)
        self.sliderLabel = QLabel("Délai IA", self)
        self.sliderLabel.setGeometry(QRect(64, 135, 60, 50))
        self.min = QLabel("2s", self)
        self.min.setGeometry(QRect(185, 155, 60, 50))
        self.max = QLabel("100s", self)
        self.max.setGeometry(QRect(600, 155, 60, 50))

    def changedSliderValue(self):
        """
        connection pour le slider
        """
        self.sliderValue = self.slider.value()


    def startButton(self):
        """
        initialization de le QPushbutton qui va demarrer le jeu
        :return:
        """
        self.startButton = QPushButton("Démarrer",self)
        self.startButton.setGeometry(QRect(64,250,140,140))
        self.startButton.setDisabled(True)
        self.startButton.clicked.connect(self.start)

    def initLoadFile(self):
        """
        initialization de le QPushbutton qui va permettre choisir le fichier .txt qui contient le plateau
        :return:
        """
        self.loadedFile = None, False
        self.browseButton = QPushButton("Charger Plateau", self)
        self.browseButton.move(64, 200)
        self.fileLabel = QLabel("Aucun plateau chargé, veuillez charger un plateau", self)
        self.fileLabel.setGeometry(QRect(213, 185, 1000, 50))
        self.browseButton.clicked.connect(self.getTextFile)

    def getTextFile(self):
        """
        Methode pour lire le fichier
        :return:
        """
        openTextDialog = QFileDialog()
        openTextDialog.setFileMode(QFileDialog.AnyFile)
        openTextDialog.setFilter(QDir.Files)
        if openTextDialog.exec_():
            fileName = openTextDialog.selectedFiles()

            if fileName[0].endswith(".txt"):    #Si il est pas un .txt fichier
                try:
                    read_file(fileName[0])
                    self.loadedFile = (fileName[0], True)
                except InvalidFormatError:                      #Si il contient pas le plateau dans le bon format
                    self.loadedFile = (fileName[0], False)

            else:
                self.loadedFile = (fileName[0], False)
        self.updateWithLoadFile()

    def updateWithLoadFile(self):
        """
        Il va faire un mis à jour pour le text , et va activer le QPushbutton pour demarrer le jeu si le fichier est bon
        :return:
        """
        if self.loadedFile[1]:
            self.fileLabel.setText(self.loadedFile[0] + "  chargé")
            self.startButton.setDisabled(False)
        else:
            try:
                self.fileLabel.setText("Le fichier sélectionné n'est pas bon. Il ne contient pas les données du plateau dans un bon format")
            except TypeError:
                pass





    def start(self):
        """
        Fonctionne pour faire des attributes qui va aller vers le GameGUI et fermer le setup
        :return:
        """
        self.start = True
        if self.player1CB.currentText() == "IA":
            P1 = False
        else:
            P1 = True
        if self.player2CB.currentText() == "IA":
            P2 = False
        else:
            P2 = True


        self.playersSettings = (P1,P2)
        self.close()









