import numpy as np
import random
import pygame

# Dimensions
SCREEN_SIZE = 500
BORDER = 20
TILE_WIDTH = (SCREEN_SIZE - BORDER * 2) // 10
TEXT_HEIGHT = 85
SCREEN = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + TEXT_HEIGHT))

# Colors
COLOR_A = (255, 0, 0)  # In this case red
COLOR_B = (0, 255, 0)  # In this case green

# Font
pygame.font.init()
DISPLAY_FONT = pygame.font.SysFont("Arial", 30)

# Which plot should be display currently
PLOT_DISPLAY = 0  # 0 --> HitsMisses; 1 --> Probabilities


def lerp_color_in_hsv(rgb_a, rgb_b, t):
    def rgb_to_hsv(rgb):
        """
        Shamelessly stolen from GeeksForGeeks
        https://www.geeksforgeeks.org/program-change-rgb-color-model-hsv-color-model/
        """
        r, g, b = rgb
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        cmax = max(r, g, b)
        cmin = min(r, g, b)
        diff = cmax - cmin

        if cmax == cmin:
            h = 0
        elif cmax == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif cmax == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        elif cmax == b:
            h = (60 * ((r - g) / diff) + 240) % 360
        if cmax == 0:
            s = 0
        else:
            s = (diff / cmax) * 100

        v = cmax * 100
        return h, s, v

    def hsv_to_rgb(hsv):
        """
        Shamelessly stolen from StackOverflow
        https://stackoverflow.com/questions/24852345/hsv-to-rgb-color-conversion
        Modified slightly.
            Expected input values in [0, 1]. I want integer input and output
        """
        h, s, v = hsv
        h /= 360
        s /= 100
        v /= 100

        if s == 0.0: result = (v, v, v)
        i = int(h * 6.)  # XXX assume int() truncates!
        f = (h * 6.) - i;
        p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f));
        i %= 6
        if i == 0: result = (v, t, p)
        if i == 1: result = (q, v, p)
        if i == 2: result = (p, v, t)
        if i == 3: result = (p, q, v)
        if i == 4: result = (t, p, v)
        if i == 5: result = (v, p, q)

        return tuple(int(result[i] * 255) for i in range(3))

    hsv_a = rgb_to_hsv(rgb_a)
    hsv_b = rgb_to_hsv(rgb_b)

    hsv_new = (
        hsv_a[i] * (1 - t) + hsv_b[i] * t
        for i in range(3)
    )

    return hsv_to_rgb(hsv_new)


def display_plot(matrix, turn_count, title, is_probability_plot):
    SCREEN.fill((150, 150, 150))

    max_val = np.max(matrix)
    min_val = np.min(matrix)

    if is_probability_plot:
        # Simple error checking in case all matrix values are equal
        # Just draw all tiles the same color. Dont do any lerping
        if max_val == min_val:
            t_calculator_func = lambda mini, maxi, value: .5
        else:
            t_calculator_func = lambda mini, maxi, value: (value - mini) / (maxi - mini)

    # This is for the hit/misses map so t values are ordered based on what integer corresponds to a git/miss/unkown
    else:
        t_calculator_func = lambda mini, maxi, value: (.5, 1, 0)[round(value)]

    # For each tile
    for x in range(10):
        for y in range(10):
            val = matrix[y, x]
            color = lerp_color_in_hsv(
                COLOR_A,
                COLOR_B,
                t_calculator_func(min_val, max_val, val)
            )

            # Draw the color part of the tile
            pygame.draw.rect(
                SCREEN,
                color,
                (
                    BORDER + TILE_WIDTH * x,
                    BORDER + TILE_WIDTH * y,
                    TILE_WIDTH,
                    TILE_WIDTH
                )
            )

            # Draw the border of the tile
            pygame.draw.rect(
                SCREEN,
                (50, 50, 50),
                (
                    BORDER + TILE_WIDTH * x,
                    BORDER + TILE_WIDTH * y,
                    TILE_WIDTH,
                    TILE_WIDTH
                ),
                2
            )

    # Render and blit the text surfaces
    top_text = f"{title}. Turn: {turn_count}. Space for next turn."
    top_surface = DISPLAY_FONT.render(top_text, True, (0, 0, 0))

    bot_text = "ESC to exit. Left Shift to switch plots."
    bot_surface = DISPLAY_FONT.render(bot_text, True, (0, 0, 0))

    SCREEN.blit(top_surface, (BORDER, SCREEN_SIZE))
    SCREEN.blit(bot_surface, (BORDER, SCREEN_SIZE + top_surface.get_height()))

    # Update the screen so we can actually see the changes
    pygame.display.update()


