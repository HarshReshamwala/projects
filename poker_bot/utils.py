from deuces import Deck, Evaluator, Card 

evaluator = Evaluator()

def evaluate_board(hand, board):
    """
    Evaluates the strength of a hand given community cards.
    :param hand: List of two cards representing player's hand
    :param board: List of five community cards
    :return: Hand strength score
    """
    # Convert the hand and board to Deuces format
    deuces_hand = [Card.new(card) for card in hand]
    deuces_board = [Card.new(card) for card in board]

    
    # Evaluate hand strength
    return evaluator.evaluate(deuces_board, deuces_hand)