import hashlib
import time

class Move:
    NONE = 0
    ROCK = 1 
    PAPER = 2
    SCISSORS = 3
    
    def _init_(self, commitment, move=0):
        self.commitment = commitment #secret string
        self.move = move
        
    @classmethod
    def move_to_str(cls, move):
        return {
            cls.NONE: "None",
            cls.ROCK: "Rock",
            cls.PAPER: "Paper",
            cls.SCISSORS: "Scissors"
        }[move]
        
class Challenge:
    def _init_(self, creator_address, _id, commitment):
        self.creator_address = creator_address
        self.opponnet_address = None
        
        self.commitments = {
            self.creator_address: Move(commitment)
        }
        
        self.id = _id
        self.created_at = time.time()
    
    def add_opponent(self, address, commitment):
        self.opponnet_address = address
        self.commitments[address] = Move(commitment)   
        
    def reveal(self, address, move, nonce):
        if not self.has_opponent_commited():
            raise Exception("Opponent has not committed.")
        reveal_hash = Challenge.generate_hash(nonce + move)
        committed_move = self.commitments.get(address)
        if committed_move.commitment != reveal_hash :
            raise Exception("Move does not match the commitment.")
        
        self.commitments[address].move = int(move)
        
    @staticmethod
    def generate_hash(input):
        return hashlib.sha256(input.encode()).hexdigest()
    
    def both_revealed(self):
        opponent_move = self.commitments[self.opponnet_address].move
        creator_move = self.commitments[self.creator_address].move
        return opponent_move != Move.NONE and creator_move != Move.NONE
    
    def has_opponent_commited(self):
        return self.commitments.get(self.opponnet_address) != None
    
    def valuate_winner(self):
        opponent_move = self.commitments[self.opponnet_address].move
        creator_move = self.commitments[self.creator_address].move
        
        # rock beat scissors
        if creator_move == Move.ROCK and opponent_move == Move.SCISSORS:
            self.winner_address = self.creator_address
        elif creator_move == Move.SCISSORS and opponent_move == Move.ROCK:
            self.winner_address = self.opponnet_address
            
        # scissors beat paper
        elif creator_move == Move.SCISSORS and opponent_move == Move.PAPER:
            self.winner_address = self.creator_address
        elif creator_move == Move.PAPER and opponent_move == Move.SCISSORS:
            self.winner_address = self.opponnet_address
            
        # paper beat rock
        elif creator_move == Move.PAPER and opponent_move == Move.ROCK:
            self.winner_address = self.creator_address
        elif creator_move == Move.ROCK and opponent_move == Move.PAPER:
            self.winner_address = self.opponnet_address
            
        return self.winner_address
        