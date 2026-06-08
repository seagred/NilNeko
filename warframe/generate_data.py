import requests
import json

# =========================
# CONFIG
# =========================
API_WARFRAME = "https://api.warframestat.us/warframes"
API_WEAPON = "https://api.warframestat.us/weapons"
API_SENTINEL = "https://api.warframestat.us/sentinels"

# =========================
# IMAGE SYSTEM (FIX ALL)
# =========================
def format_wiki_name(name):
    # Prime → ติดกัน
    name = name.replace(" Prime", "Prime")

    # Umbra → ต้องมี _
    name = name.replace(" Umbra", "_Umbra")

    # ช่องว่างอื่น
    name = name.replace(" ", "_")

    return name

def make_img(name):
    clean = format_wiki_name(name).replace("_", "")
    return f"https://wiki.warframe.com/images/thumb/{clean}.png/120px-{clean}.png"

def make_warframe_img(name):
    clean = format_wiki_name(name)
    return f"https://wiki.warframe.com/images/thumb/{clean}_Thumb.png/300px-{clean}_Thumb.png"

def item(name, type="normal"):
    if type == "warframe":
        return {"name": name, "img": make_warframe_img(name)}
    return {"name": name, "img": make_img(name)}

# =========================
# UTILS
# =========================
def safe_get(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except:
        print(f"❌ API ERROR: {url}")
        return []

def ensure_list(data, key=None):
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and key:
        return data.get(key, [])
    return []

def unique(items):
    seen = set()
    result = []
    for i in items:
        name = i.get("name")
        if name and name not in seen:
            seen.add(name)
            result.append(i)
    return result

# =========================
# FILTER
# =========================
def is_valid_name(name):
    bad = [
        "Blueprint","Set","Skin","Helmet",
        "Collection","Bundle","Glyph","Sigil",
        "Decoration","Emote"
    ]
    return not any(b.lower() in name.lower() for b in bad)

def is_real_warframe(name):
    blacklist = [
        "Necramech","Bonewidow","Voidrig",
        "Amesha","Itzal","Elytron","Odonata"
    ]
    return not any(b.lower() in name.lower() for b in blacklist)

# =========================
# LOAD
# =========================
print("📡 โหลดข้อมูล...")

warframes = ensure_list(safe_get(API_WARFRAME))
weapons = ensure_list(safe_get(API_WEAPON))
sentinels = ensure_list(safe_get(API_SENTINEL), "sentinels")

# =========================
# WARFRAME
# =========================
wf = []
for w in warframes:
    name = w.get("name")
    if not name or not is_valid_name(name) or not is_real_warframe(name):
        continue
    wf.append(item(name, "warframe"))

wf = unique(wf)

# =========================
# WEAPONS
# =========================
primary, secondary, melee = [], [], []

for w in weapons:
    name = w.get("name")
    cat = w.get("category", "")

    if not name or not is_valid_name(name):
        continue

    if cat == "Primary":
        primary.append(item(name))
    elif cat == "Secondary":
        secondary.append(item(name))
    elif cat == "Melee":
        melee.append(item(name))

primary = unique(primary)
secondary = unique(secondary)
melee = unique(melee)

# =========================
# ROBOT (Sentinel)
# =========================
if sentinels:
    robot = [item(s["name"]) for s in sentinels if s.get("name")]
else:
    print("⚠️ ใช้ sentinel manual")
    robot = [item(n) for n in [
        "Carrier","Carrier Prime","Dethcube","Dethcube Prime",
        "Diriga","Djinn","Helios","Helios Prime",
        "Nautilus","Nautilus Prime","Oxylius",
        "Shade","Shade Prime","Taxon","Wyrm","Wyrm Prime"
    ]]

robot = unique(robot)

# =========================
# COMPANION
# =========================
companion = [item(n) for n in [
    "Chesa Kubrow","Helminth Charger","Huras Kubrow",
    "Raksa Kubrow","Sahasa Kubrow","Sunika Kubrow",
    "Adarza Kavat","Smeeta Kavat","Vasca Kavat","Venari",
    "Vizier Predasite","Pharaoh Predasite","Medjay Predasite",
    "Panzer Vulpaphyla","Crescent Vulpaphyla","Sly Vulpaphyla"
]]

# =========================
# VEHICLE
# =========================
vehicle = [item(n) for n in [
    "Amesha","Elytron","Itzal","Odonata","Odonata Prime",
    "Bonewidow","Voidrig"
]]

# =========================
# ARCH
# =========================
archgun = [item(n) for n in [
    "Grattler","Velocitus","Fluctus","Corvas","Imperator",
    "Imperator Vandal","Kuva Grattler","Larkspur","Larkspur Prime",
    "Mausolon","Morgha","Prisma Dual Decurion","Phaedra"
]]

archmelee = [item(n) for n in [
    "Centaur","Kaszas","Onorix","Prisma Veritux","Rathbone","Veritux"
]]

amp = [item(n) for n in [
    "Raplak Prism","Shwaak Prism","Granmu Prism",
    "Rahm Prism","Cantic Prism","Propa Scaffold",
    "Shraksun Scaffold","Phahd Scaffold","Klamora Prism"
]]

# =========================
# BUILD
# =========================
data = [
    {"name": "Warframe", "items": wf},
    {"name": "Primary", "items": primary},
    {"name": "Secondary", "items": secondary},
    {"name": "Melee", "items": melee},
    {"name": "Robot", "items": robot},
    {"name": "Companion", "items": companion},
    {"name": "Vehicle", "items": vehicle},
    {"name": "Archgun", "items": archgun},
    {"name": "Archmelee", "items": archmelee},
    {"name": "Amp", "items": amp}
]

# =========================
# SAVE
# =========================
with open("data.js", "w", encoding="utf-8") as f:
    f.write("const data = ")
    json.dump(data, f, indent=2, ensure_ascii=False)

# =========================
# SUMMARY
# =========================
print("\n===== SUMMARY =====")
total = 0
for cat in data:
    count = len(cat["items"])
    total += count
    print(f"{cat['name']:12} : {count}")

print("----------------------")
print(f"TOTAL         : {total}")
print("✅ เสร็จแล้ว")