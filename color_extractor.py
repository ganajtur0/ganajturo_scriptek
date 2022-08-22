#!/usr/bin/python3

import colorgram
import argparse

RESET = '\033[0m'

def get_color_escape(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)

def display_colors(colors):

    color_strings = []

    for color in colors:
        hex_r = hex(color.rgb.r)[-2:]
        hex_g = hex(color.rgb.g)[-2:]
        hex_b = hex(color.rgb.b)[-2:]

        bg_color_escape = get_color_escape(color.rgb.r,color.rgb.g,color.rgb.b,True)
        fg_color_escape = get_color_escape(255 - color.rgb.r, 255 - color.rgb.g, 255 - color.rgb.b)

        color_strings.append( ("{:4}% " + fg_color_escape + bg_color_escape + "#{}{}{}" + RESET).format(int(color.proportion*100),hex_r,hex_g,hex_b) )

    print('\n'.join(color_strings))

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to extract colors from.")
    parser.add_argument("--colors", help="Number of colors to extract", type=int)
    args = parser.parse_args()

    colors = 4
    if args.colors:
        colors = colorgram.extract(args.image, args.colors)
        display_colors(colors)

if __name__ == '__main__':
    main()
