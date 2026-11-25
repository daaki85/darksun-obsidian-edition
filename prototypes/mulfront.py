"""Front-facing Mul garments, drawn in the palette of the map figures."""

import mulstudy as fit

# Each row is drawn at one game pixel per character. A space is exposed
# body or air. The ochre fabric (a–h), moss (A–G), slate (1–9) and leather
# share shadow colours; broad clusters and single turned edges follow the
# lighting on the retail Warrior and Thief.
INK = dict(zip("abcdefghABCDEFG123456789xy",
               (204,205,95,97,99,168,169,170,17,69,188,53,189,54,55,
                208,17,18,20,22,23,25,26,28,89,96)))

# Match the lighting of exposed thighs when they carry dark leather breeches.
LEATHER = {254: 88, 129: 88, 128: 89, 135: 90, 136: 91, 137: 92,
           138: 93, 139: 205, 140: 94, 141: 95, 142: 96, 143: 97,
           151: 98, 152: 99}

# The strip ends are seams and hems at native resolution. The advancing
# knee pushes up a different side of the wrap on the two passing steps.
# The cloak gathers on the near shoulder and folds behind the swinging arm.
FRONT = {
    # Front idle. Weight on the near leg, far knee bent.
    0: ((4, 6), (
        "  FG", " EGFDC      c", " FGFEF     dy",
        " DCEGFD   ebb", "  DCDFGFDbcb", "  BDCFEGCBd",
        "   CDFEDbdef", "   CEFbcdfb", "   xyyxxbab",
        "  acefgfedcb", "  bdeghgfdcba", "  bdefgfcbdefb",
        "  cdfgfcbaefb", "  ceggfc  ac", "  dfgec",
        "  cfdc", "   cb",
    ), (
        "  685     45", " 78675    463", " 675487  5742",
        " 56455788762", "  4534678642", "  3467865432", "   58765432",
        "   6543xx52", "   54xyx432", "  5754323452", "  65434345642",
        "  76432 23542", "  6532   3432", "  542     32", "  32       2",
        "  2",
    )),
    # First step. The forward hip gathers the pleat on the left.
    3: ((3, 6), (
        "  EF", " FGFED      c", " EGEFD     dy",
        " DFEGCDF  eb", "  BDFGEFCbb", "  CEGFDCbdb",
        "  BDFEBdefb", "  CEBcdefdb", "  xyxxbbaby",
        "  bdghgfcba", "  afghgfedb", "  cghgfcbdda",
        "  dghgcbbda", "   ghfca b", "   fgfb",
        "   dec", "   cb",
    ), (
        "  676     34", " 78674    562", " 87546   5652", " 67435787654",
        "  6456787652", "  4578765452", "  578654342", "  67543xxy2",
        "  653xxy432", "  575432452", "  6753235642", "  76432 4542",
        "  6532  342", "   532   32", "   42", "   2",
    )),
    # Second step. The left forearm swings across the waist. The short
    # side rides over the raised left knee while the right pleat hangs.
    4: ((3, 6), (
        "  ED", " DEGF     c", " CDFEF   dy",
        "  BDEFC ebb", "  CDFEFDCcb", "   BDFGFbd",
        "   CDFEBdb", "  BCDBcded", "  xyxxxybb",
        "  bdfecefdb", "  dgecbdfgcb", "   fdcadfhfb",
        "   dc  bghfc", "        fgdc", "        efb",
        "        cb",
    ), (
        "  65     34", " 5765    465", " 65767  35642", "  6456778652",
        "  4345677652", "   34678764", "   45786543", "  3567xx452",
        "  54xxy5432", "  6432345652", "  532 345675", "  42   45674",
        "  2    34562", "        3542", "        242", "         2",
    )),
    # Third step. The torso rises and the wrap swings around the right hip.
    5: ((3, 5), (
        "  DFE", " DEGF        c", " EFGFE     dy",
        " CDFGFD   ebc", "  CDFEFDCbb", "  BDEFGFDBb",
        "  CEFDEbcdb", "  CEBCdefdb", "  xyxxxybba",
        "  cdefcegfb", "  defcbefgfc", "  cfecbdfghfb",
        "   dcb adghfc", "    b  bcgfdb", "        dgfcb",
        "        efdb", "        dcb", "        b",
    ), (
        "  567       3", " 56786     453", " 786756   5642", " 654578  6752",
        "  4356788752", "  3467886542", "  457865432", "  56754xx42",
        "  643xxy432", "  6523234562", "  542  456752", "  32   345675",
        "  2     34564", "        34562", "         542", "         32", "         2",
    )),
    # Fourth step. The other arm comes forward, the left panel opens
    # with the leading thigh, and the cloth is pulled taut near the belt.
    6: ((3, 6), (
        "  EFD", " DEGF      c", " DFGFE    dy",
        "  DFEFDC ebc", "  BDFGFEBCb", "   CEGFBCdb",
        "   BEFBcedb", "  BDECdefdb", "  xyxxbyxxb",
        "  bdefggfdb", "  cdfghgecb", "  cdfhhfcba",
        "  dfghfc  b", "  cghgeb", "   fgec",
        "   efb", "    b",
    ), (
        "  675     34", " 67865    563", " 765457  6752", "  6544678762",
        "  5435678642", "   45787652", "   67865432", "  567543xx2",
        "  675xxy432", "  765432452", "  687543452", "  76542 352",
        "  6752   42", "  5642", "  452", "   32", "   2",
    )),
    # The middle strike compresses the distance from the throat to the
    # leading knee. The forearm crosses above the shortened front folds.
    16: ((6, 6), (
        "  EF", "  GFE      c", "  EFGC    dy",
        " BDEGFD  eb", " BDFGFEBCb", " BDEFCbedc",
        " xyxxbbabd", " cdfggfedba", " cfghgfc ab",
        " dfggfc", " cgecb", "  dcb",
    ), (
        "  58      45", "  786    564", "  6756  67542", " 34567887652",
        "  457876542", " 56765xx432", " 654xx23452", " 76543 3452",
        " 6542   342", " 532     32", " 32", " 2",
    )),
}
# In the front wind-up, follow-through and bow the torso turns almost
# side-on. These pieces are painted at native resolution around the crossing
# arm; the first coordinate is the top left of the drawing in the retail cel.
TURNS = {
    15: ((0,7), (
        "      EFCC", "     FGECD", "    GGFDEC", "   CEFGBed", "  BDEFBefd",
        "  BEFCegfd", " CDEBcegfd", " BDDccdeec", " BCBxxyxxb", "   adfggec",
        "   abefghec", "   abdefgdc", "   acdefec", "    bdfecb", "    acdb",
    ), (
        "      6752", "     78654", "    678653", "   4567854", "  34567542",
        " 346754433", " 256743344", " 245624342", "14563xxyx2", "1354245532",
        "234323442", "122  3432", " 2    22",
    )),
    17: ((6,6), (
        "    DC", "    FECC", "   EGFECB", "    FGFDEB", "    CEFGECB",
        "   cdeBEFCB", "  bdefgDCB", "  xxyyxxc", " acefggfc", " bdefheca",
        " bdefgdb", "  bcdba",
    ), (
        "    454", "    7764", "   687653", "    578653", "    2467853",
        "   342345762", "  45xxx457632", " 453232 45632", " 34232   4532",
        "  232     321", "   2",
    )),
    24: ((1,5), (
        "   CE   B", "   GFD CB", "  EGFDEFC", "  DFEGECB", "  CEGBddb", "  BEFcedd",
        "  BDEbefd", "  CDBegfc", "  CBcegfb", "  bxxxyxx", "  adffgeca",
        "  abefghfc", "  acdfggfc", "  acdefgdc", "   bdeefc", "   abddc",
    ), (
        "   56  3", "   784 52", "  6877652", "  5778653", "  4676652", "  3565423",
        "  4565432", "  5674332", "  4674232", "  465xxyx", "  5642342", "  45322342",
        "  3432 232", "  32    22", "  2",
    )),
}

