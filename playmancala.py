from mancala import *
import random, math, time

class MoveNotAvailableError(Exception):
    """Raised when a move isn't available."""
    pass

class Node:

    def __init__(self, state, parent=None):
        self.parent = parent
        self.state = state

        if not self.parent:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

class MonteNode:
    def __init__(self, state, parent = None, h = None):
        self.parent = parent
        self.state = state
        self.n = 0
        self.w = 0
        self.move = None
        if self.n == 0:
            self.ucb = math.inf
        else:
            self.ucb = (self.w/self.n) + math.sqrt(2)*math.sqrt(math.log(self.parent.n)/self.n)
        self.children = []

    def make_child(self, other):
        self.children.append(other)

    def setmove(self, move):
        self.move = move

class MancalaPlayer():

    def __init__(self, player):
        assert player in ["player1", "player2"]
        self.player = player

    def make_move(self, state):
        pass

    def h(self, state):
        if self.player == 'player1':
            return state.player1trays[6] - state.player2trays[6]
        elif self.player == 'player2':
            return state.player2trays[6] - state.player1trays[6]

class HumanPlayer(MancalaPlayer):
    def make_move(self, state):
        available = state.available_moves()
        moves = ''
        for move in available:
            moves+= str(move.tray)+' '
        print("----- {}'s turn -----".format(state.current))
        print("Available moves are: ", moves)
        move_string = input("Enter the number in 0:5 of your chosen tray: ")

        try:
            traynum = int(move_string)
            move = MancalaMove(traynum, state.current)
            if move in available:
                return move
            else:
                raise MoveNotAvailableError # Indicates move isn't available

        except (ValueError, MoveNotAvailableError):
            print("({}) is not a legal move for {}. Try again\n".format(move_string, state.current))
            return self.make_move(state)

class RandomPlayer(MancalaPlayer):
    """Plays a random move."""

    def make_move(self, state):
        """Given a game state, return a move to make."""
        return random.choice(state.available_moves())

class AlphaBetaPlayer(MancalaPlayer):

    def make_move(self, state):
        available_moves = state.available_moves()
        node = Node(state)
        return self.alphabeta(node, 0, 49, True)[1]

    def alphabeta(self, node, alpha, beta, MAX_turn):

        if node.depth >= 12 or node.state.game_over():
            return self.h(node.state), None

        best_move = random.choice(node.state.available_moves())

        if MAX_turn:
            value = 0
            for move in node.state.available_moves():
                temp = copy.deepcopy(node.state)
                temp.apply_move(move)
                child = Node(temp, node)
                child_h = self.alphabeta(child, alpha, beta, not MAX_turn)[0]
                if child_h > value:
                    value = child_h
                    best_move = move
                alpha = max(value, alpha)
                if alpha >= beta:
                    return value, best_move
            return value, best_move
        else:
            value = 49
            for move in node.state.available_moves():
                temp = copy.deepcopy(node.state)
                temp.apply_move(move)
                child = Node(temp, node)
                child_h = self.alphabeta(child, alpha, beta, not MAX_turn)[0]
                if child_h < value:
                    value = child_h
                    best_move = move
                beta = min(value, beta)
                if alpha >= beta:
                    return value, best_move
            return value, best_move

class MonteCarloPlayer(MancalaPlayer):

    def make_move(self, state):
        available_moves = state.available_moves()
        timeleft = 15
        tree = set()
        root = MonteNode(state)
        tree.add(str(root))
        simulations = 0
        while timeleft > 0:
            start_time = time.time()
            new_node = self.descend(root, tree)
            new_node.parent.make_child(new_node)
            if new_node.state.game_over():
                pass
            else:
                tree.add(new_node)
            delta = self.simulate_game(new_node.state)
            self.update_game(new_node, delta)
            simulations += 1
            end_time = time.time()
            timeleft -= (end_time - start_time)
        best_move = random.choice(state.available_moves())
        best_rec = 0
        for c in root.children:
            if c.w / c.n > best_rec:
                best_rec = c.w / c.n
                best_move = c.move
        # print (str(simulations) + " simulations")
        return best_move

    def descend(self, node, tree):
        current_node = node
        while (str(current_node) in tree) and not current_node.state.game_over():
            best_child = None
            best_ucb = 0
            for move in current_node.state.available_moves():
                temp = copy.deepcopy(current_node.state)
                temp.apply_move(move)
                if str(temp) in tree:
                    for c in current_node.children:
                        if str(c.state) == str(temp):
                            child = c
                else:
                    child = MonteNode(temp, current_node)
                    child.setmove(move)
                if child.ucb > best_ucb:
                    best_child = child
            current_node = best_child
        return current_node

    def simulate_game(self, state):
        while not state.game_over():
            state = copy.deepcopy(state.apply_move(random.choice(state.available_moves())))

        winner = state.winner()
        if winner == self.player:
            return 1
        if winner == 'draw':
            return 0.5
        else:
            return 0
    
    def update_game(self, node, delta):
        current_node = node
        while current_node.parent:
            current_node.n += 1
            current_node.w += delta
            current_node = current_node.parent

def main():
    """plays the game"""

    player1 = MonteCarloPlayer('player1')
    player2 = HumanPlayer('player2')

    game = MancalaGame(player1, player2,verbose=True)
    winner = game.play_game()

    print("Winner is "+winner)

if __name__ == "__main__":
    main()