def generatePlot(board_with_probabilities, board_with_hits_misses, turn_count):
    global PLOT_DISPLAY

    if PLOT_DISPLAY == 0:
        display_plot(board_with_hits_misses, turn_count, "Hits/Misses", False)
    else:
        display_plot(board_with_probabilities, turn_count, "Probabilities", True)

    while True:

        # Loop over all new game events since last frame
        for event in pygame.event.get():
            # Check to see if user wants the application to close
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Exit so the AI computes and plays the next move
                if event.key == pygame.K_SPACE:
                    return
                # Toggle which map to display
                elif event.key == pygame.K_LSHIFT:
                    # Update which type of plot to draw
                    PLOT_DISPLAY = (PLOT_DISPLAY + 1) % 2

                    # Update the display
                    if PLOT_DISPLAY == 0:
                        display_plot(board_with_hits_misses, turn_count, "Hits/Misses", False)
                    else:
                        display_plot(board_with_probabilities, turn_count, "Probabilities", True)


def saveCSV(board_with_probabilities, turn_counter):
    name = "textfile" + str(turn_counter) + ".csv"
    np.savetxt(name, board_with_probabilities, delimiter=",")


def generateRandomBoard():
    opponents_board = np.full((10, 10), 0)
    ships = [5, 4, 3, 3, 2]

    for length_of_the_ship in ships:
        placed = False
        while placed == False:
            col_or_row = random.randint(0, 1)

            # row
            if col_or_row == 1:
                empty_slot_counter = 0
                random_row = random.randint(0, 9)
                random_col = random.randint(0, 9 - length_of_the_ship)

                for i in range(0, length_of_the_ship):
                    if opponents_board[random_row, random_col + i] == 0:
                        empty_slot_counter += 1

                if empty_slot_counter == length_of_the_ship:
                    for i in range(0, length_of_the_ship):
                        opponents_board[random_row, random_col + i] = 1
                    placed = True

            # col
            if col_or_row == 0:
                empty_slot_counter = 0
                random_col = random.randint(0, 9)
                random_row = random.randint(0, 9 - length_of_the_ship)

                for i in range(0, length_of_the_ship):
                    if opponents_board[random_row + i, random_col] == 0:
                        empty_slot_counter += 1

                if empty_slot_counter == length_of_the_ship:
                    for i in range(0, length_of_the_ship):
                        opponents_board[random_row + i, random_col] = 1
                    placed = True

    return (opponents_board)


def possibibleLocationsProbability(board_with_hits, board_with_misses, length_of_the_ship):
    list_of_probabilities = []

    # Check all rows for possible locations
    for row in range(0, 10):
        for col in range(0, 11 - length_of_the_ship):
            positions_to_consider = range(col, col + length_of_the_ship)
            # State where hits happened
            positions_with_hits = []
            empty_slot_counter = 0
            # Check if the elements of a list all correspond to 0s, and if they do create a matrix where that segment has a certain probabiliity
            for element in positions_to_consider:
                if board_with_misses[row, element] == 0:
                    if board_with_hits[row, element] == 1:
                        positions_with_hits.append(element)
                    empty_slot_counter += 1

            # Check if the number of continious empty slots corresponds to the length of the ship
            if empty_slot_counter == length_of_the_ship:
                new_state = np.full((10, 10), 0.0)
                if_there_is_hit = 4 * len(positions_with_hits) if len(positions_with_hits) else 1
                for element in positions_to_consider:
                    if element in positions_with_hits:
                        new_state[row, element] = 0
                    else:
                        new_state[row, element] = float(length_of_the_ship) * if_there_is_hit
                list_of_probabilities.append(new_state)

    # Check all cols for possible locations
    for col in range(0, 10):
        for row in range(0, 11 - length_of_the_ship):
            positions_to_consider = range(row, row + length_of_the_ship)
            positions_with_hits = []
            empty_slot_counter = 0

            # Check if the elements of a list all correspond to 0s, and if they do create a matrix where that segment has a certain probabiliity
            for element in positions_to_consider:
                if board_with_misses[element, col] == 0:
                    if board_with_hits[element, col] == 1:
                        positions_with_hits.append(element)
                    empty_slot_counter += 1

            # Check if the number of continious empty slots corresponds to the length of the ship
            if empty_slot_counter == length_of_the_ship:
                if_there_is_hit = 4 if len(positions_with_hits) else 1

                new_state = np.full((10, 10), 0.0)
                for element in positions_to_consider:
                    if element in positions_with_hits:
                        new_state[element, col] = 0
                    else:
                        new_state[element, col] = float(length_of_the_ship) * if_there_is_hit
                list_of_probabilities.append(new_state)

    final_matrix = np.full((10, 10), 0)
    for curr_matrix in list_of_probabilities:
        final_matrix = np.add(final_matrix, curr_matrix)

    return (final_matrix)


