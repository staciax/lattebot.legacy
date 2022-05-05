import discord
from .useful import JSON
from enum import Enum
# https://github.com/colinhartigan/

base_endpoint: str = "https://pd.{shard}.a.pvp.net"
base_endpoint_glz: str = "https://glz-{region}-1.{shard}.a.pvp.net"
base_endpoint_shared: str = "https://shared.{shard}.a.pvp.net"

regions: list = ["na","eu","latam","br","ap","kr","pbe"]
region_shard_override: dict = {
    "latam":"na",
    "br":"na",
}
shard_region_override: dict = {
    "pbe": "na"
}

queues: list = ["competitive", "custom", "deathmatch", "ggteam", "snowball", "spikerush", "unrated", "onefa", "null"]

class QueueID(Enum):
    COMPETITIVE = 'competitive'
    CUSTOM = 'custom'
    DEATHMATCH = 'deathmatch'
    ESCALATION = 'ggteam'
    BREEZE = 'newmap'
    REPLICATION = 'onefa'
    SNOWBALL_FIGHT = 'snowball'
    SPIKE_RUSH = 'spikerush'
    UNRATED = 'unrated'

    def __str__(self):
        return self.value

# ---- EMOJI ---- #

agents_emoji: dict = {   
    'Astra': '<:Astra:950348653879525417>',
    'Breach': '<:Breach:950347788351328276>', 
    'Brimstone': '<:Brimstone:950348720086581278>',
    'Chamber': '<:Chamber:950347945625149470>', 
    'Cypher': '<:Cypher:950348163867373578>',
    'Fade': '<:Fade:969409084166123551>',
    'Jett': '<:Jett:950349017945112646>',
    'KAY/O': '<:KAYO:950348029939023912>',
    'Killjoy': '<:Killjoy:950348324941225985>',
    'Neon': '<:Neon:950348759953473557>', 
    'Omen': '<:Omen:950348966619410484>', 
    'Phoenix': '<:Phoenix:950348575265681458>', 
    'Raze': '<:Raze:950347842663370792>', 
    'Reyna': '<:Reyna:950348931995414538>', 
    'Sage': '<:Sage:950348864722960404>', 
    'Skye': '<:Skye:950348072041480252>', 
    'Sova': '<:Sova:950348215159500850>', 
    'Viper': '<:Viper:950348511856193596>', 
    'Yoru': '<:Yoru:950348813116248094>'
}

# class AgentID(Enum):
#     Astra = '41fb69c1-4189-7b37-f117-bcaf1e96f1bf'
#     Breach = '5f8d3a7f-467b-97f3-062c-13acf203c006'
#     Brimstone = '9f0d8ba9-4140-b941-57d3-a7ad57c6b417'
#     Chamber = '22697a3d-45bf-8dd7-4fec-84a9e28c69d7'
#     Cypher = '117ed9e3-49f3-6512-3ccf-0cada7e3823b'
#     Fade = 'dade69b4-4f5a-8528-247b-219e5a1facd6'
#     Jett = 'add6443a-41bd-e414-f6ad-e58d267f4e95'
#     KAYO = '601dbbe7-43ce-be57-2a40-4abd24953621'
#     Killjoy = '1e58de9c-4950-5125-93e9-a0aee9f98746'
#     Neon = 'bb2a4828-46eb-8cd1-e765-15848195d751'
#     Omen = '8e253930-4c05-31dd-1b6c-968525494517'
#     Phoenix = 'eb93336a-449b-9c1b-0a54-a891f7921d69'
#     Raze = 'f94c3b30-42be-e959-889c-5aa313dba261'
#     Reyna = 'a3bfb853-43b2-7238-a4f1-ad90e9e46bcc'
#     Sage = '569fdd95-4d10-43ab-ca70-79becc718b46'
#     Skye = '6f2a04ca-43e0-be17-7f36-b3908627744d'
#     Sova = '320b2a48-4d9b-a075-30f1-1f93a9b638fa'
#     Viper = '707eab51-4836-f488-046a-cda6bf494859'
#     Yoru = '7f94d92c-4234-0a36-9646-3a87eb8b5c89'

