"""The leader's CHA and shop prices (game.RULE_CHA_PRICES; DSCLOG's RULE_HI_CHA_PRICES, CHA_PRICE,
PROBE_PRICE, PROBE_PRICE_EAX, SELL_PRICE): buying costs less for the party leader's CHA, and
selling pays 60% of an item's price (the game pays all of it, which with the discount would let
anything bought be sold at a profit). The game's own prices take no account of CHA."""

NOT_FOR_SALE = 9999  # (the game's price for what a shop won't deal in)
CHA_FIRST, CHA_LAST = 18, 25  # (5% off at CHA 18, 5% more for each point to 40% at 25)


def discount(cha: int) -> int:
    """The percentage off a shop's price for a leader of CHA."""
    return 5 * min(max(cha - CHA_FIRST + 1, 0), CHA_LAST - CHA_FIRST + 1)


SELL_PERCENT = 60  # (what shops pay of an item's price: 100 less the best discount, 40%)


def sell_price(value: int) -> int:
    """What a shop pays for an item of price VALUE (DSCLOG's SELL_PRICE): 60%, rounded down, never
    below 1, so that nothing bought at the leader's best discount (40% off) sells for more than it
    cost; at CHA 25 a round trip comes out even."""
    if value in (0, NOT_FOR_SALE):
        return value
    return max(1, value * SELL_PERCENT // 100)


def price(value: int, cha: int) -> int:
    """What a shop asks for an item of price VALUE from a leader of CHA (never below 1)."""
    if value in (0, NOT_FOR_SALE):
        return value
    return max(1, value * (100 - discount(cha)) // 100)
