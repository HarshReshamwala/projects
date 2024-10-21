import numpy as np
import random
from deuces import Deck, Evaluator, Card

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state       # Current state of the game
        self.parent = parent     # Parent node
        self.children = []       # List of child nodes
        self.visits = 0          # Number of times the node has been visited
        self.wins = 0            # Number of wins from this node
        self.action = action     # Action taken to get to this node
        self.active_players = []
        self.board = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def is_fully_expanded(self):
        # If all possible actions from this state have been explored
        return len(self.children) == len(self.state.get_possible_actions())

    def best_child(self, exploration_weight=1.41):
        # UCB1 algorithm to balance exploration and exploitation
        best_score = -float('inf')
        best_child = None

        for child in self.children:
            exploitation = child.wins / child.visits
            exploration = exploration_weight * np.sqrt(np.log(self.visits) / child.visits)
            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_child = child

        return best_child
    
    def is_terminal(self):
        """
        Determines if the game state is terminal (e.g., after showdown).
        """
        # Terminal if there's only one active player left
        if len(self.active_players) == 1:
            return True
        
        # Terminal if all rounds have been played
        # Add your condition for terminal states like all community cards are dealt
        if len(self.board) == 5:  # Assuming 5 community cards means the game is over
            return True
        
        return False
    

class MCTS:
    def __init__(self, exploration_weight=1.41):
        self.exploration_weight = exploration_weight

    def selection(self, node):
        """
        Traverse the tree to find the most promising node to explore using UCB1.
        """
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            else:
                node = node.best_child(self.exploration_weight)
        return node

    def expansion(self, node):
        """
        Expand a node by adding a child node for each possible action.
        """
        action = random.choice(node.state.get_possible_actions())
        next_state = node.state.take_action(action)
        child_node = Node(state=next_state, parent=node, action=action)
        node.add_child(child_node)
        return child_node

    def simulation(self, node):
        """
        Simulate the game from the current state to a terminal state.
        """
        current_state = node.state

        while not current_state.is_terminal():
            possible_actions = current_state.get_possible_actions()
            action = random.choice(possible_actions)
            current_state = current_state.take_action(action)

        return current_state.get_result()

    def backpropagation(self, node, result):
        """
        Backpropagate the simulation result up the tree.
        """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def best_action(self, root, simulations_number=1000):
        """
        Run the MCTS algorithm to determine the best action from the root node.
        """
        for _ in range(simulations_number):
            node = self.selection(root)
            if not node.is_terminal():
                node = self.expansion(node)
            result = self.simulation(node)
            self.backpropagation(node, result)

        return root.best_child(exploration_weight=0).action


class GameState:
    def __init__(self, hands, board, pot_size, current_bet, player_turn, stacks, active_players):
        self.hands = hands                # Dict of player hands
        self.board = board                # List of community cards
        self.pot_size = pot_size          # Current pot size
        self.current_bet = current_bet    # Current highest bet on the table
        self.player_turn = player_turn    # Index of the player whose turn it is
        self.stacks = stacks              # Dict of player stacks (remaining chips)
        self.active_players = active_players # List of players still in the game

    def get_possible_actions(self):
        """
        Returns a list of possible actions for the current player.
        """
        actions = ['fold', 'call']
        if self.stacks[self.player_turn] > self.current_bet:
            actions.append('raise')
            actions.append('bet')
        if self.stacks[self.player_turn] <= self.current_bet:
            actions.append('allin')
        return actions

    def take_action(self, action, amount=None):
        """
        Apply an action and return the new game state.
        :param action: Action to be taken (fold, call, raise, bet, allin)
        :param amount: Amount to bet or raise if applicable
        """
        new_state = self._clone_state()
        
        if action == 'fold':
            # Remove the current player from active players
            new_state.active_players.remove(new_state.player_turn)
        
        elif action == 'call':
            call_amount = new_state.current_bet
            new_state.stacks[new_state.player_turn] -= call_amount
            new_state.pot_size += call_amount
        
        elif action == 'bet':
            bet_amount = amount if amount else new_state.current_bet
            new_state.current_bet = bet_amount
            new_state.stacks[new_state.player_turn] -= bet_amount
            new_state.pot_size += bet_amount
        
        elif action == 'raise':
            raise_amount = amount if amount else new_state.current_bet * 2
            new_state.current_bet = raise_amount
            new_state.stacks[new_state.player_turn] -= raise_amount
            new_state.pot_size += raise_amount
        
        elif action == 'allin':
            allin_amount = new_state.stacks[new_state.player_turn]
            new_state.stacks[new_state.player_turn] = 0
            new_state.pot_size += allin_amount
            new_state.current_bet = max(new_state.current_bet, allin_amount)

        # Move to the next player's turn
        if new_state.active_players:
            # Find the next active player
            current_player = new_state.player_turn
            while True:
                current_player = (current_player + 1) % (max(new_state.active_players) + 1)
                if current_player in new_state.active_players:
                    new_state.player_turn = current_player
                    break
        
        return new_state


    def get_result(self):
        print(f"Player hands: {self.hands}")
        print(f"Player turn: {self.player_turn}")

        player_hand = self.hands[self.player_turn]
        board = self.board
        evaluator = Evaluator()
        player_score = evaluator.evaluate(board, player_hand)
        
        return player_score




    def _clone_state(self):
        """
        Returns a deep copy of the game state.
        """
        return GameState(
            hands=self.hands.copy(),
            board=self.board[:],
            pot_size=self.pot_size,
            current_bet=self.current_bet,
            player_turn=self.player_turn,
            stacks=self.stacks.copy(),
            active_players=self.active_players[:]
        )
    
    def is_terminal(self):
        """
        Determines if the game state is terminal (e.g., after showdown).
        """
        # Terminal if there's only one active player left
        if len(self.active_players) == 1:
            return True
        
        # Terminal if all rounds have been played
        # Add your condition for terminal states like all community cards are dealt
        if len(self.board) == 5:  # Assuming 5 community cards means the game is over
            return True
        
        return False
    
