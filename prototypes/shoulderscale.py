"""Place painted rows of a shoulder scale at the pin on the fitted figure."""


def scale_pixels(pin, outside, first_y, strips):
    x, y = pin
    return {(x + outside*(start+i), y+first_y+row): int(tone)
            for row, (start, tones) in enumerate(strips)
            for i, tone in enumerate(tones)}
