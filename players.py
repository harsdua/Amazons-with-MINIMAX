import random
from abc import ABCMeta, abstractmethod
from const import *
from exceptions import *
from action import Action
import time

class Player(metaclass=ABCMeta):
    """
    Classe abstraite représentant un joueur quelconque.

    Attributes:
        board (Board): le plateau de jeu sur lequel le joueur va effectuer ses actions
        player_id (int): l'id du joueur
    """
    def __init__(self, board, player_id, timeLimit = 2):
        self.board = board
        self.player_id = player_id
        self.timeLimit = timeLimit

    @abstractmethod
    def _play(self,coup=None):
        pass

    def play(self,coup=None):
        """
        Détermine l'action à effectuer et la joue sur le plateau
        """
        action = self._play(coup)
        self.board.act(action)
        return action


    @property
    def other_player_id(self):
        """
        int: l'id du joueur adverse
        """
        return PLAYER_2 if self.player_id == PLAYER_1 else PLAYER_1

class HumanPlayer(Player):
    """
    Spécialisation de Player représentant un joueur humain
    """
    def __init__(self, board, player_id, timeLimit = 2):
        super().__init__(board, player_id,timeLimit)

    def _play(self, coup = None):
        """"
        Récupère l'action désirée via stdin

        Returns:
            Action: l'action récupérée sur stdin
        """

        if coup:
            return coup
        else:
            valid = False
            joueur = WHITE if self.player_id == 1 else BLACK

            while not valid:
                coup = input(MESSAGE_COUP.format('1' if self.player_id == PLAYER_1 else '2'))
                if coup.count('>') != 2:
                    print(ERREUR_COUP)
                    continue
                try:
                    action = Action(*coup.split('>'), self.player_id)
                    valid = self.board.is_valid_action(action)
                except InvalidActionError:
                    continue
            return action


class AIPlayer(Player):
    """
    Spécialisation de la classe Player représentant un joueur utilisant un minimax
    """
    def __init__(self, board, player_id, timeLimit = 2):
        super().__init__(board, player_id,timeLimit)

    def _play(self,dummyCoup = None):

        """
        Détermine le meilleur coup à jouer

        Returns:
            Action: le meilleur coup déterminé via minimax
        """
        return self.minimax()[0]



    def minimax(self, depth=2, maximizing=True):

        """
        Détermine le coup optimal à jouer selon l'algorithme minimax.

        Args:
            depth (int): la profondeur à explorer dans l'arbre des coups possibles
            maximizing (bool): True si on cherche à maximiser le score et False si on cherche à le maximiser

        Returns:
            Action: le meilleur coup trouvé dans la profondeur explorée
        """

        starttime = time.time()
        if depth == 0:
            return (None, DRAW)
        if maximizing:
            best_score = -INF
            player = self.player_id
        else:
            best_score = +INF
            player = self.other_player_id
        best_actions = []
        assert self.board.has_moves(player)
        for action in self.board.possible_actions(player):
            self.board.act(action)
            winner = self.board.status.winner
            if winner is not None:
                score = WIN+depth  # Il vaut mieux gagner tôt (ou perdre tard) que de gagner tard (ou perdre tôt)
                if winner == self.other_player_id:
                    score *= -1
            else:
                score = self.minimax(depth-1, not maximizing)[1]
            self.board.undo()
            # Si on trouve un meilleur score
            if (score > best_score and maximizing) or (score < best_score and not maximizing):
                best_score = score
                best_actions = [action]
            elif score == best_score:
                if time.time()-starttime>self.timeLimit*0.65:
                    return best_actions[-1], best_score
                best_actions.append(action)

        return random.choice(best_actions), best_score

