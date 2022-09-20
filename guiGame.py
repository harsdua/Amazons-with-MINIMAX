import sys, copy, time
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, QAction,QSlider, QComboBox,QLabel, QPushButton, QGraphicsScene, QGraphicsItem, QGraphicsView, QFileDialog)
from PyQt5.QtGui import QFont,QPainter, QPen, QBrush, QPainterPath, QColor
from PyQt5.QtCore import Qt,QRect, QSize, QDir, QTimer

from amazons import Amazons
from pos2d import Pos2D
from action import Action
from exceptions import *

class GameGUI(QWidget):
    """
    Classe qui contient tout les element du jeu des amazons
    """
    def __init__(self,loadedFile, playerHumanBoolTuple,timeLimit = None):
        """

        :param loadedFile:str (le path vers le fichier qui contient le plateau)
        :param playerHumanBoolTuple:  tuple des bools qui dis si P1 et P2 est humain respectivement
        :param timeLimit: int de le delai pour l'IA
        """
        super().__init__()
        self.initBackendConnection(loadedFile,playerHumanBoolTuple, timeLimit)
        self.initContainers()
        self.initWindow()
        self.initBoard()
        self.show()
        QApplication.processEvents()
        if self.needBackEndReciever:
            self.backEndReciever()


    def initBackendConnection(self,loadedFile,playerHumanBoolTuple,timeLimit):
        """
        Va connecter avec le classe Amazons, et tout les autres classes de le jeu. Il va retriever tout les informations nessecaire pour créer le GUI
        :param loadedFile: str (le path vers le fichier qui contient le plateau)
        :param playerHumanBoolTuple: tuple des bools qui dis si P1 et P2 est humain respectivement
        :param timeLimit: int de le delai pour l'IA
        :return:
        """

        self.backEnd = Amazons(loadedFile, playerHumanBoolTuple[0], playerHumanBoolTuple[1],timeLimit)
        self.gridSize = int(self.backEnd.board.startingSetup[0])
        self.blackQueens = self.tuplesFromPos2Ds(self.backEnd.board.startingSetup[1])
        self.whiteQueens = self.tuplesFromPos2Ds(self.backEnd.board.startingSetup[2])
        self.startingArrows = self.tuplesFromPos2Ds(self.backEnd.board.startingSetup[3])
        self.timeLimit = timeLimit

        self.playerHumanBoolTuple = playerHumanBoolTuple
        ## Si p1 et p2 est humain
        if self.playerHumanBoolTuple == (True,True):
            self.humanIsPlaying = True
            self.needBackEndReciever = False
        else:
            self.needBackEndReciever = True





    def initContainers(self):
        """
        Initialization de tout les containers qui va tracer des choses dans le GUI
        :return:
        """
        self.whiteQueenPointers = dict()
        self.blackQueenPointers = dict()
        self.arrowPointers = dict()
        self.squarePointers = dict()
        self.eventsDone = 0
        self.selectedSquares = []

    def initWindow(self):
        """
        Initialization de le fenetre
        :return:
        """
        self.title = 'Jeu des amazons '
        self.width = 1000
        self.height = 800
        self.setGeometry(100,100,self.width,self.height)
        self.setWindowTitle(self.title)



    def initBoard(self):
        """
        Initialization de le plateau
        :return:
        """
        self.scene = QGraphicsScene()
        self.initColors()
        self.initGraphics()
        self.fillBoard()

    def initColors(self):
        """
        Initialization de les brushes, pens et couleurs nessecaire
        :return:
        """


        self.whiteBrush = QBrush(Qt.white)
        self.blackBrush = QBrush(Qt.black)
        self.primaryColor =  QColor(0, 75, 115, 153)        #Pale Blue
        self.secondaryColor =  QColor(245,245,225)  #Off White
        self.primaryColorBrush  = QBrush(self.primaryColor)
        self.secondaryColorBrush = QBrush(self.secondaryColor)
        self.primarySelectionBrush = QBrush(Qt.darkCyan,Qt.Dense4Pattern)
        self.secondarySelectionBrush = QBrush(Qt.gray,Qt.Dense4Pattern)
        self.endTextBrush = QBrush(Qt.red)


    def initGraphics(self):
        """
        Initialization de le graphics view
        :return:
        """
        graphicsView = QGraphicsView(self.scene, self)
        graphicsView.setGeometry(0,0,800,800)
        graphicsView.setSceneRect(0,0,750,750)
        self.zerozero = (30,-24)
        self.squareSize = (742/self.gridSize)
        self.scene.addRect(30, -24, 742, 742, QPen(), self.whiteBrush)



    def tuplesFromPos2Ds(self,listOfPos2D):
        """
        translation  de les tuples dans les lists avec des Pos2Ds
        Utile pour transformer les pos_noirs/pos_reines/pos_arrow  au debut pour les Pos2Ds pour le jeu
        :param listOfPos2D: list
        :return: (x,y) tuple de le cas de le plateau
        """
        translated = []
        for coords in listOfPos2D:
            translated.append((coords.x,coords.y))
        return translated

    def Pos2DToPixelCoord(self,x,y):
        """
        Translation de (x,y) cas de le plateau à des (x,y) pixel coordonnées
        :param x: float/int
        :param y: float/int
        :return: (int,int)
        """
        return self.zerozero[0] + (self.squareSize * x), self.zerozero[1] + (self.squareSize * (self.gridSize - 1 - y))

    def PixelToPos2D(self,x,y):
        """
        Inverse de self.Pos2DToPixelCoord()
        :param x: float/int
        :param y: float/int
        :return: (int,int)
        """
        x0,y0 = 55,742
        return int((x-x0)//self.squareSize),int(-(y-y0)//self.squareSize)

    def pos2DToLetterNumber(self,coup):
        """
        Traduit la position ligne,colonne en format string
        Args:
            coup (int,int): Position dans la matrice
            taille (int): Taille du plateau

        Returns:
            str: Position du plateau en format string
        """
        taille = self.gridSize
        lettres = [chr(x + ord('a')) for x in range(taille)]
        nombres = [str(x) for x in range(1, taille + 1)]
        return ''.join([lettres[coup[0]], nombres[coup[1]]])

    def isPrimaryColored(self,x,y):
        """
        Va voir si un cas dans le plateau est primaryColored ou secondaryColored
        :param x:
        :param y:
        :return: bool
        """
        if x%2:
            if y % 2:
                return True
            else:
                return False
        else:
            if y%2:
                return False
            else:
                return True


    def drawLetters(self,x):
        """
        Methode pour designer les Alphabets sous le plateau dans QGraphicsScene
        :param x: int, le X de le cas sur le lettre
        :return:
        """
        xcoord, ycoord = self.Pos2DToPixelCoord(x, 0)
        letter = self.pos2DToLetterNumber((x,0))[0]
        paintLetter = QPainterPath()
        paintLetter.addText(xcoord+self.squareSize/2.3,ycoord+self.squareSize+35,QFont("Comic Sans", int(self.squareSize * 0.18)), letter)
        letterPath = self.scene.addPath(paintLetter)
        letterPath.setPen(QPen())
        letterPath.setBrush(self.blackBrush)

    def drawNumbers(self,y):
        """
        Methode pour designer les nombres à gauche de le plateau dans QGraphicsScene
        :param y: int, le y de le cas à droit de le nombre
        :return:
        """
        xcoord, ycoord,   = self.Pos2DToPixelCoord(0, y-1)
        letter = self.pos2DToLetterNumber((0,y))[1]
        paintLetter = QPainterPath()
        paintLetter.addText(xcoord-35, ycoord-self.squareSize/2.3,QFont("Comic Sans", int(self.squareSize * 0.18)), letter)
        letterPath = self.scene.addPath(paintLetter)
        letterPath.setPen(QPen())
        letterPath.setBrush(self.blackBrush)


    def drawSquare(self,x,y,primaryColorBool):
        """
        Methode pour designer un carré(case) de le plateau à x,y
        :param x: int, coordonnée x de le plateau
        :param y: int, coordonnée y de le plateau
        :param primaryColorBool: bool, si cest primaryColored
        :return:
        """
        if primaryColorBool == True:
            fillColor = self.primaryColorBrush
        else:
            fillColor = self.secondaryColorBrush
        xcoord , ycoord= self.Pos2DToPixelCoord(x,y)
        squarePath = self.scene.addRect(xcoord,ycoord,self.squareSize,self.squareSize,QPen(),fillColor)
        self.squarePointers[(x,y)]  = squarePath, primaryColorBool #Pour trouver lobjet qu'on viens de crée dans le cas on veut le modifier

    def drawQueen(self, x, y, isWhite):
        """
        Methode pour designer une reine à x,y
        :param x: int, coordonnée x de le plateau
        :param y: int, coordonnée y de le plateau
        :param isWhite: bool, si cest blanche
        :return:
        """
        xcoord, ycoord = self.Pos2DToPixelCoord(x,y)
        painterQueen = QPainterPath()
        painterQueen.addText(xcoord+0.05*self.squareSize,ycoord+0.8*self.squareSize,QFont("Sanserif", int(self.squareSize * 0.66)), "♛")
        queenPath = self.scene.addPath(painterQueen)
        queenPath.setPen(QPen())
        if isWhite:
            queenPath.setBrush(self.whiteBrush)
            self.whiteQueenPointers[(x, y)] = queenPath #Pour trouver lobjet qu'on viens de crée dans le cas on veut le modifier
        else:
            queenPath.setBrush(self.blackBrush)
            self.blackQueenPointers[(x, y)] = queenPath #Pour trouver lobjet qu'on viens de crée dans le cas on veut le modifier

    def drawArrow(self,x,y):
        """
         Methode pour designer une fleche à x,y
        :param x: int, coordonnée x de le plateau
        :param y: int, coordonnée y de le plateau
        :return:
        """
        xcoord, ycoord = self.Pos2DToPixelCoord(x,y)
        painterArrow = QPainterPath()
        painterArrow.addText(xcoord+0.25*self.squareSize,ycoord+0.82*self.squareSize,QFont("Sanserif", int(self.squareSize * 0.66)), "X")
        arrowPath = self.scene.addPath(painterArrow)
        arrowPath.setPen(QPen())
        arrowPath.setBrush(self.blackBrush)
        self.arrowPointers[(x,y)] = arrowPath  #Pour trouver lobjet qu'on viens de crée dans le cas on veut le modifier


    def removeQueen(self,x,y):
        """
        Pour supprimer un reine designé à x,y
        :param x: int, coordonnée x de le plateau
        :param y:  int, coordonnée y de le plateau
        :return:
        """
        queenPath = self.blackQueenPointers.get((x,y))
        if queenPath ==  None:
            queenPath=  self.whiteQueenPointers.get((x,y))
        if queenPath:
            self.whiteQueenPointers.pop((x,y),None)
            self.blackQueenPointers.pop((x,y),None)
            self.scene.removeItem(queenPath)

    def removeArrow(self,x,y):
        """
        Pour supprimer un reine designé à x,y
        :param x: int, coordonnée x de le plateau
        :param y:  int, coordonnée y de le plateau
        :return:
        """
        arrowpath = self.arrowPointers.get((x,y))
        if arrowpath:
            self.scene.removeItem(arrowpath)
            self.arrowPointers.pop((x,y))

    def performMove(self,startPos,endPos,arrowPos):
        """
        Fonctionne pour bouger le reine et tirer une fleche
        :param startPos: tuple de (x,y)
        :param endPos: tuple de (x,y)
        :param arrowPos: tuple de (x,y)
        :return:
        """
        self.performMoveDone = False
        self.removeQueen(startPos[0],startPos[1])
        self.drawQueen(endPos[0],endPos[1], self.isWhiteTurn)
        self.drawArrow(arrowPos[0],arrowPos[1])
        self.performMoveDone = True                             #Utilile pour debugging
        self.update()



    def fillBoard(self):
        """
        Designe le plateau avec tout les elements
        :return:
        """
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                self.drawSquare(x, y, self.isPrimaryColored(x,y))
        for i in self.blackQueens:
            self.drawQueen(i[0],i[1],False)
        for i in self.whiteQueens:
            self.drawQueen(i[0],i[1],True)
        for i in self.startingArrows:
            self.drawArrow(i[0],i[1])
        for i in range(self.gridSize):
            self.drawLetters(i)
        for i in range(self.gridSize):
            self.drawNumbers(i)



    def selectSquare(self,squarePath):
        """
        Fais un effet pour donner limpression que lutilisateur à choisi le carrée
        :param squarePath: objet path de le carré
        :return:
        """
        if squarePath[1]:
            squarePath[0].setBrush(self.primarySelectionBrush)
        else:
            squarePath[0].setBrush(self.secondarySelectionBrush)
        self.selectedSquares.append(squarePath)

    def deselectAllSquares(self):
        """
        Fais un effet pour donner limpression que lutilisateur à deselectionée tout les carrées qu'il à choisi auparavant
        :return:
        """
        for squarePath in self.selectedSquares:
            if squarePath[1]:
                squarePath[0].setBrush(self.primaryColorBrush)
            else:
                squarePath[0].setBrush(self.secondaryColorBrush)
        if self.eventsDone==1:
            del self.selection1
        elif self.eventsDone==2:
            try:
                del self.selection1

            except AttributeError:
                pass
            try:
                del self.selection2
            except AttributeError:
                pass
        self.eventsDone = 0

    def mousePressEvent(self,event):
        """
        Methode qui gere jouer le jeu
        :param event:
        :return:
        """
        if not self.humanIsPlaying:
            return

        if event.button()== Qt.LeftButton:
                self.lastPoint = event.pos()
                pixX = self.lastPoint.x()
                pixY = self.lastPoint.y()
                if 54 < pixX < 800 and 0 < pixY < 743:
                    if self.eventsDone == 0:            #Si cest le premier carré il selectione
                        self.selectionEvent1(pixX,pixY)
                    elif self.eventsDone == 1:          #Si cest le deuxieme carré il selectione
                        self.selectionEvent2(pixX,pixY)
                    elif self.eventsDone == 2:          #Si cest le troiseme carré il selectione
                        self.validstep3 = self.selectionEvent3(pixX,pixY)



    def selectionEvent1(self,pixX,pixY):
        """
        pour gerer le premier selection d'un carrée avec une reine. Il va sousligner le carré si cest valide
        :param pixX:  float pixel X de le souris où il a cliqué
        :param pixY: float pixel Y de le souris où il a cliqué
        :return:
        """
        casx, casy = self.PixelToPos2D(pixX, pixY)
        if self.backEnd.current_player_idx == 0:
            queenPath = self.whiteQueenPointers.get((casx, casy))
            self.isWhiteTurn = True
        else:
            queenPath = self.blackQueenPointers.get((casx, casy))
            self.isWhiteTurn = False

        if queenPath:
            self.selection1 = casx, casy
            squarePath = self.squarePointers[(casx, casy)]
            self.selectSquare(squarePath)
            self.eventsDone += 1

    def selectionEvent2(self,pixX,pixY):
        """
        pour gerer le deuxieme selection d'un carrée vide. Il va sousligner le carré si cest valide
        :param pixX:  float pixel X de le souris où il a cliqué
        :param pixY: float pixel Y de le souris où il a cliqué
        :return:
        """
        cas2x, cas2y = self.PixelToPos2D(pixX, pixY)
        try:
            validStep2 = self.backEnd.board.is_accessible(Pos2D(self.selection1[1], self.selection1[0]), Pos2D(cas2y, cas2x))
        except AttributeError:
            validStep2 = False
        if validStep2 and self.backEnd.board.at(Pos2D(cas2y,cas2x)) != 3:
            squarePath = self.squarePointers[(cas2x,cas2y)]
            self.selectSquare(squarePath)
            self.selection2 = cas2x,cas2y
            self.eventsDone += 1
        else:
            self.deselectAllSquares()


    def selectionEvent3(self,pixX,pixY):
        """
        pour gerer le troiseme selection d'un carrée vide. Il va sousligner le carré si cest valide
        :param pixX:  float pixel X de le souris où il a cliqué
        :param pixY: float pixel Y de le souris où il a cliqué
        :return:
        """
        cas3x,cas3y = self.PixelToPos2D(pixX,pixY)
        try:
            validStep3 = self.validateCoup(self.selection1,self.selection2,(cas3x,cas3y))
        except AttributeError:
            validStep3 = False,None
        if validStep3[0]:
            selection3 = cas3x,cas3y
            self.performMove(self.selection1,self.selection2,selection3)
            self.deselectAllSquares()
            QApplication.processEvents()
            self.backEndTransmitor(validStep3[1])
            if self.needBackEndReciever:
                self.backEndReciever()
            return validStep3
        else:
            self.deselectAllSquares()
            return None



    def validateCoup(self,startPos,endPos,arrowPos):
        """
        Si le coup est valide
        :param startPos: (x,y) de le plateau
        :param endPos: (x,y) de le plateau
        :param arrowPos: (x,y) de le plateau
        :return:
        """
        coup = self.pos2DToLetterNumber(startPos)+">"+self.pos2DToLetterNumber(endPos)+">"+self.pos2DToLetterNumber(arrowPos)
        action = None
        valid = False
        if self.isWhiteTurn:
            playerID = 0
        else:
            playerID = 1
        try:
            action = Action(*coup.split('>'),playerID)
            valid = self.backEnd.board.is_valid_action(action)
        except InvalidActionError:
            pass
        return valid, action

    def backEndTransmitor(self,action):
        """
        Pour envoyer le coup d'utilisateur
        :param action: Action objet
        :return:
        """
        self.backEnd.play(action)
        if self.backEnd.is_over():
            self.backEnd.show_winner()
            self.endGame()

    def backEndReciever(self):
        """
        Pour recevoir le coup de l'ia
        :param action: Action Objet
        :return:
        """
        if self.playerHumanBoolTuple ==(True, False):
            if self.backEnd.current_player_idx == 0:
                self.isWhiteTurn = True
                self.humanIsPlaying = True
            if self.backEnd.current_player_idx == 1:
                self.isWhiteTurn= False
                self.connectAI()
        elif self.playerHumanBoolTuple == (False, True):
            if self.backEnd.current_player_idx == 0:
                self.isWhiteTurn = True
                self.connectAI()
        elif self.playerHumanBoolTuple == (False, False):
            self.connectDoubleAI()

    def connectAI(self):
        """
        Pour connecter l'IA
        :return:
        """
        startTimeAI = time.time()
        self.humanIsPlaying = False
        self.backEnd.play()
        actionAI = self.backEnd.minimaxPlay
        QApplication.processEvents()
        timeDiff = time.time() - startTimeAI
        timeRemaining = self.timeLimit - timeDiff
        if 0<timeRemaining <3 :
            time.sleep(timeRemaining+timeRemaining*0.33)
        elif timeRemaining> 0:
            time.sleep(timeRemaining*0.7)
        self.performMove((actionAI.old_pos.x, actionAI.old_pos.y),(actionAI.new_pos.x, actionAI.new_pos.y),(actionAI.arrow_pos.x, actionAI.arrow_pos.y))
        self.humanIsPlaying = True
        if self.backEnd.is_over():
            self.backEnd.show_winner()
            self.endGame()

    def connectDoubleAI(self):
        """
        Pour connecter deux IA
        :return:
        """
        while not self.backEnd.is_over():
            self.isWhiteTurn = True
            self.connectAI()
            self.humanIsPlaying = False
            self.isWhiteTurn = False

            self.connectAI()
        self.winner = self.backEnd.show_winner()
        self.endGame()




    def endGame(self):
        """
        pour gerer le fin de le jeu
        :return:
        """
        self.winner = self.backEnd.show_winner()
        xcoord, ycoord = self.Pos2DToPixelCoord(self.gridSize/2, self.gridSize/2)
        winnerText = "GAME OVER! JOUEUR :" + str(self.winner)+ " A GAGNÉ"


        paintText = QPainterPath()
        paintText.addText(xcoord -225 , ycoord +150 ,
                            QFont("Comic Sans", int(self.squareSize * 0.15)), winnerText)
        textPath = self.scene.addPath(paintText)
        textPath.setPen(QPen())
        textPath.setBrush(self.endTextBrush)
        self.humanIsPlaying = False
        self.makeExitButton()
        QApplication.processEvents()

    def makeExitButton(self):
        """
        button pour quitter le jeu
        :return:
        """
        self.exitButton = QPushButton("Quitter",self)
        self.exitButton.setGeometry(800,500,100,100)
        self.exitButton.clicked.connect(self.leave)


    def leave(self):
        """
        Connection pour le button pour quiter le jeu
        :return:
        """
        self.close()
