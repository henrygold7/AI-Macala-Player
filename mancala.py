
import copy

class MancalaMove:

    def __init__(self, traynum, player):
        self.tray = traynum
        self.player = player

    def __str__(self):
        return str(self.tray)

    def __eq__(self, other):
        return self.tray == other.tray and self.player == other.player

class MancalaState:

    def __init__(self):

        self.player1trays = [4,4,4,4,4,4,0]
        self.player2trays = [4,4,4,4,4,4,0]
        self.current = 'player1'

    def evaluation(self):
        """Difference between player1 and player2 pieces on board."""
        return self.player1trays[6] - self.player2trays[6]
    
    def available_moves(self):
        """Returns a list of all nonempty trays owned by current player"""

        if self.current == 'player1':
            traylist = self.player1trays
        else:
            traylist = self.player2trays

        moves = []
        for i in range(6):
            if traylist[i] > 0:
                moves.append(MancalaMove(i,self.current))
        
        return moves

    def apply_move(self, move):
        """Applies a Mancala move"""

        newstate = copy.deepcopy(self)
        if self.current == 'player1':
            otherplayer = 'player2'
            traylistcurr = self.player1trays
            traylistother = self.player2trays
        else:
            otherplayer = 'player1'
            traylistcurr = self.player2trays
            traylistother = self.player1trays
        
        place = move.tray + 1
        marble_count = traylistcurr[move.tray]
        traylistcurr[move.tray] = 0
        flipped = False
        end_in_tray = False

        while marble_count > 0:
            # print("marble count: ",marble_count)
            # print("place: ",place)
            # print("flipped? ",flipped)
            # print("--------------------------")
            if marble_count == 1 and not flipped:
                if place == 7:
                    flipped = True
                    place = 0
                    continue
                if place == 6:
                    traylistcurr[place] += 1
                    end_in_tray = True
                elif traylistcurr[place] == 0 and traylistother[5-place] > 0:
                    traylistcurr[6] += 1 + traylistother[5-place]
                    traylistother[5-place] = 0
                else:
                    traylistcurr[place] += 1
                    
            elif not flipped:
                if place <= 6:
                    traylistcurr[place] += 1
                    place += 1
                elif place == 7:
                    flipped = True
                    place = 0
                    continue
            elif flipped:
                if place <= 5:
                    traylistother[place] += 1
                    place += 1
                elif place == 6:
                    flipped = False
                    place = 0
                    continue
            marble_count -= 1

        if self.current == 'player1':
            newstate.player1trays = traylistcurr
            newstate.player2trays = traylistother
        else:
            newstate.player1trays = traylistother
            newstate.player2trays = traylistcurr
        
        if not end_in_tray:
            newstate.current = otherplayer

        return newstate

    def game_over(self):
        """True if the game is over; false otherwise"""
        return self.player1trays[:6] == [0,0,0,0,0,0] or self.player2trays[:6] == [0,0,0,0,0,0]

    def winner(self):
        """ PRE:  self.game_over().  Return winner or 'draw' """
        assert self.game_over()
        ev = self.evaluation()
        return 'draw' if ev == 0 else 'player1' if ev > 0 else 'player2'

    def end_game(self):
        player1sum = 0
        player2sum = 0
        for i in range(6):
            player1sum += self.player1trays[i]
            player2sum += self.player2trays[i]

            self.player1trays[i] = 0
            self.player2trays[i] = 0
    
        self.player1trays[6] += player1sum
        self.player2trays[6] += player2sum

    def __str__(self):
        player1trays = ' '
        player2trays = ' '
        for i in range(6):
            player1trays += str(self.player1trays[i])+ ' '
            player2trays += str(self.player2trays[5-i])+ ' '
        result = '  '+player2trays+'  '+'\n'
        result += str(self.player2trays[6])+' ------------- '+str(self.player1trays[6]) + '\n'
        result += '  '+player1trays+'  '+'\n'
        return result
        
class MancalaGame:

    def __init__(self, player1, player2, verbose=True):

        self.player1 = player1
        self.player2 = player2

        self.verbose = verbose

        self.board = MancalaState()

    def log(self, args):
        """Prints *args if verbose=True"""
        if self.verbose:
            print(args)
    def play_game(self):
        
        self.log(self.board)

        while not self.board.game_over():
            if self.board.current == 'player1':
                player = self.player1
            else:
                player = self.player2
        
            move = player.make_move(self.board)

            self.board = self.board.apply_move(move)

            self.log(self.board)
        
        self.board.end_game()
        self.log(self.board)

        self.log("Winner is", self.board.winner())

        return self.board.winner()