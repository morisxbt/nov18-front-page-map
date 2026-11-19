"""Render the illustrated 18 November 2026 world-news front page."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

random.seed(18)
W = H = 1024
PAPER = (246, 240, 222)
INK = (27, 35, 37)
MUTED = (76, 83, 80)
RED = (166, 49, 43)
DISPLAY = "/usr/share/fonts/truetype/sand-box/google/Playfair Display/PlayfairDisplay-VariableFont_wght.ttf"
HEAD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
BODY = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LABEL = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REGION = {
    "EUROPE": (169, 55, 48), "MIDDLE EAST": (190, 125, 35),
    "ASIA": (45, 112, 83), "AFRICA": (124, 82, 136),
    "AMERICAS": (44, 99, 145), "OCEANIA": (34, 128, 132),
    "WORLD": (78, 82, 87),
}

im = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(im)
for _ in range(2400):
    px, py = random.randrange(W), random.randrange(H)
    dv = random.choice((-3, -2, 2, 3))
    d.point((px, py), fill=tuple(max(0, min(255, c + dv)) for c in PAPER))

_FONT_CACHE = {}

def ft(path, size):
    # Reuse font objects for consistent metrics and faster dense-page rendering.
    key = (path, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]

def text(x, y, value, size, color=INK, face=BODY, anchor=None):
    d.text((x, y), value, font=ft(face, size), fill=color, anchor=anchor)

def wrap(value, face, size, width):
    f = ft(face, size)
    lines = []
    for paragraph in value.splitlines() or [value]:
        current = ""
        for word in paragraph.split():
            candidate = (current + " " + word).strip()
            if d.textlength(candidate, font=f) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines

def para(x, y, value, size, width, color=INK, face=BODY, leading=1, max_lines=None):
    lines = wrap(value, face, size, width)
    if max_lines is not None:
        if len(lines) > max_lines:
            raise ValueError(f"Text needs {len(lines)} lines, limit is {max_lines}: {value}")
    if any(d.textlength(line, font=ft(face, size)) > width for line in lines):
        raise ValueError(f"Wrapped text exceeds its {width}px slot: {value}")
    for idx, line in enumerate(lines):
        text(x, y + idx * (size + leading), line, size, color, face)
    return lines

def rect(x, y, w, h, fill, outline=(175, 161, 135), radius=5):
    d.rounded_rectangle((x, y, x+w, y+h), radius=radius, fill=fill, outline=outline, width=1)

def rule(y, width=2, color=INK):
    d.line((24, y, 1000, y), fill=color, width=width)

def lines_height(lines, size, leading=1):
    return len(lines) * (size + leading)

def assert_text_fits(lines, x, y, size, face, bounds, leading=0):
    left, top, right, bottom = bounds
    f = ft(face, size)
    for idx, line in enumerate(lines):
        bbox = d.textbbox((x, y + idx * (size + leading)), line, font=f)
        if bbox[0] < left or bbox[2] > right or bbox[1] < top or bbox[3] > bottom:
            raise ValueError(f"Text bbox {bbox} exceeds box {bounds}: {line}")

# Count check: EU 7, Middle East 3, Asia 12, Africa 3, Americas 8,
# Oceania 3, World 2. The story set below and the map carry 38 numbers.
counts = [("EUROPE", 7), ("MIDDLE EAST", 3), ("ASIA", 12), ("AFRICA", 3),
          ("AMERICAS", 8), ("OCEANIA", 3), ("WORLD", 2)]
assert sum(n for _, n in counts) == 38

# Masthead and calendar badge.
text(25, 8, "THE WORLD'S NEWS IN ONE PICTURE  ·  38 STORIES", 12, RED, LABEL)
text(25, 22, "Wednesday 18 November 2026", 36, INK, DISPLAY)
text(27, 63, "Everything here happened, or was first reported, on this date.", 11, MUTED, BODY)
rect(894, 9, 102, 61, (36, 54, 58), (36, 54, 58), 3)
text(945, 8, "18", 24, (250, 241, 218), DISPLAY, "mt")
text(945, 36, "WED", 12, (232, 186, 93), LABEL, "mt")
text(945, 53, "2026", 10, (250, 241, 218), LABEL, "mt")
rule(79, 3)
for i, (region, count) in enumerate(counts):
    x = 25 + i * 139
    d.rectangle((x, 86, x+5, 102), fill=REGION[region])
    text(x+10, 86, f"{region}  {count}", 11, REGION[region], LABEL)
text(998, 105, "38 STORIES · 7 REGIONS", 8, MUTED, LABEL, "ra")
text(25, 105, "THE DAY IN NUMBERS", 9, RED, LABEL)

# Six illustrated number cells replace the old compressed ticker.
nums = [
    ("141", "Russian drones\nfired at Ukraine"),
    ("126", "downed or jammed\nby Ukraine"),
    ("25.9bn km", "Voyager 1's\none light-day"),
    ("3.6%", "UK October CPI,\none-year high"),
    ("251–11", "Jeffries' House\nDemocratic vote"),
    ("~300", "Bangladesh arrests\nreported in unrest"),
]
for i, (number, caption) in enumerate(nums):
    x = 25 + i * 162
    rect(x, 116, 154, 58, (238, 228, 207), (193, 179, 151), 4)
    text(x+8, 116, number, 21, INK, LABEL)
    for j, capline in enumerate(caption.split("\n")):
        text(x+8, 143+j*12, capline, 11, MUTED, BODY)
    if i in (0, 1):
        # Tiny drone silhouettes in the Ukraine number cells.
        cx = x+127
        d.line((cx-9, 137, cx+9, 137), fill=REGION["EUROPE"], width=2)
        d.line((cx, 132, cx, 142), fill=REGION["EUROPE"], width=2)
        for dx in (-10, 10):
            d.ellipse((cx+dx-3, 134, cx+dx+3, 140), outline=REGION["EUROPE"], width=1)
    elif i == 2:
        d.ellipse((x+124, 125, x+143, 144), outline=REGION["WORLD"], width=2)
        d.arc((x+129, 125, x+138, 144), 90, 270, fill=REGION["WORLD"], width=1)
    elif i == 3:
        d.line((x+123, 150, x+128, 144, x+133, 147, x+141, 128), fill=REGION["EUROPE"], width=2)
    elif i == 4:
        d.polygon([(x+125, 133), (x+143, 133), (x+139, 143), (x+129, 143)], fill=REGION["AMERICAS"])
        d.line((x+134, 125, x+134, 132), fill=REGION["AMERICAS"], width=2)
    else:
        d.rectangle((x+125, 130, x+142, 144), outline=REGION["ASIA"], width=2)
        d.line((x+128, 135, x+139, 135), fill=REGION["ASIA"], width=1)

leads = [
    ("ASIA · APEC SUMMIT", "Xi greets Trump at Shenzhen airport",
     "At Bao'an, Xi and Trump handshake and briefly hug. Trump later greets Putin. Critics fear Kyiv and Europe could be sidelined by Thursday's planned talks.", "CONFIRMED · AP · REUTERS", "summit"),
    ("MIDDLE EAST · IRAN", "Iran says it struck US base in Kuwait",
     "Tehran says it targeted Ali Al Salem after a US strike on Qeshm Island. Bahrain says it intercepted Iranian aerial attacks for a third time in a week.", "CLAIM · IRAN STATE MEDIA · BAHRAIN SAYS", "gulf"),
    ("WORLD · SPACE", "Voyager 1 reaches one light-day away",
     "NASA calculates 25.9 billion km from Earth at 5:16 a.m. ET: the first human-made object one light-day distant, in interstellar space.", "NASA CALCULATION", "space"),
]

def lead_art(kind, x, y, w, h):
    bg = {"summit": (36, 77, 86), "gulf": (42, 76, 77), "space": (27, 43, 68)}[kind]
    d.rounded_rectangle((x, y, x+w, y+h), radius=4, fill=bg)
    if kind == "summit":
        # Three flags, tarmac perspective and simplified welcoming figures.
        for idx, fx in enumerate((x+12, x+62, x+112)):
            d.line((fx, y+7, fx, y+61), fill=(230, 224, 204), width=2)
            if idx == 0:
                d.rectangle((fx+2, y+9, fx+40, y+30), fill=(240, 239, 223))
                for yy in (11, 16, 21, 26): d.line((fx+2, y+yy, fx+40, y+yy), fill=(178, 49, 45), width=2)
                d.rectangle((fx+2, y+9, fx+18, y+19), fill=(45, 73, 112))
            elif idx == 1:
                d.rectangle((fx+2, y+9, fx+40, y+30), fill=(183, 47, 42))
                d.ellipse((fx+8, y+13, fx+14, y+19), fill=(243, 194, 66))
            else:
                d.rectangle((fx+2, y+9, fx+40, y+16), fill=(239, 238, 224))
                d.rectangle((fx+2, y+16, fx+40, y+23), fill=(63, 94, 140))
                d.rectangle((fx+2, y+23, fx+40, y+30), fill=(175, 57, 51))
        d.polygon([(x+8, y+72), (x+w-8, y+54), (x+w-8, y+78), (x+8, y+84)], fill=(56, 66, 61))
        d.line((x+17, y+76, x+w-15, y+62), fill=(225, 191, 116), width=2)
        d.ellipse((x+191, y+18, x+211, y+38), fill=(225, 186, 146))
        d.ellipse((x+223, y+18, x+243, y+38), fill=(196, 153, 120))
        d.polygon([(x+184,y+40),(x+207,y+35),(x+218,y+52),(x+229,y+36),(x+250,y+40),(x+245,y+76),(x+188,y+76)], fill=(231,225,205))
        text(x+w-8, y+4, "SHENZHEN · APEC", 9, (255,229,175), LABEL, "ra")
    elif kind == "gulf":
        # Map-like Gulf, island/coast shapes, tracks and attributed claim boxes.
        d.polygon([(x+8,y+9),(x+89,y+8),(x+104,y+29),(x+78,y+43),(x+51,y+36),(x+27,y+56),(x+8,y+48)], fill=(178,157,111))
        d.polygon([(x+125,y+7),(x+184,y+8),(x+192,y+27),(x+172,y+43),(x+141,y+37)], fill=(188,166,118))
        d.polygon([(x+91,y+25),(x+120,y+22),(x+137,y+35),(x+117,y+48),(x+97,y+43)], fill=(68,140,149))
        for px, py in ((42,32),(106,34),(163,28)):
            d.ellipse((x+px-5,y+py-5,x+px+5,y+py+5), fill=(222,78,56), outline=(255,239,216), width=1)
        d.line((x+42,y+32,x+98,y+36), fill=(240,134,75), width=2)
        rect(x+199,y+8,88,24,(131,49,45),(131,49,45),3)
        text(x+243,y+12,"IRAN SAYS",10,(255,243,224),LABEL,"mt")
        rect(x+199,y+42,88,28,(221,233,218),(221,233,218),3)
        text(x+243,y+46,"BAHRAIN SAYS",9,(40,84,77),LABEL,"mt")
        text(x+243,y+58,"INTERCEPTED",8,(40,84,77),LABEL,"mt")
    else:
        # Earth, outbound trajectory and distant probe at one light-day scale.
        d.ellipse((x+21,y+20,x+81,y+80), fill=(75,139,169), outline=(219,234,226), width=2)
        d.arc((x+39,y+20,x+63,y+80), 90, 270, fill=(221,234,227), width=2)
        d.arc((x+30,y+20,x+72,y+80), 90, 270, fill=(221,234,227), width=1)
        d.line((x+22,y+50,x+80,y+50), fill=(221,234,227), width=2)
        for sx in range(x+101, x+222, 19): d.ellipse((sx,y+24,sx+2,y+26), fill=(242,230,194))
        d.line((x+84,y+50,x+242,y+50), fill=(139,188,201), width=2)
        d.polygon([(x+220,y+43),(x+254,y+49),(x+267,y+45),(x+254,y+53),(x+220,y+54)], fill=(226,231,219))
        d.ellipse((x+264,y+42,x+278,y+56), fill=(237,198,118))
        text(x+w-9,y+7,"25.9 BILLION KM",10,(255,230,177),LABEL,"ra")

for i, (tag, headline, dek, attribution, art_kind) in enumerate(leads):
    x, y, w, h = 25+i*326, 184, 314, 221
    rect(x,y,w,h,(239,228,205),(174,157,126),5)
    reg = tag.split(" · ")[0]
    text(x+9,y+5,tag,10,REGION[reg],LABEL)
    lead_art(art_kind,x+8,y+23,w-16,86)
    head_lines = para(x+9,y+113,headline,22,296,INK,HEAD,0,2)
    deck_y = y+113+lines_height(head_lines,22,0)+2
    deck_lines = para(x+9,deck_y,dek,11,296,MUTED,BODY,0,3)
    attr_y = deck_y + lines_height(deck_lines,11,0)+2
    text(x+9,attr_y,attribution,8,RED,LABEL)
    bounds=(x+5,y+108,x+w-5,y+h-2)
    assert_text_fits(head_lines,x+9,y+113,22,HEAD,bounds)
    assert_text_fits(deck_lines,x+9,deck_y,11,BODY,bounds)
    assert_text_fits([attribution],x+9,attr_y,8,LABEL,bounds)

# Nine illustrated secondary packages, with a bespoke small vignette each.
cards = [
 (4,"EUROPE","UKRAINE AID","EU proposes €45bn loan","2027 funding toward €70bn gap;\nKyiv repays after Russian reparations.","coin"),
 (5,"EUROPE","UKRAINE WAR","Ukraine says 126 of 141 drones down","Russia's overnight barrage hit seven sites;\nUkrainian Air Force says.","drones"),
 (6,"MIDDLE EAST","GAZA","Tanks cross Gaza's yellow line","First central Gaza incursion since truce;\nIsrael cites Hamas targets, Hamas says violation.","tank"),
 (7,"AMERICAS","US POLITICS","Jeffries wins 251–11 nomination","If elected in January, he would be\nthe first Black Speaker.","capitol"),
 (8,"AMERICAS","MARKETS","Fed officials see hikes as likely","Rate held at 3.75–4%; minutes flag\nAI inflation and stability risks.","chart"),
 (9,"WORLD","CULTURE","GTA VI launches in New Zealand","After 13 years, midnight launch precedes\nglobal release on 19 November.","game"),
 (10,"ASIA","LABOUR","Bangladesh garment unrest spreads","Demand rises Tk12,500 to Tk30,000;\n~300 arrested, hundreds of factories halted.","factory"),
 (11,"AFRICA","SUDAN","Amnesty reports 37 civilians killed","10 injured in El Obeid between June and August;\nRSF denies responsibility.","desert"),
 (12,"EUROPE","ECONOMY","UK inflation reaches 3.6%","October is a one-year high; petrol rose\nand diesel hit record prices, ONS says.","cpi"),
]

def vignette(kind,x,y,w):
    sky=(42,69,76)
    d.rectangle((x,y,x+w,y+23),fill=sky)
    if kind=="coin":
        for j in range(4):
            xx=x+16+j*17
            d.ellipse((xx,y+9-j%2*3,xx+14,y+21-j%2*3),fill=(221,175,68),outline=(255,224,139))
            text(xx+7,y+9-j%2*3,"€",8,(112,78,29),LABEL,"mm")
        d.line((x+105,y+18,x+276,y+18),fill=(130,180,156),width=2)
    elif kind=="drones":
        d.ellipse((x+240,y+3,x+259,y+22),fill=(226,195,130))
        for xx,yy in ((43,12),(104,7),(181,16),(274,9)):
            d.line((x+xx-7,y+yy,x+xx+7,y+yy),fill=(224,232,218),width=2)
            d.line((x+xx,y+yy-4,x+xx,y+yy+4),fill=(224,232,218),width=2)
        d.line((x+41,y+14,x+104,y+8),fill=(226,112,73),width=1)
    elif kind=="tank":
        d.line((x+178,y+2,x+178,y+22),fill=(240,197,81),width=3)
        d.rectangle((x+10,y+13,x+137,y+22),fill=(63,124,86))
        d.polygon([(x+39,y+11),(x+67,y+3),(x+99,y+11)],fill=(81,145,94))
        d.line((x+80,y+7,x+116,y+7),fill=(198,218,190),width=3)
        d.ellipse((x+27,y+19,x+43,y+23),fill=(30,44,39)); d.ellipse((x+105,y+19,x+121,y+23),fill=(30,44,39))
    elif kind=="capitol":
        d.polygon([(x+45,y+8),(x+81,y+2),(x+117,y+8),(x+111,y+11),(x+51,y+11)],fill=(229,222,197))
        for xx in (54,68,82,96,110): d.rectangle((x+xx,y+11,x+xx+5,y+21),fill=(229,222,197))
        d.rectangle((x+47,y+20,x+119,y+23),fill=(229,222,197))
        d.line((x+235,y+5,x+263,y+17),fill=(218,179,101),width=3)
        d.polygon([(x+230,y+3),(x+239,y+3),(x+237,y+10),(x+229,y+9)],fill=(218,179,101))
    elif kind=="chart" or kind=="cpi":
        d.line((x+18,y+20,x+18,y+4,x+292,y+4),fill=(182,199,187),width=1)
        d.line((x+22,y+18,x+74,y+15,x+126,y+17,x+180,y+8,x+231,y+12,x+285,y+5),fill=(227,97,76),width=2)
        if kind=="cpi": text(x+250,y+3,"3.6%",12,(255,229,172),LABEL)
        else: text(x+258,y+3,"AI",12,(255,229,172),LABEL)
    elif kind=="game":
        d.rounded_rectangle((x+99,y+4,x+177,y+21),radius=7,fill=(224,223,205))
        d.line((x+113,y+12,x+127,y+12),fill=(41,66,77),width=2); d.line((x+120,y+6,x+120,y+18),fill=(41,66,77),width=2)
        for xx in (154,164): d.ellipse((x+xx,y+8,x+xx+4,y+12),fill=(158,59,49))
        d.ellipse((x+227,y+3,x+245,y+21),outline=(242,195,81),width=2)
        d.line((x+236,y+2,x+236,y+22),fill=(242,195,81),width=1)
    elif kind=="factory":
        d.rectangle((x+45,y+9,x+131,y+23),fill=(184,175,145))
        d.polygon([(x+44,y+9),(x+65,y+1),(x+65,y+9),(x+85,y+2),(x+85,y+9),(x+105,y+2),(x+131,y+9)],fill=(194,184,149))
        for xx in (54,75,96,117): d.rectangle((x+xx,y+14,x+xx+7,y+20),fill=(81,143,155))
        d.rectangle((x+231,y+4,x+236,y+13),fill=(208,202,180)); d.rectangle((x+250,y+2,x+255,y+13),fill=(208,202,180))
    elif kind=="desert":
        d.polygon([(x,y+17),(x+67,y+8),(x+122,y+17),(x+190,y+9),(x+247,y+17),(x+w,y+10),(x+w,y+23),(x,y+23)],fill=(191,152,99))
        d.ellipse((x+234,y+2,x+251,y+19),fill=(238,194,112))
        d.polygon([(x+38,y+22),(x+55,y+6),(x+73,y+22)],fill=(124,98,71))

for idx,(num,region,topic,headline,deck,kind) in enumerate(cards):
    row,col=divmod(idx,3)
    x,y=25+col*326,412+row*77
    w,h=314,75
    rect(x,y,w,h,(240,230,209),(178,161,132),4)
    vignette(kind,x+1,y+1,w-2)
    text(x+7,y+25,f"{num:02d} · {region} · {topic}",9,REGION[region],LABEL)
    hlines=para(x+7,y+36,headline,15,300,INK,HEAD,0,1)
    decklines=para(x+7,y+50,deck,11,300,MUTED,BODY,0,2)
    if len(decklines)!=2:
        raise ValueError(f"Secondary deck must use two lines: {num} {deck}")
    card_bounds=(x+4,y+24,x+w-4,y+h-2)
    assert_text_fits(hlines,x+7,y+36,15,HEAD,card_bounds)
    assert_text_fits(decklines,x+7,y+50,11,BODY,card_bounds)

# Lower band: map at left, all 26 remaining stories in three readable columns.
rule(651,3)
text(25,655,"WHERE IT HAPPENED",13,INK,LABEL)
text(290,655,"ALSO ON WEDNESDAY 18 NOVEMBER · 13–38",13,INK,LABEL)
d.line((277,675,277,918),fill=(150,140,120),width=1)
mx,my,mw,mh=25,679,244,235
rect(mx,my,mw,mh,(211,229,226),(67,99,99),4)
def land(points):
    d.polygon([(mx+a,my+b) for a,b in points],fill=(223,211,180),outline=(151,143,115),width=1)
land([(9,45),(20,30),(37,22),(57,25),(75,32),(91,39),(95,53),(82,64),(74,79),(67,98),(54,112),(47,99),(37,85),(28,74),(19,60)])
land([(76,117),(91,118),(98,133),(94,157),(87,180),(80,205),(74,188),(73,164),(68,141)])
land([(112,47),(124,40),(137,44),(145,51),(141,62),(128,65),(121,73),(112,64)])
land([(121,69),(137,65),(150,73),(157,90),(153,111),(144,132),(137,149),(129,132),(125,113),(117,94)])
land([(143,47),(157,40),(174,37),(194,31),(213,36),(229,46),(237,55),(224,66),(211,69),(198,80),(184,75),(172,82),(159,74),(149,70)])
land([(174,78),(184,81),(190,94),(185,104),(179,100)])
land([(193,154),(205,148),(220,151),(230,160),(226,171),(214,179),(202,177),(193,167)])
# All 38 numbered pins; region colors stay consistent with the counts and cards.
pin_data={
1:(197,63,"ASIA"),2:(147,92,"MIDDLE EAST"),3:(231,17,"WORLD"),4:(127,48,"EUROPE"),5:(114,56,"EUROPE"),6:(132,95,"MIDDLE EAST"),7:(58,59,"AMERICAS"),8:(44,45,"AMERICAS"),9:(217,171,"OCEANIA"),10:(176,118,"ASIA"),11:(139,137,"AFRICA"),12:(112,44,"EUROPE"),13:(48,102,"AMERICAS"),14:(229,193,"OCEANIA"),15:(31,53,"AMERICAS"),16:(129,38,"EUROPE"),17:(216,89,"ASIA"),18:(61,39,"AMERICAS"),19:(141,106,"MIDDLE EAST"),20:(132,141,"AFRICA"),21:(222,162,"OCEANIA"),22:(210,51,"ASIA"),23:(183,53,"ASIA"),24:(187,98,"ASIA"),25:(171,67,"ASIA"),26:(168,94,"ASIA"),27:(143,89,"ASIA"),28:(38,71,"AMERICAS"),29:(150,108,"AFRICA"),30:(144,60,"EUROPE"),31:(108,67,"EUROPE"),32:(174,59,"ASIA"),33:(52,77,"AMERICAS"),34:(53,127,"AMERICAS"),35:(181,98,"ASIA"),36:(218,160,"OCEANIA"),37:(210,71,"ASIA"),38:(120,36,"EUROPE")}
for n,(px,py,region) in pin_data.items():
    xx,yy=mx+px,my+py
    d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=REGION[region],outline=(255,249,225),width=1)
    text(xx,yy,str(n),7,(255,255,250),LABEL,"mm")
legend=[("EUROPE","EU"),("MIDDLE EAST","ME"),("ASIA","AS"),("AFRICA","AF"),("AMERICAS","AM"),("OCEANIA","OC"),("WORLD","W")]
for i,(region,short) in enumerate(legend):
    col,row=i%4,i//4
    xx,yy=mx+7+col*58,my+218+row*12
    d.ellipse((xx,yy+2,xx+7,yy+9),fill=REGION[region])
    text(xx+9,yy,short,7,INK,LABEL)

also=[
"Caracas — Hegseth met interim leader Rodríguez; later due in Colombia.",
"N Cook Islands — Xavier down to Cat 4; 300+ sheltered; no casualties.",
"San Francisco — Waymo pauses US freeway rides after California DMV ban.",
"Frankfurt — Watchdog probes Deutsche Bank after ~15m files leaked.",
"Manila — Trump hails deal; Manila says economic understanding reached.",
"Ottawa — Canada, China expand tariff relief on pork, seafood, metals.",
"Gaza / UN — Board of Peace warns truce in danger; both sides fail commitments.",
"Borno — Troops kill 21 suspected ISWAP fighters, Vanguard reports.",
"Suva — Fiji declares disaster over El Niño drought; enables evacuations.",
"Shenzhen — Albanese joins APEC family photo with Putin, defying critics.",
"Shenzhen — Japan's Takaichi shakes hands with Xi; no formal talks.",
"Bay of Bengal — Akvan turns north; coast crossing forecast for 20 Nov.",
"Kulgam — Forces kill LeT militant Lateef Bhat after mosque firefight.",
"Kollam — About 50 students hospitalised after suspected tar-unit pollution.",
"Ceyhan — Iraq resumes Turkey oil pumping after 12 years; up to 750k b/d.",
"Silicon Valley — US arrests alleged Russian agent accused of spying on firm.",
"Ethiopia–Eritrea — Armies mass within striking distance, Reuters sources say.",
"Brussels — EPP prepares December move to suspend Vučić's SNS party.",
"Kyiv — Zelenskyy proposes 10 more humanitarian evacuations after Oleshky.",
"New Delhi — Police tell court no rule requires women officers for crowd control.",
"Washington — FAA chief: 'Blame me'; critics should 'lay off' Duffy.",
"Port-au-Prince — Bukele confirms strike on Larose mansion; his presence unclear.",
"Mumbai — Niue Ocean Wide Trust wins Earthshot Prize; Waleses attended.",
"Australia — Bancroft reopens sandpaper row; Warner calls for public inquiry.",
"Shenzhen — South Korea's Lee arrives for APEC; ceremonial welcome.",
"Antalya — COP31 phase-out row; four EU states publish exit roadmaps.",
]
for i,story in enumerate(also):
    col,row=divmod(i,9)
    x=290+col*235
    y=679+row*26
    number=i+13
    text(x,y,f"{number:02d}",10,RED,LABEL)
    story_lines=para(x+23,y,story,11,205,INK,BODY,0,2)
    if len(story_lines)>2:
        raise ValueError(f"Also story {number} exceeds its two-line slot")
    assert_text_fits(story_lines,x+23,y,11,BODY,(x+21,y,x+230,y+25))

# Date check fills the footer band with both earlier reports and future events.
rect(25,922,975,75,(249,235,220),(177,58,49),4)
text(35,925,"DATE CHECK",11,RED,LABEL)
text(132,925,"Tuesday 17 November reports, left out:",11,INK,LABEL)
text(515,925,"Not happened yet:",11,INK,LABEL)
tuesday="Prague train collision (46 injured) · Kerch Bridge road-span collapse · Nvidia $115.8bn quarter / Huang board news · Knesset elects Matan Kahana · Haiti–El Salvador pact · Houthi drones toward Saudi East-West pipeline."
future="Thursday 19 Nov: planned Xi–Trump–Putin APEC talks; GTA VI global release. 20 Nov: forecast Cyclone Akvan landfall on Andhra Pradesh / south Odisha coast."
tuesday_lines=para(35,942,tuesday,11,463,INK,BODY,1,4)
future_lines=para(515,942,future,11,466,INK,BODY,1,4)
footer_bounds=(30,920,995,995)
assert_text_fits(tuesday_lines,35,942,11,BODY,footer_bounds,1)
assert_text_fits(future_lines,515,942,11,BODY,footer_bounds,1)
sources="Sources: Reuters · AP · AFP · BBC · The Hindu · The Guardian · NPR · CNBC · Amnesty · Ukrainian Air Force · ONS · Kyodo · RNZ · Euronews · Vanguard · Washington Post · NamPA/AFP"
text(25,1001,sources,8,INK,BODY)
source_bbox=d.textbbox((25,1001),sources,font=ft(BODY,8))
if source_bbox[0]<24 or source_bbox[2]>1000 or source_bbox[3]>1024:
    raise ValueError(f"Sources footer overflows canvas: {source_bbox}")
text(999,1011,"18 NOV 2026",8,RED,LABEL,"ra")

out=Path(__file__).resolve().parent/"entry.png"
im.save(out,format="PNG",optimize=True)
if im.size != (1024, 1024) or im.mode != "RGB":
    raise ValueError(f"Entry must be 1024x1024 RGB; got {im.size} {im.mode}")
if out.stat().st_size > 1048576:
    raise ValueError(f"Optimized PNG exceeds 1 MiB: {out.stat().st_size} bytes")
print(f"Wrote {out} ({out.stat().st_size} bytes)")