#     def __str__(self) -> str:
#         return self.value

AgentID = {
    'Astra': '41fb69c1-4189-7b37-f117-bcaf1e96f1bf',
    'Breach': '5f8d3a7f-467b-97f3-062c-13acf203c006',
    'Brimstone': '9f0d8ba9-4140-b941-57d3-a7ad57c6b417',
    'Chamber': '22697a3d-45bf-8dd7-4fec-84a9e28c69d7',
    'Cypher': '117ed9e3-49f3-6512-3ccf-0cada7e3823b',
    'Fade': 'dade69b4-4f5a-8528-247b-219e5a1facd6',
    'Jett': 'add6443a-41bd-e414-f6ad-e58d267f4e95',
    'KAY/O': '601dbbe7-43ce-be57-2a40-4abd24953621',
    'Killjoy': '1e58de9c-4950-5125-93e9-a0aee9f98746',
    'Neon': 'bb2a4828-46eb-8cd1-e765-15848195d751',
    'Omen': '8e253930-4c05-31dd-1b6c-968525494517',
    'Phoenix': 'eb93336a-449b-9c1b-0a54-a891f7921d69',
    'Raze': 'f94c3b30-42be-e959-889c-5aa313dba261',
    'Reyna': 'a3bfb853-43b2-7238-a4f1-ad90e9e46bcc',
    'Sage': '569fdd95-4d10-43ab-ca70-79becc718b46',
    'Skye': '6f2a04ca-43e0-be17-7f36-b3908627744d',
    'Sova': '320b2a48-4d9b-a075-30f1-1f93a9b638fa',
    'Viper': '707eab51-4836-f488-046a-cda6bf494859',
    'Yoru': '7f94d92c-4234-0a36-9646-3a87eb8b5c89'
}

ranks: dict = {
    '0': {'name': 'Unranked', 'emoji': '<:unranked:950360601991970866>'}, 
    '1': {'name': 'Unused1', 'emoji': None},
    '2': {'name': 'Unused2', 'emoji': None},
    '3': {'name': 'Iron 1', 'emoji': '<:iron1:950360602444988427>'},
    '4': {'name': 'Iron 2', 'emoji': '<:iron2:950360603405463593>'},
    '5': {'name': 'Iron 3', 'emoji': '<:iron3:950360604491792424>'}, 
    '6': {'name': 'Bronze 1', 'emoji': '<:bronze1:950360605443895306>'}, 
    '7': {'name': 'Bronze 2', 'emoji': '<:bronze2:950360605867528216>'}, 
    '8': {'name': 'Bronze 3', 'emoji': '<:bronze3:950360606836408340>'}, 
    '9': {'name': 'Silver 1', 'emoji': '<:silver1:950360607713009694>'}, 
    '10': {'name': 'Silver 2', 'emoji': '<:silver2:950360608002437191>'}, 
    '11': {'name': 'Silver 3', 'emoji': '<:silver3:950360611391418428>'}, 
    '12': {'name': 'Gold 1', 'emoji': '<:gold1:950360617246683146>'}, 
    '13': {'name': 'Gold 2', 'emoji': '<:gold2:950360618093924462>'}, 
    '14': {'name': 'Gold 3', 'emoji': '<:gold3:950360619062804540>'}, 
    '15': {'name': 'Platinum 1', 'emoji': '<:platinum1:950360619717103627>'}, 
    '16': {'name': 'Platinum 2', 'emoji': '<:platinum2:950360621097037874>'}, 
    '17': {'name': 'Platinum 3', 'emoji': '<:platinum3:950360621772341258>'}, 
    '18': {'name': 'Diamond 1', 'emoji': '<:diamond1:950360622502137856>'}, 
    '19': {'name': 'Diamond 2', 'emoji': '<:diamond2:950360623420674048>'}, 
    '20': {'name': 'Diamond 3', 'emoji': '<:diamond3:950360624460857395>'}, 
    '21': {'name': 'Immortal 1', 'emoji': '<:immortal1:950360625882738708>'}, 
    '22': {'name': 'Immortal 2', 'emoji': '<:immortal2:950360627111673916>'}, 
    '23': {'name': 'Immortal 3', 'emoji': '<:immortal3:950360628172845106>'}, 
    '24': {'name': 'Radiant', 'emoji': '<:radiant:950362888055447562>'}
}

