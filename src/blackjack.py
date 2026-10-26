import random

BUST = 22

VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
TENS = ['10', 'J', 'Q', 'K']

def set_seed(seed):
    random.seed(seed)

# Deal a card.
def deal_card():
    return random.choice(VALUES)

# Sum a hand according to blackjack rules.
def sum_hand(hand):
    aces = 0
    total = 0

    for value in hand:
        if value == 'A':
            aces += 1
        elif value in TENS:
            total += 10
        else:
            total += int(value)

    # Add aces seperately as their quantity must be considered.
    total += aces

    # Determine the best use of the aces, if any.
    # Only one ace per hand can be counted as 11 to prevent going bust.
    if aces > 0 and total + 10 < BUST:
        total += 10

    return total

# Determine if a hand is a blackjack.
def blackjack(hand):
    return len(hand) == 2 and sum_hand(hand) == 21

# Determine if a hand busts.
def bust(hand):
    return sum_hand(hand) >= BUST

# Determine if a hand is a soft hand (contains an ace).
# Needs fixing prior to implementation.
def soft_hand(hand):
    return 'A' in hand and not bust(hand)

# Deal initial hands to player and dealer.
def deal_initial_hands():
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
        
    return player_hand, dealer_hand

# Player's gameplay logic.
# Can be modified to implement different strategies.
# Argument 'dealer_upcard' is for future use.
def player_turn(hand, dealer_upcard, stand_value):
    while True:
        if bust(hand):
            break
        elif sum_hand(hand) < stand_value:
            hand.append(deal_card())
        else:
            break

# Dealer's gameplay logic.
# These are generally fixed rules.
def dealer_turn(hand):
    while True:
        if bust(hand):
            break
        elif sum_hand(hand) < 17:
            hand.append(deal_card())
        else:
            break

# 0 is a push, 1 is a player win, -1 is a dealer win.
def determine_winner(player_hand, dealer_hand):
    # Check for a blackjack in either hand.
    if blackjack(player_hand):
        if blackjack(dealer_hand):
            # Push if both have a blackjack.
            return 0
        else:
            # Win if only player has blackjack.
            return 1
    elif blackjack(dealer_hand):
        # Lose if only dealer has black jack.
        return -1

    # Check for a bust.
    if bust(player_hand) and bust(dealer_hand):
            # Error if both hands bust, this should never occur if game logic is sound.
            raise RuntimeError("Invalid game state, both hands bust.")
    elif bust(player_hand):
        # Lose if only player bust.
        return -1
    elif bust(dealer_hand):
        # Win if only dealer bust.
        return 1

    # If neither hand contains a blackjack nor is bust, determine which is stronger.
    if sum_hand(player_hand) == sum_hand(dealer_hand):
        return 0
    elif sum_hand(player_hand) > sum_hand(dealer_hand):
        return 1
    elif sum_hand(player_hand) < sum_hand(dealer_hand):
        return -1

def play_round(stand_value):
    # Default outcome is 2 to indicate an error in the game logic.
    # This should never be returned if the game runs correctly.
    round_action = {'player_hand': [],
                    'dealer_hand': [],
                    'player_blackjack': False,
                    'dealer_blackjack': False,
                    'outcome': 2}

    # Deal starting hands prior to 'play'.
    round_action['player_hand'], round_action['dealer_hand'] = deal_initial_hands()

    # Immediately check for blackjack before continuing.
    # Assigning these to variables for future use.
    player_blackjack = blackjack(round_action['player_hand'])
    dealer_blackjack = blackjack(round_action['dealer_hand'])

    # If either player or dealer has a blackjack, end the round immediately.
    if player_blackjack or dealer_blackjack:
        round_action['player_blackjack'] = player_blackjack
        round_action['dealer_blackjack'] = dealer_blackjack
        round_action['outcome'] = determine_winner(round_action['player_hand'], round_action['dealer_hand'])

        return round_action

    # Player's turn.
    player_turn(round_action['player_hand'], round_action['dealer_hand'][0], stand_value)

    # If the player hasn't bust, allow the dealer to play.
    if not bust(round_action['player_hand']):
        dealer_turn(round_action['dealer_hand'])

    # Determine a winner.
    round_action['outcome'] = determine_winner(round_action['player_hand'], round_action['dealer_hand'])

    # Ensure the outcomex of the game is a valid figure (-1, 0, 1).
    if round_action['outcome'] not in [-1, 0, 1]:
        raise ValueError('Invalid round outcome, internal game logic error.')
    
    return round_action
