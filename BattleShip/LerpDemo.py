import pygame

pygame.display.set_caption("Linear Interpolation Demo")

# Dimensions
SCREEN_SIZE = 500
SCREEN = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

# Color
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Font
pygame.font.init()
DISPLAY_FONT = pygame.font.SysFont("Arial", 30)


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


def lerp_color_in_rgb(rgb_a, rgb_b, t):
    return tuple(
        int(rgb_a[i] * (1 - t) + rgb_b[i] * t)
        for i in range(3)
    )


def lerp_color_in_hsv(rgb_a, rgb_b, t):
    hsv_a = rgb_to_hsv(rgb_a)
    hsv_b = rgb_to_hsv(rgb_b)

    hsv_new = tuple(
        int(hsv_a[i] * (1 - t) + hsv_b[i] * t)
        for i in range(3)
    )

    return hsv_to_rgb(hsv_new)


def draw_screen(color_space, x, lerp_func):
    SCREEN.fill((150, 150, 150))

    # Top section for current lerp selection
    pygame.draw.rect(
        SCREEN,
        lerp_func(RED, GREEN, x / SCREEN_SIZE),
        (0, 0, SCREEN_SIZE, SCREEN_SIZE // 3)
    )

    # Draw bottom section
    SCREEN.blit(
        DISPLAY_FONT.render(f"Color Space: {color_space}", True, (0, 0, 0)),
        (20, SCREEN_SIZE * 8 / 12)
    )
    SCREEN.blit(
        DISPLAY_FONT.render(f"Selected t%: {round(100 * x / SCREEN_SIZE, 1)}%", True, (0, 0, 0)),
        (SCREEN_SIZE * 1 / 2, SCREEN_SIZE * 8 / 12)
    )

    SCREEN.blit(
        DISPLAY_FONT.render(f"Selected Color: {lerp_func(RED, GREEN, x / SCREEN_SIZE)}", True, (0, 0, 0)),
        (20, SCREEN_SIZE * 9 / 12)
    )

    SCREEN.blit(
        DISPLAY_FONT.render("Left Shift to change color space.", True, (0, 0, 0)),
        (20, SCREEN_SIZE * 10 / 12)
    )

    SCREEN.blit(
        DISPLAY_FONT.render("Left Mouse to change selection.", True, (0, 0, 0)),
        (20, SCREEN_SIZE * 11 / 12)
    )

    # Draw middle section
    # This is overwriting the input parameter but it doesnt matter
    for x in range(SCREEN_SIZE):
        pygame.draw.rect(
            SCREEN,
            lerp_func(RED, GREEN, x / SCREEN_SIZE),
            (x, SCREEN_SIZE // 3, SCREEN_SIZE, SCREEN_SIZE // 3)
        )

    pygame.display.update()


def main():
    # color space lerp functions
    lerp_functions = [
        ("RGB", lerp_color_in_rgb),
        ("HSV", lerp_color_in_hsv)
    ]

    # Initial conditions
    current_x = SCREEN_SIZE // 2
    current_color_space_index = 0

    # Preliminary draw so it isnt a black screen on startup
    draw_screen(lerp_functions[current_color_space_index][0], current_x, lerp_functions[current_color_space_index][1])

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Change the color space
                if event.key == pygame.K_LSHIFT:
                    current_color_space_index = (current_color_space_index + 1) % len(lerp_functions)
                    draw_screen(lerp_functions[current_color_space_index][0], current_x,
                                lerp_functions[current_color_space_index][1])

            elif event.type in {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP}:
                # Change the selected x position
                current_x = event.pos[0]
                draw_screen(lerp_functions[current_color_space_index][0], current_x,
                            lerp_functions[current_color_space_index][1])

            # Only select based on mouse motion if the mouse is held
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    # Change the selected x position
                    current_x = event.pos[0]
                    draw_screen(lerp_functions[current_color_space_index][0], current_x,
                                lerp_functions[current_color_space_index][1])


if __name__ == '__main__':
    main()
