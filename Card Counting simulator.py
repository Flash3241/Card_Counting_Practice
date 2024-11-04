import pygame
import random
import os

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)  # Dark green for background

# Constants for display dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack")

# Load card images
CARD_IMAGES = {}
CARD_BACK = pygame.image.load("backcard.png")
CARD_BACK = pygame.transform.scale(CARD_BACK, (60, 90))

# Function to load and scale card images
def load_card_images():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    for suit in suits:
        for rank in ranks:
            image_name = f"{rank}_of_{suit}.png"
            path = os.path.join("cards", image_name)
            card_image = pygame.image.load(path)
            CARD_IMAGES[f"{rank} of {suit}"] = pygame.transform.scale(card_image, (60, 90))

load_card_images()

# Card counting variable
running_count = 0  # Hi-Lo card counting strategy

# Card and Deck classes
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    @property
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    def get_image(self):
        key = f"{self.rank} of {self.suit}"
        return CARD_IMAGES[key]

    def count_value(self):
        # Returns the counting value of the card according to the Hi-Lo system
        if self.rank in ['2', '3', '4', '5', '6']:
            return +1
        elif self.rank in ['10', 'J', 'Q', 'K', 'A']:
            return -1
        else:
            return 0

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in ['hearts', 'diamonds', 'clubs', 'spades']
                      for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']]
        random.shuffle(self.cards)

    def deal(self):
        card = self.cards.pop()
        update_count(card)  # Update the running count when a card is dealt
        return card

def update_count(card):
    global running_count
    running_count += card.count_value()

# Player and Dealer classes
class Player:
    def __init__(self):
        self.hand = []
        self.standing = False

    def hit(self, card):
        self.hand.append(card)

    def stand(self):
        self.standing = True

    def hand_value(self):
        value = sum(card.value for card in self.hand)
        aces = sum(1 for card in self.hand if card.rank == 'A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_busted(self):
        return self.hand_value() > 21

    def draw_hand(self, screen, x, y):
        for idx, card in enumerate(self.hand):
            screen.blit(card.get_image(), (x + idx * 20, y))

class Dealer(Player):
    def __init__(self):
        super().__init__()
        self.show_all_cards = False  # Start with only one card shown

    def play_hand(self, deck):
        self.show_all_cards = True  # Show all cards when dealer starts their turn
        while self.hand_value() < 17:
            pygame.time.delay(500)  # Add a 0.5 second delay for each card dealt
            self.hit(deck.deal())
            draw_table()  # Refresh the screen after each hit to show the new card
            pygame.display.flip()  # Update the display to show the card
            print(f"Dealer hits, hand value: {self.hand_value()}")  # Debugging statement
        print("Dealer finished playing. Cards should be revealed.")
        self.show_all_cards = True  # Ensure all cards remain shown after dealer finishes their turn

    def draw_hand(self, screen, x, y):
        for idx, card in enumerate(self.hand):
            if idx == 0 and not self.show_all_cards:
                screen.blit(CARD_BACK, (x, y))  # Show back of card if dealer's turn hasn't started
            else:
                screen.blit(card.get_image(), (x + idx * 20, y))  # Show face of card


# Initialize the game
deck = Deck()
player = Player()
dealer = Dealer()
player_balance = 100
bet = 10
waiting_for_next_round = False  # New flag to control waiting for 'N' key

# Function to start a new round
def start_new_round():
    global deck, player, dealer, bet, player_balance, waiting_for_next_round, running_count
    deck = Deck()
    player = Player()
    dealer = Dealer()
    waiting_for_next_round = False  # Reset flag for new round

    # Deal initial hands
    player.hit(deck.deal())
    player.hit(deck.deal())
    dealer.hit(deck.deal())
    dealer.hit(deck.deal())

# Draw game state
def draw_table():
    screen.fill(GREEN)

    # Display dealer's hand
    dealer.draw_hand(screen, 300, 50)
    # Display player's hand
    player.draw_hand(screen, 300, 400)

    # Display balance, bet, and running count
    font = pygame.font.Font(None, 36)
    balance_text = font.render(f"Balance: ${player_balance}", True, WHITE)
    bet_text = font.render(f"Bet: ${bet}", True, WHITE)
    count_text = font.render(f"Count: {running_count}", True, WHITE)
    screen.blit(balance_text, (10, 10))
    screen.blit(bet_text, (10, 50))
    screen.blit(count_text, (10, 90))

    pygame.display.flip()

# Main game loop
running = True
game_over = False
start_new_round()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h and not player.standing and not game_over:
                # Player chooses to hit
                player.hit(deck.deal())
                if player.is_busted():
                    print("Player busted!")
                    dealer.show_all_cards = True  # Reveal dealer's cards if player busts
                    game_over = True
            elif event.key == pygame.K_s and not game_over:
                # Player chooses to stand
                player.stand()
                dealer.show_all_cards = True  # Reveal dealer's cards when player stands
                draw_table()  # Refresh table to reveal cards immediately
                dealer.play_hand(deck)
                game_over = True
            elif event.key == pygame.K_n and waiting_for_next_round:
                # Start a new round when 'N' is pressed after game over
                start_new_round()
                game_over = False

    # Check game result after player stands or if they busted
    if game_over and not waiting_for_next_round:
        draw_table()  # Refresh display to show all cards
        if player.is_busted():
            player_balance -= bet
            print("Player loses!")
        elif dealer.is_busted() or player.hand_value() > dealer.hand_value():
            player_balance += bet
            print("Player wins!")
        elif player.hand_value() < dealer.hand_value():
            player_balance -= bet
            print("Player loses!")
        else:
            print("Push! No one wins.")
        
        waiting_for_next_round = True  # Set flag to wait for 'N' key
        print(f"End of Round Count: {running_count}")
        print("Press 'N' to start the next round.")

    # Update the display
    draw_table()

pygame.quit()
