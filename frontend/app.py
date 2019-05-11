import sys
import copy
import random
import pygame
import itertools

from loader import CardLoader, BackgroundLoader, ButtonLoader, BackCardLoader

class GameRule:
    def __init__(self, cards):
        self.cards = cards
        self.card_counter = {
            3 : [],
            4 : [],
            5 : [],
            6 : [],
            7 : [],
            8 : [],
            9 : [],
            10 : [],
            11 : [],
            12 : [],
            13 : [],
            14 : [],
            15 : [],
        }
        self.card_type_counter = {
            'clover' : [],
            'diamond' : [],
            'heart' : [],
            'spade' : [],
        }
        self.counting_card()

        self.combo = {
            "pair" : [],
            "trice" : [],
            "straight" : [],
            "flush" : [],
            "four-of-a-kind" : [],
            "full-house" : [],
        }

        self.generate_combo()

    def counting_card(self):
        index = 0
        for card in self.cards:
            self.card_counter[card.number].append(index)
            self.card_type_counter[card.type].append(index)
            index += 1

    def generate_combo(self):
        index_pair = []
        index_trice = []
        index_straight = []
        index_flush = []
        index_four = []
        index_full_house = []
        for key, value in self.card_counter.items():
            if len(value) == 2:
                index_pair.append([value[0], value[1]])
            elif len(value) == 3:
                index_trice.append([value[0], value[1], value[2]])
            elif len(value) == 4:
                for index in range(3,16):
                    if index != key and len(self.card_counter[index]) != 4:
                        for index_card in self.card_counter[index]:
                            index_four.append([value[0], value[1], value[2], value[3], index_card])


            if key <= 11 :
                straight_exist = True
                for straight_key in range(key, key+5):
                    if len(self.card_counter[straight_key]) == 0 :
                        straight_exist = False
                
                if straight_exist :
                    for straight1 in self.card_counter[key]:
                        for straight2 in self.card_counter[key+1]:
                            for straight3 in self.card_counter[key+2]:
                                for straight4 in self.card_counter[key+3]:
                                    for straight5 in self.card_counter[key+4]:
                                        index_straight.append([straight1, straight2, straight3, straight4, straight5])
        
        for key, value in self.card_type_counter.items():
            if len(value) >= 5:
                for permutation in itertools.combinations(value, 5):
                    index_flush.append(permutation)

        for pair in index_pair:
            for trice in index_trice:
                index_full_house.append([pair[0], pair[1], trice[0], trice[1], trice[2]])

        
        
        for trice in index_trice:
            index_pair.append([trice[0], trice[1]])
            index_pair.append([trice[0], trice[2]])
            index_pair.append([trice[1], trice[2]])

        self.combo['pair'] = index_pair
        self.combo['trice'] = index_trice
        self.combo['straight'] = index_straight
        self.combo['flush'] = index_flush
        self.combo['four-of-a-kind'] = index_four
        self.combo['full-house'] = index_full_house
            

