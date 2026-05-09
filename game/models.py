import random

class GalacticDeck:
    PLANETS = ['Ice', 'Volcanic', 'Jungle', 'Desert']
    CARGO_TYPES = ['Fuel', 'Minerals', 'Food', 'Tech']
    
    def __init__(self):
        self.cards = self.generate_deck()

    def generate_deck(self):
        deck = []
        # Create standard cards (Match for numbers 1-7, 9, 10)
        for planet in self.PLANETS:
            for cargo in self.CARGO_TYPES:
                # Add multiple copies of each to make a 52ish card deck
                for _ in range(3): 
                    deck.append({'planet': planet, 'cargo': cargo, 'type': 'standard'})
        
        # Add Special Action Cards
        for planet in self.PLANETS:
            deck.append({'planet': planet, 'cargo': 'Wormhole', 'type': 'action'}) # The "8"
            deck.append({'planet': planet, 'cargo': 'Solar Flare', 'type': 'action'}) # Skip
            deck.append({'planet': planet, 'cargo': 'Pirate Raid', 'type': 'action'}) # Draw 2
            
        random.shuffle(deck)
        return deck
    def draw(self, num_cards=1):
        drawn_cards = []
        for _ in range(num_cards):
            if len(self.cards) > 0:
                drawn_cards.append(self.cards.pop(0)) # Take the top card
        return drawn_cards
# Test it out
# new_game = GalacticDeck()
# print(new_game.cards[0])