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
# The cloak gathers on the near shoulder. Its single lit fold descends
# toward the waist, leaving the far chest in the shadow of the cowl.
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
        "  765     33", " 67544    432", " 574543  3432",
        " 46543454432", "  5745454332", "  6544543432",
        "   64544332", "   5643xy42", "   54yx3252",
        "  5654323542", "  46534323542", "  35432  3452",
        "   432    32", "   32",
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
        "  765     33", " 67544    432", " 57454   3432",
        " 46543454332", "  5645443432", "  6744544332",
        "  564544332", "  64543xy42", "  65xyx3432",
        "  565432452", "  6764323542", "  465432 342",
        "   3542   32", "   242",
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
        "  76     33", " 6754    432", " 56454  34332",
        "  6544354432", "  5645453432", "   67445432",
        "   56454432", "  3564xy432", "  54xxy5432",
        "  6432345652", "   42 345675", "    2  35674",
        "       24562", "        342", "         2",
    )),
    # Third step. The torso rises and the wrap swings around the right hip.
    5: ((3, 5), (
        "   DE", "  EFG        b", " EFdFD      ec",
        " DFGEFD   fed", "  CDFGECdefb", "  BECFGDCed",
        "  BDFEGFBcb", "  CdBcEDGDC", "  dycecbCCB",
        "  bdgfecbxx", "  adghegdbc", "  bcghgfedcb",
        "   bfgefdecba", "    cbdfgfdb", "      acdec",
        "        cb",
    ), (
        "  765       3", " 67544     432", " 564544   3432",
        " 654435  4332", "  6454454332", "  5745443432",
        "  654454432", "   5643xy32", "   54xy5432",
        "  654x34565", "  5532234574", "   343 457652",
        "    2  235642", "        2452", "          32",
    )),
    # Fourth step. The other arm comes forward, the left panel opens
    # with the leading thigh, and the cloth is pulled taut near the belt.
    6: ((3, 6), (
        "   ED", "  EGF      bc", " DGFE     dec",
        "  EGFDC  fed", "  DFEGFDcdb", "   BCEFGDCb",
        "   CBDGFEb", "   cdBCFDBC", "  cdyebCCB",
        "  cgfeccyb", "  dghgfdcb", "  beghgfedb",
        "  acdfgecba", "  bcdefcb", "   bcdb",
    ), (
        "  765     33", " 67544    432", " 564543  3432",
        "  6544345432", "  5645454332", "   67445432",
        "   56454432", "  465443xy2", "  675xxy432",
        "  765432454", "  687543342", "  76542  32",
        "   56423", "    5423", "     2",
    )),
    # The middle strike compresses the distance from the throat to the
    # leading knee. The forearm crosses above the shortened front folds.
    16: ((6, 6), (
        "  EF", "  GFE      c", "  EFGC    dy",
        " BDEGFD  eb", " BDFGFEBCb", " BDEFCbedc",
        " xyxxbbabd", " cdfggfedba", " cfghgfc ab",
        " dfggfc", " cgecb", "  dcb",
    ), (
        "  76      33", "  675    432", "  5645  34332", " 46544544332",
        "  564544332", " 65443xx432", " 654xx23452", " 76543 3452",
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
        "      7543", "     67543", "    574543", "   4654543", "  34564532",
        " 344564433", " 234654343", " 234564432", "14563xxyx2", "1354245532",
        "234323442", "122  3432", " 2    22",
    )),
    17: ((6,6), (
        "    DC", "    FECC", "   EGFECB", "    FGFDEB", "    CEFGECB",
        "   cdeBEFCB", "  bdefgDCB", "  xxyyxxc", " acefggfc", " bdefheca",
        " bdefgdb", "  bcdba",
    ), (
        "    653", "    6754", "   564543", "    654543", "    4654543",
        "   343654432", "  45xxx457632", " 453232 45632", " 34232   4532",
        "  232     321", "   2",
    )),
    24: ((1,5), (
        "   CE   B", "   GFD CB", "  EGFDEFC", "  DFEGECB", "  CEGBddb", "  BEFcedd",
        "  BDEbefd", "  CDBegfc", "  CBcegfb", "  bxxxyxx", "  adffgeca",
        "  abefghfc", "  acdfggfc", "  acdefgdc", "   bdeefc", "   abddc",
    ), (
        "   65  3", "   674 32", "  5745432", "  4654543", "  3456453", "  3456543",
        "  3456432", "  3465432", "  3456432", "  465xxyx", "  5642342", "  45322342",
        "  3432 232", "  32    22", "  2",
    )),
}

# Back of the front-facing cloak. On the retail Thief the free corner
# swings behind the arm and the supporting leg stays visible in front.
# Each painting starts at the far ribs and follows the turn of that hip.
CLOAK_BACK = {
    0: ((13, 9), ("  443", " 4543", " 35432", " 345342", " 235453",
                  "  34542", "  34562", "  23453", "   3452", "    343",
                  "     32", "      2")),
    3: ((12, 9), ("  443", " 4543", " 34542", " 23453", "  34543",
                  "  23542", "  34563", "  23453", "   3452", "    342", "     32")),
    4: ((11, 9), ("  443", " 4543", " 34543", " 234542", "  34543",
                  "  234562", "   34563", "   23454", "    34532", "      342",
                  "        2")),
    5: ((12, 8), ("  443", " 45432", "  35432", "  34543", "   34532",
                  "  234543", "  234563", "   234563", "    34562",
                  "     23453", "       342", "         2")),
    6: ((11, 9), ("  443", " 4543", " 34542", " 23453", "  34542",
                  "  23453", "   34542", "   23453", "    3452", "     342", "      2")),
}

# The low hands pass through the old rectangular breeches mask. Use the
# actual outer edges of the thighs through the walk.
THIGHS = {0: (6, 17), 3: (5, 14), 4: (5, 14), 5: (5, 14), 6: (5, 13)}

# A rolled rim grips the temple and clears the entire cheek. The first
# two rows share the scalp height; the shade at one temple turns into the
# short collar instead of continuing down to the hem.
COWL = (
    "    57752  ", "  46786532 ", " 5754   432", "675      32",
    "564      23", "345      43", " 456    542", "  453   32 ",
    "   432     ",
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
    thigh_left, thigh_right = THIGHS.get(pose, (wl-3, wr+3))
    knee = fit.HIDE_POINTS[pose][3]
    (left, top), drows, trows = FRONT[pose] if pose in FRONT else TURNS[pose]
    for y, row in enumerate(body):
        for u, skin in enumerate(row):
            x = u-fit.PAD
            pt = x,y
            if pt in bow or (skin is not None and pt in hands):
                continue
            if pose in CLOAK_BACK and skin is None:
                (cx, cy), lining = CLOAK_BACK[pose]
                thief[y][u] = mark(lining, x-cx, y-cy)
            if pt not in protected:
                d = mark(drows, x-left, y-top)
                t = mark(trows, x-left, y-top)
                if d is not None:
                    druid[y][u] = d
                # The leather breeches remain visible in
                # the opening. Keep the separate leg silhouettes and bare feet.
                near_elbow = pose == 17 and pt == (6, 14)
                if skin in LEATHER and waist <= y <= knee+1 and thigh_left <= x <= thigh_right and not near_elbow:
                    # Deep leather at the knees separates them from the loose
                    # slate fold that swings over the tunic.
                    thief[y][u] = LEATHER[skin]
                if t is not None:
                    thief[y][u] = t
            if pose in FRONT:
                c = mark(COWL, x-hx+2, y-hy)
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