class Game:
    def __init__(self):
        self.SCREEN_RESOLUTION = (1280, 720)
        self.CAPTION = "Capsa Banting Super"

        # init pygame
        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        
        # set pygame screen
        self.screen = pygame.display.set_mode(self.SCREEN_RESOLUTION, 0 , 32)

        # load assets
        self.card_loader = CardLoader().load()
        self.background_loader = BackgroundLoader().load()
        self.button_loader = ButtonLoader().load()
        self.back_card_loader = BackCardLoader().load()
        self.CARD_IN_DECK = 13
        self.CARD_SELECTED = 0
        self.CARD_SELECTED_BEFORE = 0
        
        # TODO: shuffle on server
        random.shuffle(self.card_loader.card)

        # set button image to disabled
        self.button_loader.button['play'].index = 2

    def start(self):
        # TODO: get player card index from server
        # shallow copy
        player_card = copy.copy(self.card_loader.card[:13])
        player_card.sort()
        choosen_card = []
        choosen_card_before = []
        counter_button = {
            'pair' : 0,
            'trice' : 0,
            'straight' : 0,
            'flush' : 0,
            'full-house': 0,
            'four-of-a-kind' : 0,
        }
        game_rule = ''

        player_card_count = [0] * 4
        player_card_count[0] = len(player_card)
        player_card_count[1] = 13
        player_card_count[2] = 13
        player_card_count[3] = 13

        combo_list = ['pair', 'trice', 'straight', 'flush' , 'full-house', 'four-of-a-kind']

        while True:

            game_rule = GameRule(player_card)

            for combo_name in combo_list:
                if len(game_rule.combo[combo_name]) == 0 :
                    self.button_loader.button[combo_name].index = 2
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # click on player card
                    exist_select = False
                    for card in player_card:
                        card_rect = card.sprite.get_rect()
                        
                        # if card is not selected the width of bounding box become half of normal
                        if not card.select and card != player_card[-1]:
                            card_rect.w = card_rect.w//2
                        # if sprite card is clicked in the bounding box then card is set to selected or not selected
                        if card_rect.collidepoint(mouse_x - card.pos['x'], mouse_y - card.pos['y']):
                            print(card.type, card.number)
                            card.select = not card.select
                        # if card is selected, set the play button to click-able
                        if card.select:
                            exist_select = True
                            self.button_loader.button['play'].index = 0
                    
                    # if no card selected, set the play button to disabled
                    if not exist_select:
                        self.button_loader.button['play'].index = 2

                    # click on button
                    # if button click and not disabled, set the sprite to clicked
                    for button in self.button_loader.button.values():
                        if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 0:
                            button.index = 1

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    # if play button clicked
                    if self.button_loader.button['play'].sprite[0].get_rect().collidepoint(mouse_x - self.button_loader.button['play'].pos['x'], mouse_y - self.button_loader.button['play'].pos['y']) and self.button_loader.button['play'].index != 2:
                        center_position_x = 640
                        center_position_y = 360
                        
                        counter_card = 0
                        choosen_card_before = copy.copy(choosen_card)
                        choosen_card = []
                        for card in player_card:
                            if card.select :
                                counter_card += 1
                                choosen_card.append(card)

                        for card in choosen_card:
                            player_card.remove(card)

                        self.CARD_SELECTED_BEFORE = self.CARD_SELECTED
                        self.CARD_SELECTED = counter_card
                        self.CARD_IN_DECK -= self.CARD_SELECTED

                        PADDING_BEFORE = 10
                        PADDING = 2
                        bounding_box_card_x = ( card.sprite.get_width() + PADDING ) * counter_card
                        bounding_box_card_y = ( card.sprite.get_height() )

                        center_position_x -= bounding_box_card_x // 2
                        center_position_y -= bounding_box_card_y // 2

                        for i in range(counter_card):
                            choosen_card[i].pos['y'] = center_position_y
                            choosen_card[i].pos['x'] = center_position_x + i * ( choosen_card[i].sprite.get_width() + PADDING ) 
                            print(choosen_card[i].position())

                        print(len(choosen_card_before), self.CARD_SELECTED_BEFORE)
                        for i in range(self.CARD_SELECTED_BEFORE):
                            choosen_card_before[i].pos['y'] -= choosen_card_before[i].sprite.get_height() + PADDING_BEFORE

                        self.button_loader.button['play'].index = 2

                    for combo_name in combo_list:
                        if len(game_rule.combo[combo_name]) == 0 :
                           self.button_loader.button[combo_name].index = 2
                        if self.button_loader.button[combo_name].sprite[0].get_rect().collidepoint(mouse_x - self.button_loader.button[combo_name].pos['x'], mouse_y - self.button_loader.button[combo_name].pos['y']) and self.button_loader.button[combo_name].index != 2:
                            combo = game_rule.combo[combo_name]
                            print(game_rule.card_counter)
                            print(combo)

                            counter_button[combo_name] += 1
                            counter_button[combo_name] %= (len(combo) + 1)
                            index = counter_button[combo_name]-1

                            for card in player_card:
                                card.select = False
                            
                            if counter_button[combo_name] > 0:
                                for idx in combo[index]:
                                    player_card[idx].select = True
                                self.button_loader.button['play'].index = 0
                            else :
                                self.button_loader.button['play'].index = 2

                    # if button is clicked, on mouseup set the sprite to click-able
                    for button in self.button_loader.button.values():
                        if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 1:
                            button.index=0

            # TODO: make a function for set initial position
            # set initial position of button
            self.button_loader.button['play'].pos['x'] = 850
            self.button_loader.button['play'].pos['y'] = 595

            self.button_loader.button['pass'].pos['x'] = 850
            self.button_loader.button['pass'].pos['y'] = 550

            for i in range(len(combo_list)):
                self.button_loader.button[combo_list[i]].pos['y'] = 650
                self.button_loader.button[combo_list[i]].pos['x'] = 400 + i * (self.button_loader.button[combo_list[i]].sprite[0].get_width()+3)

            # load assets to the screen -> (image,position)
            self.screen.blit(self.background_loader.background, (0,0))
            self.screen.blit(self.button_loader.button['play'].get_sprite(), self.button_loader.button['play'].position())
            self.screen.blit(self.button_loader.button['pass'].get_sprite(), self.button_loader.button['pass'].position())

            for combo_name in combo_list :
                self.screen.blit(self.button_loader.button[combo_name].get_sprite(), self.button_loader.button[combo_name].position())

            # set position of back card player 1
            for i in range(player_card_count[1]):
                player_back_card = self.back_card_loader.backcard
                player_back_card = pygame.transform.rotate(player_back_card, 90)
                self.screen.blit(player_back_card, (70, 100 + i * (player_back_card.get_height()//3)))

            for i in range(player_card_count[1]):
                player_back_card = self.back_card_loader.backcard
                self.screen.blit(player_back_card, (400 + i * (player_back_card.get_width()//3) , 7))

            for i in range(player_card_count[3]):
                player_back_card = self.back_card_loader.backcard
                player_back_card = pygame.transform.rotate(player_back_card, 90)
                self.screen.blit(player_back_card, (1080, 100 + i * (player_back_card.get_height()//3)))

            # set position of card
            for i in range(self.CARD_IN_DECK):   
                player_card[i].pos['y'] = 550
                player_card[i].pos['x'] = 400 + i * player_card[i].sprite.get_width()//2
                # if card is selected, set position higher 
                if player_card[i].select :
                    player_card[i].pos['y'] -= 32

            # load card assets to the screen
            for i in range(self.CARD_IN_DECK):
                self.screen.blit(player_card[i].sprite, player_card[i].position())

            for i in range(self.CARD_SELECTED):
                self.screen.blit(choosen_card[i].sprite, choosen_card[i].position())

            for i in range(self.CARD_SELECTED_BEFORE):
                self.screen.blit(choosen_card_before[i].sprite, choosen_card_before[i].position())


            pygame.display.update()

        
if __name__ == "__main__":
    app = Game()
    app.start()