# A rolled rim grips the temple and clears the entire cheek. The first
# two rows share the scalp height; the shade at one temple turns into the
# short collar instead of continuing down to the hem.
COWL = (
    "   57752  ", "  6876532 ", " 675    32", " 45     32", " 34     23",
    " 245    43", "  356  542", "   34  32 ",
)


def mark(picture, x, y):
    if 0 <= y < len(picture) and 0 <= x < len(picture[y]):
        return INK.get(picture[y][x])
    return None


def dress(pose, body, protected, hands, bow, hood):
    druid, thief = ([row[:] for row in body] for _ in range(2))
    hx, hy, spans = fit.HEADS[pose]
    head = fit.head_pixels(pose, len(body[0])-2*fit.PAD, len(body))
    waist, wl, wr = fit.ROBE_CUTS[pose][2]
    knee = fit.HIDE_POINTS[pose][3]
    (left, top), drows, trows = FRONT[pose] if pose in FRONT else TURNS[pose]
    for y, row in enumerate(body):
        for u, skin in enumerate(row):
            x = u-fit.PAD
            pt = x,y
            if pt in bow or (skin is not None and pt in hands):
                continue
            if pt not in protected:
                d = mark(drows, x-left, y-top)
                t = mark(trows, x-left, y-top)
                if d is not None:
                    druid[y][u] = d
                # The leather breeches remain visible in
                # the opening. Keep the separate leg silhouettes and bare feet.
                near_elbow = pose == 17 and pt == (6, 14)
                if skin in LEATHER and waist <= y <= knee+1 and wl-3 <= x <= wr+3 and not near_elbow:
                    # Deep leather at the knees separates them from the loose
                    # slate fold that swings over the tunic.
                    thief[y][u] = LEATHER[skin]
                if t is not None:
                    thief[y][u] = t
            if pose in FRONT:
                c = mark(COWL, x-hx+1, y-hy)
                if c is None and pt in head and y-hy < 3:
                    # Carry the crown over the bald scalp to its shaded brim.
                    c = (25, 20, 17)[y-hy]
                if c is not None and (pt not in head or y-hy < 3):
                    thief[y][u] = c
            elif pt in hood and (pt not in head or y-hy < 3):
                k = min(len(spans)-1,max(0,y-hy))
                a,b = spans[k]
                side = (x-hx-a)/max(1,b-a)
                ramp = (17,18,19,20,21,22,49,23,24,25,50,26)
                value = 9.5-7*abs(side-.31)-.6*k
                thief[y][u] = ramp[max(0,min(len(ramp)-1,round(value)))]
    return {"Druid": druid, "Thief": thief}