tiers: dict = {
    '0cebb8be-46d7-c12a-d306-e9907bfc5a25': {'name':'Deluxe', 'emoji':'<:Deluxe:950372823048814632>', 'color': 0x009587},
    'e046854e-406c-37f4-6607-19a9ba8426fc': {'name':'Exclusive', 'emoji':'<:Exclusive:950372911036915762>', 'color': 0xf1b82d},
    '60bca009-4182-7998-dee7-b8a2558dc369': {'name':'Premium', 'emoji':'<:Premium:950376774620049489>', 'color': 0xd1548d},
    '12683d76-48d7-84a3-4e09-6985794f0445': {'name':'Select', 'emoji':'<:Select:950376833982021662>', 'color': 0x5a9fe2},
    '411e4a55-4e59-7757-41f0-86a53f101bb5': {'name':'Ultra', 'emoji':'<:Ultra:950376896745586719>', 'color': 0xefeb65}
}


maps: dict = {
    '/Game/Maps/Ascent/Ascent': 'Ascent',
    '/Game/Maps/Duality/Duality': 'Bind',
    '/Game/Maps/Foxtrot/Foxtrot': 'Breeze',
    '/Game/Maps/Bonsai/Bonsai': 'Split',
    '/Game/Maps/Canyon/Canyon': 'Fracture',
    '/Game/Maps/Port/Port': 'Icebox',
    '/Game/Maps/Triad/Triad': 'Haven',
    '/Game/Maps/Poveglia/Range': 'The Range'
}

class MapID(Enum):
    Asent = '/Game/Maps/Ascent/Ascent'
    Bind = '/Game/Maps/Duality/Duality'
    Breeze = '/Game/Maps/Foxtrot/Foxtrot'
    Split = '/Game/Maps/Bonsai/Bonsai'
    Fracture = '/Game/Maps/Canyon/Canyon'
    Icebox = '/Game/Maps/Port/Port'
    Haven = '/Game/Maps/Triad/Triad'
    Range = '/Game/Maps/Poveglia/Range'

    def __str__(self):
        return self.value

points: dict = {
    'vp':'<:ValorantPoint:950365917613817856>',
    'rad':'<:RadianitePoint:970261814157910066>'
}

def get_item_type(uuid: str):
    """Get item type"""
    item_type = {
        '01bb38e1-da47-4e6a-9b3d-945fe4655707': 'Agents',
        'f85cb6f7-33e5-4dc8-b609-ec7212301948': 'Contracts',
        'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475': 'Sprays',
        'dd3bf334-87f3-40bd-b043-682a57a8dc3a': 'Gun Buddies',
        '3f296c07-64c3-494c-923b-fe692a4fa1bd': 'Player Cards',
        'e7c63390-eda7-46e0-bb7a-a6abdacd2433': 'Skins',
        '3ad1b2b2-acdb-4524-852f-954a76ddae0a': 'Skins chroma',
        'de7caa6b-adf7-4588-bbd1-143831e786c6': 'Player titles'
    }
    return item_type.get(uuid, uuid)

def get_emoji_tier(skin_uuid) -> discord.Emoji:
    data = JSON.read('cache')
    uuid = data['skins'][skin_uuid]['tier']
    uuid = data['tiers'][uuid]['uuid']
    emoji = tiers[uuid]['emoji']
    return emoji