def generateProbabilitiesForAllShips(board_with_hits, board_with_misses):
    final = np.full((10, 10), 0)
    ships = [5, 4, 3, 3, 2]
    for i in ships:
        probabilites = possibibleLocationsProbability(board_with_hits, board_with_misses, i)
        final = np.add(final, probabilites)
    return (final)


def generateNextMove(board_with_probabilities):
    return (np.unravel_index(board_with_probabilities.argmax(), board_with_probabilities.shape))


def bot(opponents_board, board_with_hits, board_with_misses, turn_counter, successful_hits, do_display=False):
    board_with_probabilities = generateProbabilitiesForAllShips(board_with_hits, board_with_misses)

    if successful_hits >= 17 or turn_counter >= 100:
        if do_display:
            generatePlot(board_with_probabilities, board_with_hits + board_with_misses, turn_counter)
            # generatePlot((board_with_hits + board_with_misses), turn_counter + 100)
        return (turn_counter)

    nextHit = generateNextMove(board_with_probabilities)
    row = nextHit[0]
    col = nextHit[1]

    if do_display:
        # generatePlot(board_with_probabilities, turn_counter)
        # generatePlot((board_with_hits + board_with_misses), turn_counter + 100)
        generatePlot(board_with_probabilities, board_with_hits + board_with_misses, turn_counter)
        # saveCSV(board_with_probabilities, turn_counter)

    # if opponents_board[row, col] == 1:
    #     successful_hits += 1
    #     board_with_hits[row, col] = 1
    #     board_with_probabilities[row, col] = 0
    #
    # else:
    #     board_with_misses[row, col] = 2

    # return (bot(opponents_board, board_with_hits, board_with_misses, turn_counter + 1, successful_hits))
    return row, col

