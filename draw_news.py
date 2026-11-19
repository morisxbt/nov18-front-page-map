"""Draw an original, compact world-news broadsheet for 18 November 2026."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

random.seed(18)
W = H = 1024
PAPER = (246, 240, 222)
INK = (27, 35, 37)
MUTED = (80, 87, 82)
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
for _ in range(2200):
    x, y = random.randrange(W), random.randrange(H)
    delta = random.choice((-3, -2, 2, 3))
    d.point((x, y), fill=tuple(max(0, min(255, c + delta)) for c in PAPER))

def font(face, size):
    return ImageFont.truetype(face, size)

def txt(x, y, value, size, color=INK, face=BODY, anchor=None):
    d.text((x, y), value, font=font(face, size), fill=color, anchor=anchor)

def wrap(value, face, size, width):
    ft = font(face, size)
    lines, line = [], ""
    for word in value.split():
        trial = (line + " " + word).strip()
        if d.textlength(trial, font=ft) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def para(x, y, value, size, width, color=INK, face=BODY, leading=2, max_lines=None):
    lines = wrap(value, face, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        txt(x, y + i * (size + leading), line, size, color, face)
    return len(lines) * (size + leading)

def rule(y, color=INK, width=2, x0=24, x1=1000):
    d.line((x0, y, x1, y), fill=color, width=width)

def box(x, y, w, h, fill=(239, 229, 207), outline=(170, 157, 130), radius=5):
    d.rounded_rectangle((x, y, x+w, y+h), radius=radius, fill=fill, outline=outline, width=1)

# Masthead: the date is the visual anchor; the calendar tile carries the day code.
txt(26, 12, "THE WORLD'S NEWS IN ONE PICTURE", 13, RED, LABEL)
txt(26, 29, "Wednesday 18 November 2026", 43, INK, DISPLAY)
txt(28, 81, "Everything on this page happened, or was first reported, on Wednesday 18 November 2026.", 11, MUTED, BODY)
box(894, 17, 102, 70, (36, 54, 58), (36, 54, 58), 3)
txt(945, 18, "18", 28, (250, 241, 218), DISPLAY, "mt")
txt(945, 49, "WED", 13, (232, 186, 93), LABEL, "mt")
txt(945, 68, "2026", 11, (250, 241, 218), LABEL, "mt")
rule(103, width=3)

# Actual story distribution: Europe 7, Middle East 3, Asia 12, Africa 3,
# Americas 8, Oceania 3 and World 2; together the page carries 38 stories.
counts = [("EUROPE",7),("MIDDLE EAST",3),("ASIA",12),("AFRICA",3),("AMERICAS",8),("OCEANIA",3),("WORLD",2)]
for i, (name, count) in enumerate(counts):
    x = 25 + i * 139
    d.rectangle((x, 112, x+5, 128), fill=REGION[name])
    txt(x+10, 110, f"{name}  {count}", 11, REGION[name], LABEL)
rule(135, color=(169, 158, 137), width=1)
txt(26, 140, "THE DAY IN NUMBERS", 11, RED, LABEL)
numbers = "141 drones fired at Ukraine · 126 downed or jammed · Voyager 1 at 25.9 billion km · UK CPI 3.6% · Jeffries 251–11 · ~300 arrested in Bangladesh · €45bn EU loan · 37 civilians in Amnesty's El Obeid report"
para(156, 140, numbers, 9, 844, INK, BODY, 1, 2)
rule(165, color=(169, 158, 137), width=1)

leads = [
    ("ASIA · APEC SUMMIT", "Xi greets Trump on the tarmac in Shenzhen", "At Bao'an airport, Xi meets Trump with a handshake and brief hug; Trump later greets Putin. Formal three-way APEC talks are set for Thursday. Critics fear Kyiv and Europe could be sidelined.", "summit"),
    ("MIDDLE EAST · IRAN", "Iran fires at a US base in Kuwait; Bahrain reports interceptions", "Iran says it targeted US forces at Ali Al Salem after a US strike on Qeshm Island. Bahrain says it intercepted Iranian aerial attacks for a third time in a week.", "gulf"),
    ("WORLD · SPACE", "Voyager 1 is one light-day from Earth", "NASA calculations put the 1977 probe at 25.9 billion km, reached at 5:16 a.m. ET Wednesday: the first human-made object one light-day away, in interstellar space.", "space"),
]

def art(kind, x, y, w, h):
    bg = {"summit":(37,75,84), "gulf":(39,75,78), "space":(27,43,68)}[kind]
    d.rounded_rectangle((x,y,x+w,y+h), radius=4, fill=bg)
    if kind == "summit":
        # Three flags and a runway handshake silhouette.
        flags = [(x+14,"US"),(x+69,"CN"),(x+124,"RU")]
        for j,(fx,label) in enumerate(flags):
            d.line((fx,y+4,fx,y+35), fill=(226,222,204), width=1)
            if j == 0:
                d.rectangle((fx+1,y+5,fx+31,y+20), fill=(232,232,214))
                for sy in (7,11,15,19): d.line((fx+1,y+sy,fx+31,y+sy), fill=(172,55,48), width=2)
                d.rectangle((fx+1,y+5,fx+13,y+12), fill=(46,72,105))
            elif j == 1:
                d.rectangle((fx+1,y+5,fx+31,y+20), fill=(181,48,42))
                d.ellipse((fx+7,y+8,fx+11,y+12), fill=(241,196,73))
            else:
                d.rectangle((fx+1,y+5,fx+31,y+10), fill=(235,235,225))
                d.rectangle((fx+1,y+10,fx+31,y+15), fill=(62,92,139))
                d.rectangle((fx+1,y+15,fx+31,y+20), fill=(175,54,50))
            txt(fx+15,y+22,label,8,(246,236,212),LABEL,"mt")
        d.line((x+174,y+30,x+w-9,y+30), fill=(220,191,121), width=2)
        d.ellipse((x+197,y+8,x+211,y+22), fill=(224,187,143))
        d.ellipse((x+219,y+8,x+233,y+22), fill=(199,158,122))
        d.polygon([(x+192,y+22),(x+206,y+19),(x+215,y+29),(x+222,y+20),(x+237,y+23),(x+229,y+38),(x+203,y+38)], fill=(226,222,202))
        txt(x+w-8,y+2,"APEC · SHENZHEN",8,(255,227,170),LABEL,"ra")
    elif kind == "gulf":
        # Gulf coast diagram, incoming tracks, and explicitly attributed labels.
        d.polygon([(x+5,y+4),(x+69,y+4),(x+75,y+18),(x+58,y+29),(x+45,y+24),(x+31,y+36),(x+4,y+28)], fill=(178,157,111))
        d.polygon([(x+80,y+5),(x+111,y+3),(x+142,y+12),(x+140,y+33),(x+117,y+38),(x+99,y+26)], fill=(183,166,121))
        d.polygon([(x+69,y+14),(x+87,y+12),(x+100,y+20),(x+88,y+29),(x+73,y+26)], fill=(64,134,145))
        for px,py in ((47,16),(86,21),(120,26)):
            d.ellipse((x+px-3,y+py-3,x+px+3,y+py+3), fill=(224,76,57), outline=(255,238,211))
        d.line((x+47,y+16,x+78,y+22), fill=(240,128,72), width=2)
        txt(x+151,y+5,"IRAN SAYS",9,(255,213,155),LABEL)
        txt(x+151,y+17,"HIT ON ALI AL SALEM",9,(255,245,224),LABEL)
        txt(x+151,y+30,"BAHRAIN: INTERCEPTED",8,(164,220,211),LABEL)
    else:
        d.ellipse((x+15,y+7,x+49,y+41), fill=(91,151,174), outline=(218,231,223), width=2)
        d.arc((x+23,y+7,x+41,y+41),90,270,fill=(222,231,223),width=1)
        d.line((x+16,y+24,x+48,y+24),fill=(222,231,223),width=1)
        d.ellipse((x+219,y+13,x+228,y+22), fill=(234,202,127))
        d.polygon([(x+187,y+20),(x+215,y+14),(x+225,y+18),(x+215,y+22),(x+201,y+22)], fill=(227,230,215))
        d.line((x+50,y+24,x+183,y+24), fill=(145,190,203), width=1)
        txt(x+64,y+5,"1 LIGHT-DAY",13,(255,233,181),LABEL)
        txt(x+73,y+26,"25.9bn km",10,(232,241,235),LABEL)

for i,(tag,headline,dek,kind) in enumerate(leads):
    x = 25 + i*326
    box(x,171,314,219,(239,228,205))
    txt(x+9,175,f"0{i+1}  {tag}",10,RED,LABEL)
    art(kind,x+9,193,296,45)
    hh = para(x+9,243,headline,17,296,INK,HEAD,0,2)
    para(x+9,246+hh,dek,10,296,MUTED,BODY,1,4)

# Nine brief illustrated cards complete the main package without crowding it.
cards = [
 (4,"EUROPE · UKRAINE AID","EU proposes €45bn loan for Ukraine in 2027, toward a €70bn gap; Kyiv repays after Russian reparations.","€"),
 (5,"EUROPE · UKRAINE WAR","Russia launched 141 drones; Ukraine says 126 were destroyed or jammed. Impacts at seven sites.","141"),
 (6,"MIDDLE EAST · GAZA","Israeli tanks cross the yellow line into central Gaza for the first time since the ceasefire; both sides trade accusations.","G"),
 (7,"AMERICAS · US POLITICS","House Democrats nominate Hakeem Jeffries for Speaker, 251–11; election would make him the first Black Speaker.","251"),
 (8,"AMERICAS · MARKETS","Fed minutes: almost all officials said further rate hikes would likely be appropriate; AI risks flagged.","%"),
 (9,"WORLD · CULTURE","GTA VI midnight launch begins in New Zealand ahead of the 19 November global release, after 13 years.","VI"),
 (10,"ASIA · LABOUR","Bangladesh garment unrest: highway blockades, clashes and a police vehicle fire; reports say ~300 arrested.","Tk"),
 (11,"AFRICA · SUDAN","Amnesty says RSF drone strikes killed 37 civilians and injured 10 in El Obeid; RSF denies responsibility.","37"),
 (12,"EUROPE · ECONOMY","UK inflation rose to 3.6% in October, a one-year high, ONS says, after petrol and record diesel rises.","3.6"),
]
for i,(num,tag,copy,symbol) in enumerate(cards):
    row,col = divmod(i,3)
    x,y = 25+col*326,397+row*64
    box(x,y,314,58,(241,232,213))
    d.ellipse((x+8,y+8,x+43,y+43), fill=REGION["EUROPE"] if num in (4,5,12) else REGION["ASIA"] if num==10 else REGION["AFRICA"] if num==11 else REGION["AMERICAS"] if num in (7,8) else REGION["WORLD"] if num in (9,) else REGION["MIDDLE EAST"], outline=(255,248,225), width=1)
    txt(x+25.5,y+25,str(symbol),9,(255,250,230),LABEL,"mm")
    txt(x+50,y+4,f"{num:02d}  {tag}",9,RED,LABEL)
    para(x+50,y+18,copy,9,254,INK,BODY,1,4)

rule(595, width=3)
txt(25,599,"WHERE IT HAPPENED",14,INK,LABEL)
txt(478,599,"ALSO ON WEDNESDAY 18 NOVEMBER",14,INK,LABEL)
d.line((464,600,464,879),fill=(147,139,121),width=1)

# Simplified world map with numbered, color-coded pins at approximate locations.
mx,my,mw,mh = 25,622,426,250
box(mx,my,mw,mh,(211,229,226),(67,99,99),4)
def land(points):
    d.polygon([(mx+a,my+b) for a,b in points],fill=(223,211,180),outline=(151,143,115),width=1)
land([(18,52),(29,33),(52,22),(73,27),(94,35),(116,45),(121,58),(107,70),(97,86),(88,101),(79,126),(66,136),(58,116),(49,98),(37,88),(30,68)])
land([(93,130),(109,132),(119,147),(115,169),(107,192),(100,216),(92,199),(91,177),(84,155)])
land([(183,52),(199,43),(213,49),(223,58),(217,70),(202,72),(194,82),(183,72)])
land([(195,78),(213,73),(228,81),(236,101),(231,124),(221,148),(211,164),(203,144),(198,124),(190,105)])
land([(220,54),(243,42),(269,38),(296,31),(326,38),(355,42),(383,56),(402,64),(390,78),(372,81),(352,92),(333,86),(316,96),(294,89),(278,98),(258,84),(240,86),(226,74)])
land([(270,91),(284,94),(291,110),(284,123),(277,117)])
land([(337,138),(354,131),(378,136),(392,148),(388,163),(372,171),(352,168),(338,157)])
d.ellipse((mx+403,my+127,mx+409,my+132),fill=(223,211,180),outline=(151,143,115))

# geographic projection pin data, deliberately slightly offset where places cluster
pins = {
1:(348,82,"ASIA"),2:(244,99,"MIDDLE EAST"),3:(405,18,"WORLD"),4:(196,62,"EUROPE"),5:(190,52,"EUROPE"),6:(217,103,"MIDDLE EAST"),7:(75,75,"AMERICAS"),8:(70,58,"AMERICAS"),9:(366,168,"OCEANIA"),10:(300,130,"ASIA"),11:(213,145,"AFRICA"),12:(198,79,"EUROPE"),13:(79,117,"AMERICAS"),14:(387,173,"OCEANIA"),15:(57,52,"AMERICAS"),16:(207,55,"EUROPE"),17:(331,100,"ASIA"),18:(89,47,"AMERICAS"),19:(226,120,"MIDDLE EAST"),20:(205,143,"AFRICA"),21:(370,153,"OCEANIA"),22:(358,72,"ASIA"),23:(338,73,"ASIA"),24:(324,111,"ASIA"),25:(292,91,"ASIA"),26:(290,125,"ASIA"),27:(234,100,"ASIA"),28:(64,66,"AMERICAS"),29:(229,109,"AFRICA"),30:(211,65,"EUROPE"),31:(185,68,"EUROPE"),32:(299,80,"ASIA"),33:(88,76,"AMERICAS"),34:(84,144,"AMERICAS"),35:(310,120,"ASIA"),36:(366,155,"OCEANIA"),37:(360,91,"ASIA"),38:(202,48,"EUROPE")}
for n,(px,py,region) in pins.items():
    xx,yy = mx+px,my+py
    color = REGION[region]
    d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=color,outline=(255,249,225),width=1)
    txt(xx,yy-0.2,str(n),7,(255,255,247),LABEL,"mm")
legend = [("EUROPE","EU"),("MIDDLE EAST","ME"),("ASIA","AS"),("AFRICA","AF"),("AMERICAS","AM"),("OCEANIA","OC"),("WORLD","W")]
for i,(region,label) in enumerate(legend):
    col,row = i%4,i//4
    xx,yy = mx+9+col*102,my+222+row*13
    d.ellipse((xx,yy+2,xx+8,yy+10),fill=REGION[region])
    txt(xx+12,yy,label,8,INK,LABEL)

also = [
"Caracas — Hegseth meets interim leader Rodríguez; later due in Colombia.",
"N Cook Islands — Xavier down to Cat 4; 300+ sheltered on Pukapuka; no casualties.",
"San Francisco — Waymo pauses US driverless freeway rides after California DMV ban.",
"Frankfurt — Watchdog probes Deutsche Bank after leak of ~15 million internal files.",
"Manila — Trump hails trade deal; Manila says sides reached an economic understanding.",
"Ottawa — Canada and China expand tariff relief on pork, seafood and metals.",
"Gaza / UN — Board of Peace says Israel and Hamas fail commitments; truce at risk.",
"Borno, Nigeria — Troops kill 21 suspected ISWAP fighters, Vanguard reports.",
"Suva — Fiji declares disaster over El Niño drought; evacuations and rationing enabled.",
"Shenzhen / Canberra — Albanese joins APEC family photo with Putin, defying critics.",
"Shenzhen — Japan's Takaichi shakes Xi's hand; no formal bilateral talks scheduled.",
"Bay of Bengal — Akvan turns north-northwest; coast crossing forecast for 20 Nov.",
"Kulgam, Kashmir — Security forces kill LeT militant Lateef Bhat after mosque firefight.",
"Kollam, Kerala — About 50 students hospitalised after suspected tar-unit pollution.",
"Ceyhan / Iraq — Oil pumping to Turkey resumes after 12 years; capacity 750,000 b/d.",
"Silicon Valley — US arrests alleged Russian agent accused of corporate espionage.",
"Ethiopia–Eritrea border — Armies amass within striking distance, Reuters sources say.",
"Brussels — EPP prepares December move to suspend President Vučić's SNS party.",
"Kyiv — Zelenskyy proposes 10 more humanitarian evacuations after Oleshky to US mediators.",
"New Delhi — Police tell court no mandate requires women officers to handle women in crowds.",
"Washington — FAA chief Bedford: 'Blame me' over flight stoppage; critics should 'lay off' Duffy.",
"Port-au-Prince — Bukele confirms strike on Larose's mansion; gang leader's presence unclear.",
"Mumbai — Niue Ocean Wide Trust wins Earthshot Prize at ceremony attended by Waleses.",
"Australia — Bancroft reopens sandpaper row; Warner calls for a public inquiry.",
"Shenzhen — South Korea's Lee Jae-myung receives ceremonial APEC welcome.",
"Antalya — COP31 phase-out row; four EU countries publish fossil-fuel exit roadmaps.",
]
for i,story in enumerate(also):
    col,row = divmod(i,13)
    x,y = 478+col*258,622+row*19
    txt(x,y,f"{i+13:02d}",9,RED,LABEL)
    para(x+22,y,story,9,232,INK,BODY,0,2)

# Date check and sourcing sit in a separate footer band.
box(25,881,975,86,(249,235,220),(177,58,49),4)
txt(35,884,"DATE CHECK",11,RED,LABEL)
txt(130,884,"Left out on purpose — first reported on Tuesday 17 November, so not this day's news:",8,INK,BODY)
excluded = "Prague train collision (46 injured) · Kerch Bridge road-span collapse · Nvidia's $115.8bn quarter / Huang board news · Knesset elects Matan Kahana speaker · Haiti formalises El Salvador security pact · Houthi drones toward the Saudi East-West pipeline."
para(35,902,excluded,8,950,INK,BODY,2,4)
txt(25,974,"Sources: Reuters · AP · AFP · BBC · The Hindu · The Guardian · NPR · CNBC · Amnesty · Ukrainian Air Force · ONS · Kyodo · RNZ · Euronews · Vanguard · Washington Post · NamPA/AFP",8,INK,BODY)
txt(999,1002,"18 NOV 2026",8,RED,LABEL,"ra")

out = Path(__file__).resolve().parent / "entry.png"
im.save(out, format="PNG", optimize=True)
print(f"Wrote {out} ({out.stat().st_size} bytes)")
