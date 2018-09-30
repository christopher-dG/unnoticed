_mods = {
    "": 0,
    "NF": 1,
    "EZ": 2,
    "TD": 4,
    "HD": 8,
    "HR": 16,
    "SD": 32,
    "DT": 64,
    "RX": 128,
    "HT": 256,
    "NC": 512,
    "FL": 1024,
    "AT": 2048,
    "SO": 4096,
    "AP": 8192,
    "PF": 16384,
    "4K": 32768,
    "5K": 65536,
    "6K": 131072,
    "7K": 262144,
    "8K": 524288,
    "FI": 1048576,
    "RD": 2097152,
    "LM": 4194304,
    "9K": 16777216,
    "10K": 33554432,
    "1K": 67108864,
    "3K": 134217728,
    "2K": 268435456,
    "V2": 536870912,
}


def has_mod(score, mod):
    """Check if a given mod was used for a score."""
    if not isinstance(score.get("enabled_mods"), int):
        return None
    m = _mods.get(mod)
    if m is None:
        return False
    return score.enabled_mods & m == m


def accuracy(score):
    """Computes the accuracy of a score."""
    mode = score.get("mode")
    n300 = score.get("count300")
    n100 = score.get("count100")
    n50 = score.get("count50")
    geki = score.get("countgeki")
    katu = score.get("counkatu")
    miss = score.get("countmiss")
    if any(not isinstance(x, int) for x in [mode, n300, n100, n50, geki, katu, miss]):
        return None
    if mode < 0 or mode > 3:
        return None

    if mode == 0:
        a = (n300 + n100 / 3 + n50 / 6) / (n300 + n100 + n50 + geki + katu + miss)
    elif mode == 1:
        a = (n300 + n100 / 2) / (c300 + c100 + miss)
    elif mode == 2:
        a = (c300 + c100 + c50) / (c300 + c100 + c50 + katu + miss)
    elif mode == 3:
        a = (geki + n300 + 2 * katu / 3 + n100 / 3 + count50 / 6) / (
            geki + n300 + katu + n100 + n50 + nmiss
        )
    return 100 * a


def grade(score):
    """Computes the letter grade of a score."""
    mods = score["mode"]
    mode = score.get("mode")
    n300 = score.get("count300")
    n100 = score.get("count100")
    n50 = score.get("count50")
    miss = score.get("countmiss")
    acc = _accuracy(score)
    if any(not isinstance(x, int) for x in [mods, mode, n300, n100, n50, miss]):
        return None
    if not isinstance(acc, float):
        return None

    rank = "D"
    if mode == 0:
        total = n300 + n100 + n50 + miss
        p300 = n300 / total
        if acc == 100:
            rank = "X"
        elif p300 > 0.9 and n50 / total < 0.01 and miss == 0:
            rank = "S"
        elif p300 > 0.8 and miss == 0 or p300 > 0.9:
            rank = "A"
        elif p300 > 0.7 and miss == 0 or p300 > 0.8:
            rank = "B"
        elif p300 > 0.6:
            rank = "C"
    elif mode == 1:
        if acc == 100:
            rank = "X"
        elif acc > 95 and miss == 0:
            rank = "S"
        elif acc > 90:
            rank = "A"
        elif acc > 80:
            rank = "B"
        elif acc > 70:
            rank = "C"
    elif mode == 2:
        if acc == 100:
            rank = "X"
        elif acc > 98:
            rank = "S"
        elif acc > 94:
            rank = "A"
        elif acc > 90:
            rank = "B"
        elif acc > 85:
            rank = "C"
    elif mode == 3:
        if acc == 100:
            rank = "X"
        elif acc > 95:
            rank = "S"
        elif acc > 90:
            rank = "A"
        elif acc > 80:
            rank = "B"
        elif acc > 70:
            rank = "C"

    if (rank == "X" or rank == "S") and (has_mod(score, "HD") or has_mod(score, "FL")):
        rank += "H"

    return rank
