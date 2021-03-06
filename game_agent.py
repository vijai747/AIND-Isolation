"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random
import math

class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass

def custom_score(game, player):
    """Aggressive player heuristic : this algorithm makes the player act more
    aggressively prioritizing game boards in which the difference between player
    and opponent moves is the greatest.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    return float((2 * own_moves) - opp_moves)

def custom_score_2(game, player):
    """Player distance heuristic : maximize the distance between players on the
    board.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).
    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)
    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float('-inf')

    if game.is_winner(player):
        return float('inf')

    opp_player = game.get_opponent(player)
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(opp_player))

    distance = player_distance(game, player, opp_player)

    return float(distance)

def player_distance(game, player, opp_player):
    """Distance between the player and opponent's location
    """

    player_location = game.get_player_location(player)
    opponent_location = game.get_player_location(opp_player)

    x_squared = math.pow(player_location[0] - opponent_location[0], 2)
    y_squared = math.pow(player_location[1] - opponent_location[1], 2)

    return math.sqrt(x_squared + y_squared)

def custom_score_3(game, player):
    """Give bonus points to players in non-corner squares (with max move count >= 4)

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    center_bonus = 2
    if location_is_center(game, game.get_player_location(player)):
        own_moves += center_bonus

    return float(own_moves - opp_moves)

def location_is_center(game, player_location):
    """Evaluate whether player is located on a high-value square (move score >= 4)"""

    corner_positions = [(0,0),(0,1),(0,5),(0,6),
                        (1,0),(1,6),
                        (5,0),(5,6),
                        (6,0),(6,1),(6,5),(6,6)]

    return not (player_location in corner_positions)

class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=20.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def terminal_test(self, game):
        """ Return True if the game is over for the active player
        and False otherwise.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        return not bool(game.get_legal_moves())

    def min_value(self, game, depth):
        """ Return the value for a win if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if depth == 0 or self.terminal_test(game):
            return self.score(game, self)

        v = float("inf")
        for m in game.get_legal_moves():
            v = min(v, self.max_value(game.forecast_move(m), depth-1))
        return v

    def max_value(self, game, depth):
        """ Return the value for a loss if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if depth == 0 or self.terminal_test(game):
            return self.score(game, self)

        v = float("-inf")
        for m in game.get_legal_moves():
            v = max(v, self.min_value(game.forecast_move(m), depth-1))
        return v

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if self.terminal_test(game):
            return (-1, -1)

        best_score = float("-inf")
        n = game.get_legal_moves()
        best_move = n[0]

        for m in game.get_legal_moves():
            v = self.min_value(game.forecast_move(m), depth-1)
            if v > best_score:
                best_score = v
                best_move = m
        return best_move

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)
        iterative_depth = 0

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            while True:
                best_move = self.alphabeta(game, iterative_depth)
                iterative_depth += 1
        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def terminal_test(self, game):
        """ Return True if the game is over for the active player
        and False otherwise.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        return not bool(game.get_legal_moves())

    def min_value(self, game, depth, alpha, beta):

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if depth == 0 or self.terminal_test(game):
            return self.score(game, self)

        v = float("inf")
        for c in game.get_legal_moves():
            vPrime = self.max_value(game.forecast_move(c), depth-1, alpha, beta)
            if vPrime < v:
                v = vPrime
            if vPrime <= alpha:
                return v
            if vPrime < beta:
                beta = vPrime
        return v

    def max_value(self, game, depth, alpha, beta):

        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if depth == 0 or self.terminal_test(game):
            return self.score(game, self)

        v = float("-inf")
        for c in game.get_legal_moves():
            vPrime = self.min_value(game.forecast_move(c), depth-1, alpha, beta)
            if vPrime > v:
                v = vPrime
            if vPrime >= beta:
                return v
            if vPrime > alpha:
                alpha = vPrime
        return v

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if depth == 0:
            return self.score(game, self)

        if self.terminal_test(game):
            return (-1, -1)

        best_score = float("-inf")
        n = game.get_legal_moves()
        best_move = n[0]

        for m in game.get_legal_moves():
            v = self.min_value(game.forecast_move(m), depth-1, alpha, beta)
            if v > best_score:
                best_score = v
                best_move = m
            alpha = max(alpha, v)
        return best_move
