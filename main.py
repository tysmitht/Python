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
COLOR_A = (255, 0, 0) # In this case red
COLOR_B = (0, 255, 0) # In this case green

# Font
pygame.font.init()
DISPLAY_FONT = pygame.font.SysFont("Arial", 30)

# Which plot should be display currently
PLOT_DISPLAY = 0 # 0 --> HitsMisses; 1 --> Probabilities


def generatePlot(board_with_probabilities, board_with_hits_misses, turn_count):
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
            # Just draw all tiles the same color. Dont do any tweening
            if max_val == min_val:
                t_calculator_func = lambda mini, maxi, value: .5
            else:
                t_calculator_func = lambda mini, maxi, value: (value - mini) / (maxi - mini)
        else:
            t_calculator_func = lambda mini, maxi, value: (.5, 1, 0)[round(value)]

        for x in range(10):
            for y in range(10):
                val = matrix[y, x]
                color = lerp_color_in_hsv(
                    COLOR_A,
                    COLOR_B,
                    t_calculator_func(min_val, max_val, val)
                )

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

        top_text = f"{title}. Turn: {turn_count}. Space for next turn."
        top_surface = DISPLAY_FONT.render(top_text, True, (0, 0, 0))

        bot_text = "ESC to exit. Left Shift to switch plots."
        bot_surface = DISPLAY_FONT.render(bot_text, True, (0, 0, 0))

        SCREEN.blit(top_surface, (BORDER, SCREEN_SIZE))
        SCREEN.blit(bot_surface, (BORDER, SCREEN_SIZE + top_surface.get_height()))

        pygame.display.update()

    global PLOT_DISPLAY

    if PLOT_DISPLAY == 0:
        display_plot(board_with_hits_misses, turn_count, "Hits/Misses", False)
    else:
        display_plot(board_with_probabilities, turn_count, "Probabilities", True)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
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


def bot(opponents_board, board_with_hits, board_with_misses, turn_counter, successful_hits):
    board_with_probabilities = generateProbabilitiesForAllShips(board_with_hits, board_with_misses)

    if successful_hits >= 17 or turn_counter >= 100:
        generatePlot(board_with_probabilities, board_with_hits + board_with_misses, turn_counter)
        # generatePlot((board_with_hits + board_with_misses), turn_counter + 100)
        return (turn_counter)

    nextHit = generateNextMove(board_with_probabilities)
    row = nextHit[0]
    col = nextHit[1]
    # generatePlot(board_with_probabilities, turn_counter)
    # generatePlot((board_with_hits + board_with_misses), turn_counter + 100)

    generatePlot(board_with_probabilities, board_with_hits + board_with_misses, turn_counter)
    # saveCSV(board_with_probabilities, turn_counter)

    if opponents_board[row, col] == 1:
        successful_hits += 1
        board_with_hits[row, col] = 1
        board_with_probabilities[row, col] = 0

    else:
        board_with_misses[row, col] = 2

    return (bot(opponents_board, board_with_hits, board_with_misses, turn_counter + 1, successful_hits))


final_sum = 0
opponents_board = generateRandomBoard()
board_with_probabilities = np.zeros((10, 10))
board_with_hits = np.zeros((10, 10))
board_with_misses = np.zeros((10, 10))
final_sum += bot(opponents_board, board_with_hits, board_with_misses, 0, 0)
# generateProbabilitiesForAllShips(board_with_hits, board_with_misses)
# print(final_sum/100)
# plt.imshow(board_with_probabilities, cmap='hot')
# plt.show()