class Button:
    """Represents a simple button. Not very general, but its quick and works for this"""

    def __init__(self, rect):
        self.rect = rect
        self.text = "Human"
        self.text_surface = None
        self.text_rect = None

        self.render_text()

    def render_text(self):
        self.text_surface = DISPLAY_FONT.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = (
            self.rect.x + self.rect.w // 2,
            self.rect.y + self.rect.h // 2
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.text = "AI" if self.text == "Human" else "Human"
                self.render_text()

    def draw(self):
        pygame.draw.rect(
            SCREEN,
            (175, 175, 175),
            self.rect
        )
        pygame.draw.rect(
            SCREEN,
            (0, 0, 0),
            self.rect,
            2
        )
        SCREEN.blit(self.text_surface, self.text_rect)

    def create_player(self, player_num):
        if self.text == "Human":
            return HumanPlayer(player_num)
        else:
            return AIPlayer(player_num)


class HumanPlayer:
    def __init__(self, player_num):
        self.player_num = player_num

        self.board = np.full((10, 10), 0)

        self.generate_board(player_num)

    def is_valid_placement(self, potential_board, ship_length):
        if np.count_nonzero(potential_board == 1) != ship_length:
            return False

        # Find all coordinate of candidate locations
        x_pos = set()
        y_pos = set()
        for x in range(10):
            for y in range(10):
                if potential_board[y, x] == 1:
                    x_pos.add(x)
                    y_pos.add(y)

        x_pos = sorted(list(x_pos))
        y_pos = sorted(list(y_pos))

        # Check that those locations are possible
        # 2 correct options. Everything else means return false
        if len(x_pos) == 1 and len(y_pos) == ship_length:
            min_y_pos = min(y_pos)
            correct_range = list(range(min_y_pos, min_y_pos + ship_length))
            return y_pos == correct_range
        elif len(y_pos) == 1 and len(x_pos) == ship_length:
            min_x_pos = min(x_pos)
            correct_range = list(range(min_x_pos, min_x_pos + ship_length))
            return x_pos == correct_range
        else:
            return False

    def generate_board(self, player_num):
        def draw(current_ship_being_placed):
            display_plot(self.board, 0, "", False)

            pygame.draw.rect(
                SCREEN,
                (150, 150, 150),
                (0, SCREEN_SIZE, SCREEN_SIZE, SCREEN_SIZE)
            )

            top_text = f"Player {player_num}. Placing {current_ship_being_placed} long ship."
            top_surface = DISPLAY_FONT.render(top_text, True, (0, 0, 0))

            bot_text = "Click to place. Space to accept. C to clear."
            bot_surface = DISPLAY_FONT.render(bot_text, True, (0, 0, 0))

            SCREEN.blit(top_surface, (BORDER, SCREEN_SIZE))
            SCREEN.blit(bot_surface, (BORDER, SCREEN_SIZE + top_surface.get_height()))

            pygame.display.update()

        ships_left_to_place = [5, 4, 3, 3, 2]

        draw(ships_left_to_place[0])

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Clicked on the board check
                    if BORDER <= event.pos[0] < SCREEN_SIZE - BORDER and BORDER <= event.pos[1] < SCREEN_SIZE - BORDER:
                        x = (event.pos[0] - BORDER) // TILE_WIDTH
                        y = (event.pos[1] - BORDER) // TILE_WIDTH
                        if self.board[y, x] in {0, 1}:
                            self.board[y, x] = 1 if self.board[y, x] == 0 else 0

                        draw(ships_left_to_place[0])

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.board = np.full((10, 10), 0)
                        draw(ships_left_to_place[0])
                    elif event.key == pygame.K_SPACE:
                        if self.is_valid_placement(self.board, ships_left_to_place[0]):
                            self.board = np.where(self.board == 1, 2, self.board)
                            ships_left_to_place.pop(0)
                            if len(ships_left_to_place) == 0:
                                self.board = np.where(self.board == 2, 1, self.board)
                                return
                            draw(ships_left_to_place[0])

    def make_move(self, opponent_board, hits_misses, turn):
        def draw():
            display_plot(hits_misses, 0, "", False)

            pygame.draw.rect(
                SCREEN,
                (150, 150, 150),
                (0, SCREEN_SIZE, SCREEN_SIZE, SCREEN_SIZE)
            )

            top_text = f"Player {self.player_num}'s turn."
            top_surface = DISPLAY_FONT.render(top_text, True, (0, 0, 0))

            bot_text = f"Turn: {turn}. Click to play."
            bot_surface = DISPLAY_FONT.render(bot_text, True, (0, 0, 0))

            SCREEN.blit(top_surface, (BORDER, SCREEN_SIZE))
            SCREEN.blit(bot_surface, (BORDER, SCREEN_SIZE + top_surface.get_height()))

            pygame.display.update()

        draw()

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Clicked on the board check
                    if BORDER <= event.pos[0] < SCREEN_SIZE - BORDER and BORDER <= event.pos[1] < SCREEN_SIZE - BORDER:
                        x = (event.pos[0] - BORDER) // TILE_WIDTH
                        y = (event.pos[1] - BORDER) // TILE_WIDTH
                        if hits_misses[y, x] == 0:
                            if opponent_board[y, x] == 1:
                                hits_misses[y, x] = 1
                            else:
                                hits_misses[y, x] = 2
                            return


class AIPlayer:
    def __init__(self, player_num):
        self.player_num = player_num
        self.board = generateRandomBoard()

    def make_move(self, opponent_board, hits_misses, turn):
        hits = np.where(hits_misses==2, 0, hits_misses)
        misses = np.where(hits_misses==1, 0, hits_misses)
        row, col = bot(opponent_board, hits, misses, turn, 0)
        if opponent_board[row, col] == 1:
            hits_misses[row, col] = 1
        else:
            hits_misses[row, col] = 2


class MainScene:
    def __init__(self):
        self.player_1_text = DISPLAY_FONT.render("Player 1", True, (0, 0, 0))
        self.player_2_text = DISPLAY_FONT.render("Player 2", True, (0, 0, 0))

        button_y = BORDER + self.player_1_text.get_height()
        button_width = (SCREEN_SIZE - BORDER * 3) // 2
        button_height = SCREEN_SIZE // 2 - BORDER * 2 - self.player_1_text.get_height()

        self.player_1_button = Button(pygame.Rect(BORDER, button_y, button_width, button_height))
        self.player_2_button = Button(pygame.Rect(BORDER * 2 + button_width, button_y, button_width, button_height))

        self.instructions_1_text = DISPLAY_FONT.render("Left click to toggle player types.", True, (0, 0, 0))
        self.instructions_2_text = DISPLAY_FONT.render("Space to start the game.", True, (0, 0, 0))

    def handle_event(self, event):
        self.player_1_button.handle_event(event)
        self.player_2_button.handle_event(event)

    def draw_player_selection(self):
        SCREEN.fill((150, 150, 150))

        SCREEN.blit(self.player_1_text, (self.player_1_button.rect.x, BORDER // 2))
        SCREEN.blit(self.player_2_text, (self.player_2_button.rect.x, BORDER // 2))

        self.player_1_button.draw()
        self.player_2_button.draw()

        SCREEN.blit(self.instructions_1_text, (BORDER, SCREEN_SIZE / 2))
        SCREEN.blit(self.instructions_2_text, (BORDER, SCREEN_SIZE / 2 + 50))

        pygame.display.update()

    def run_player_selection(self):

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        p1 = self.player_1_button.create_player(1)
                        p2 = self.player_2_button.create_player(2)
                        self.run_game(p1, p2)
                        return

                self.player_1_button.handle_event(event)
                self.player_2_button.handle_event(event)

            self.draw_player_selection()

    @staticmethod
    def is_board_solved(board):
        return np.count_nonzero(board == 1) == sum([5, 4, 3, 3, 2])

    @staticmethod
    def display_unsolved_board(board, turn, title, opponent_num):
        def draw():
            display_plot(board, turn, title, False)

            pygame.draw.rect(
                SCREEN,
                (150, 150, 150),
                (0, SCREEN_SIZE, SCREEN_SIZE, SCREEN_SIZE)
            )

            top_text = title
            top_surface = DISPLAY_FONT.render(top_text, True, (0, 0, 0))

            bot_text = "Space to continue"
            bot_surface = DISPLAY_FONT.render(bot_text, True, (0, 0, 0))

            SCREEN.blit(top_surface, (BORDER, SCREEN_SIZE))
            SCREEN.blit(bot_surface, (BORDER, SCREEN_SIZE + top_surface.get_height()))

            pygame.display.update()

        draw()

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return

    @staticmethod
    def display_win(winner_num, winner_hits_misses, loser_hits_misses, winner_board):
        def draw(board, title):
            display_plot(board, 0, "", False)

            pygame.draw.rect(
                SCREEN,
                (150, 150, 150),
                (0, SCREEN_SIZE, SCREEN_SIZE, SCREEN_SIZE)
            )

            top_text = title
            top_surface = DISPLAY_FONT.render(top_text, True, (0, 0, 0))

            bot_text = "Space to continue"
            bot_surface = DISPLAY_FONT.render(bot_text, True, (0, 0, 0))

            SCREEN.blit(top_surface, (BORDER, SCREEN_SIZE))
            SCREEN.blit(bot_surface, (BORDER, SCREEN_SIZE + top_surface.get_height()))

            pygame.display.update()

        loser_num = 1 if winner_num == 2 else 2

        draw(winner_hits_misses, f"Player {winner_num} won! Player {loser_num}'s board.")

        quit = False
        while not quit:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        quit = True

        # Solve the winners board for the loser
        for y in range(10):
            for x in range(10):
                if winner_board[y, x] == 1:
                    loser_hits_misses[y, x] = 1

        draw(loser_hits_misses, f"Player {loser_num} lost. Player {winner_num}'s board.")

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return

    def run_game(self, player_1, player_2):
        player_1_hits_misses = np.full((10, 10), 0)
        player_2_hits_misses = np.full((10, 10), 0)

        turn = 1

        while True:

            # Player 1
            player_1.make_move(player_2.board, player_1_hits_misses, turn)

            self.display_unsolved_board(player_1_hits_misses, turn, "Player 1 Hits and Misses.", 2)

            if self.is_board_solved(player_1_hits_misses):
                self.display_win(1, player_1_hits_misses, player_2_hits_misses, player_1.board)
                return

            # Player 2
            player_2.make_move(player_1.board, player_2_hits_misses, turn)

            self.display_unsolved_board(player_2_hits_misses, turn, "Player 2 Hits and Misses.", 1)

            if self.is_board_solved(player_2_hits_misses):
                self.display_win(2, player_2_hits_misses, player_1_hits_misses, player_2.board)
                return

            turn += 1


if __name__ == '__main__':
    MainScene().run_player_selection()
