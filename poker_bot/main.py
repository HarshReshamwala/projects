from mcts import GameState, MCTS, Node
from deuces import Card

if __name__ == "__main__":
    # Assume we have a current game state (hand, board, pot size, etc.)
    
    board = [Card.new('As'), Card.new('Kd'), Card.new('Qc')]  # Example community cards
    # Assuming three players with unique hands
    hands = {
        1: [Card.new('Jh'), Card.new('Th')],
        2: [Card.new('9c'), Card.new('9d')],
        3: [Card.new('8s'), Card.new('7s')]
    }

    pot_size = 100
    current_bet = 50
    player_turn = 1
    stacks = {1: 1000, 2: 1000, 3: 1000}  # Dictionary with the stack size of each player
    active_players = [1, 2, 3]

    # Initialize the GameState with the correct parameters
    initial_state = GameState(
        hands=hands,
        board=board,
        pot_size=pot_size,
        current_bet=current_bet,
        player_turn=player_turn,
        stacks=stacks,
        active_players=active_players
    )
    
    root = Node(state=initial_state)
    mcts = MCTS()

    # Run MCTS to determine the best action
    best_action = mcts.best_action(root, simulations_number=100)

    print(f"The best action to take is: {best_action}")
