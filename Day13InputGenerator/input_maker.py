import pygame
import numpy as np
import os
from random import random

LOCAL_DIR = os.path.dirname(__file__)
FONT_ADDRESS = os.path.join(LOCAL_DIR, "Fonts/dogica.ttf")

FONT_HEIGHT = 8
pygame.font.init()

def grey(n):
    return n, n, n

def fold_prompt():
    folds = input("Please input the number of folds: ")
    while not folds.isdigit():
        print("The number of folds needs to be an integer.")
        folds = input("Please input the number of folds: ")
    return int(folds)

def text_prompt():
    text = input("Please input the requested text: ")
    while not text.replace(" ", "").isalpha():
        print("Only letters allowed.")
        text = input("Please select the number of folds: ")
    return text

def reselect_prompt(f, t):
    def display_prompt():
        print(f"(1) Folds: {f}")
        print(f"(2) Text: {t}")
        print(f"(3) Continue?")
        return input("Selection: ")
    option = display_prompt()

    while True:
        if not option.isdigit():
            print("Selection needs to be an integer.")
            option = display_prompt()
            continue
        elif not (1 <= int(option) <= 3):
            print("The selection needs to be between 1 and 3.")
            option = display_prompt()
            continue
        else:
            break

    return int(option)

def get_char_dots(t):
    def remove_blank_edges(array):
        """Remove all blank borders"""
        idx = np.argwhere(np.all(array[0,:,:][..., :] == 255, axis=0))
        array = np.delete(array, idx, axis=2)
        
        idx = np.argwhere(np.all(array[0,:,:][:, ...] == 255, axis=1))
        array = np.delete(array, idx, axis=1)

        return array

    font = pygame.font.Font(FONT_ADDRESS, FONT_HEIGHT)
    char_dots = dict()
    for char in set(t):
        if char == " ": continue
        surf = font.render(char, False, grey(0))

        array = pygame.surfarray.array3d(surf).T
        array = remove_blank_edges(array).T

        dots = set()
        for y in range(array.shape[1]):
            for x in range(array.shape[0]):
                if np.any(array[x, y, :] == 0):
                    dots.add((x, y))

        char_dots[char] = dots
    
    return char_dots

def generate_initial_paper(char_dots, t):
    initial_dots = set()
    dx = 0
    for char in t:
        if char == " ":
            dx += 2
            continue
        new_dots = char_dots[char]
        max_x = max(x for x,y in new_dots)
        for x, y in new_dots:
            initial_dots.add((x+dx, y))
        dx += max_x + 2
    return initial_dots

def unfold_paper(dots, fold_count):
    """
    Return:
    1. The set of dots that make up the puzzle input
    2. The folds that the puzzle solver have to make in order.
         Not reversed order AKA the order my input maker unfolds.
    """
    folds = []
    for _ in range(fold_count):
        max_x = max(x for x,y in dots)
        max_y = max(y for x,y in dots)
        if max_x > max_y:
            var = "y"
            n = max_y + 1
        else:
            var = "x"
            n = max_x + 1

        folds.append((var, n))

        new_dots = set()
        for x, y in dots:
            old = (x, y)
            if var == "y":
                dy = abs(n - y)
                new = (x, n + dy)
            else:
                dx = abs(n - x)
                new = (n + dx, y)

            r = random()
            if r < 2/3:
                new_dots.add(new)
            if r > 1/3:
                new_dots.add(old)

        dots = new_dots

    return dots, reversed(folds)

def main():

    f = fold_prompt()
    t = text_prompt()
    t = t.upper()

    r = reselect_prompt(f, t)
    while r != 3:
        if r == 1:
            f = fold_prompt()
        elif r == 2:
            t = text_prompt()
            t = t.upper()
            
        r = reselect_prompt(f, t)

    print(f"Folds: {f}")
    print(f"Text: {t}")

    char_dots_map = get_char_dots(t)

    initial_dots = generate_initial_paper(char_dots_map, t)

    result_dots, folds = unfold_paper(initial_dots, f)

    filename = f"Output/{t}.txt"
    address = os.path.join(LOCAL_DIR, filename)
    with open(address, "w") as outfile:
        for x, y in result_dots:
            print(f"{x},{y}", file=outfile)

        print("", file=outfile)

        for var, n in folds:
            print(f"fold along {var}={n}", file=outfile)
        

if __name__ == "__main__":
    main()