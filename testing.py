import math

def simulation(number : int):
    """
    example
    1 = 10
    11 = 20
    21 = 30
    31 = 40
    41 = 50

    121 = 124
    """
    return math.ceil(number / 10) * 10

print(simulation(121))











# # from cryptography.fernet import Fernet
# # key = Fernet.generate_key()
# # f = Fernet(key)
# # token = f.encrypt(b"my deep dark secret")
# # print(token)

# import sys

# if sys.version_info < (3, 0):
#     from urllib2 import urlopen
# else:
#     from urllib.request import urlopen

# import io

# from colorthief import ColorThief


# fd = urlopen('http://lokeshdhakar.com/projects/color-thief/img/photo1.jpg')
# f = io.BytesIO(fd.read())
# color_thief = ColorThief(f)
# print(color_thief.get_color(quality=1))
# print(color_thief.get_palette(quality=1))




# text = 'test\ntest\ntest\ntest\ntest\ntest\ntest\n'

# print(text.splitlines())



    # #@valorant.command(name='Account Data')
    # async def account_data(self, name: str, tag: str) -> None:
    #     # /valorant/v1/account/:name/:tag
    #     ...

    # async def mmr_data(self, name: str, tag:str, region: Literal['AP', 'EU', 'NA', 'KR'], api_version: Literal['1','2']) -> None:
    #     # /valorant/:version/mmr/:name/:tag
    #     ...

    # async def mmr_by_puuid(self, puuid: str, region: Literal['AP', 'EU', 'NA', 'KR'], api_version: Literal['1','2']) -> None:
    #     #  /valorant/:version/by-puuid/mmr/:region/:puuid
    #     ...

    # async def mmr_history(self, name: str, tag:str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/:version/by-puuid/mmr/:region/:puuid
    #     ...

    # async def mmr_history_puuid(self, puuid: str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/v1/by-puuid/mmr-history/:region/:puuid
    #     ...

    # async def match_history(self, name: str, tag:str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/v3/matches/:region/:name/:tag
    #     ...
    
    # async def match_history_puuid(self, puuid: str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/v3/by-puuid/matches/:region/:puuid
    
    #     ...
    # async def match_data(self, match_id: str) -> None:
    #     #  /valorant/v2/match/:matchid
    #     ...

    # async def website_articles(region):
    #     # en-us, en-gb, de-de, es-es fr-fr it-it ru-ru tr-tr es-MX ja-jp ko-kr pt-br
    #     # /valorant/v1/website/:country-code
    #     ...

    # async def server_status(region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     # /valorant/v1/status/:region
    #     ...
    
    # async def content():
    #     ...
    #     # https://api.henrikdev.xyz/valorant/v1/content
    #     # /valorant/v1/content


    # @valorant.command()
    # @app_commands.describe(bundle='Bundle name')
    # async def bundle(self, interaction: Interaction, bundle: Optional[str]) -> None:
    #     """Shows current bundle or search for bundle"""

    #     bundles = data_read('bundles')
    #     bundles_list = [bundles['bundles'][x]['name'] for x in bundles['bundles']]

    #     filter_bundle = get_close_matches(bundle, bundles_list, 1)

    #     def embed_bundle(name:str, icon: str, type: str) -> discord.Embed:
            
    #         buddy_price = 475
    #         spray_price = 325
    #         card_price = 375

    #         embed = discord.Embed(
    #             description=f"{name}\n{points['vp']}",
    #         )
    #         embed.set_thumbnail(url=icon)
    #         return embed

    #     if filter_bundle:
    #         bundle = filter_bundle[0]

    #         embeds = []

    #         skins = filter_skin(bundle)
    #         sprays = filter_sprays(bundle)
    #         buddies = filter_buddies(bundle)
    #         playercards = filter_playercards(bundle)

    #         for skin in skins:
    #             embed = embed_bundle(skin['name'], skin['icon'])
    #             embeds.append(embed)
            
    #         for spray in sprays:
    #             embed = embed_bundle(spray['name'], spray['icon'])
    #             embeds.append(embed)
            
    #         for buddy in buddies:
    #             embed = embed_bundle(buddy['name'], buddy['icon'])
    #             embeds.append(embed)
            
    #         for playercard in playercards:
    #             embed = embed_bundle(playercard['name'], playercard['icon'])
    #             embeds.append(embed)
            
    #         embeds = [embed for embed in list(embeds)]

    #         await interaction.response.send_message(embeds=embeds)
    #         return

    #     raise RuntimeError('Bunndle Not Found')


# A_list = ["Aluminum", "Python", "Coding"]

# output = []

# for index, i in enumerate(sorted(A_list, reverse=True), start=1):
#     output.append(i[0])
#     output.append(str(index) + ". " + i)

# print(output)
# import re
# import json
# import random
# from datetime import datetime

# from ext.valorant.useful import JSON
# from ext.valorant.cache import fetch_mission


# new_header = {'Authorization': f'Bearer testing', 'X-Riot-Entitlements-JWT': 'testing'}

# header = json.dumps(new_header)


# print(header)
# def iso_to_timestamp(iso: datetime):
#     timestamp = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S%z").timestamp()
#     return int(timestamp)

# fetch_mission()

# missions = JSON.read('missions')
# mission_data = missions['missions']

# fetch_mission()
# mission_future = {}

# count = 0
# for mission in mission_data:
#     start_time = mission_data[mission]['start']
#     if start_time > datetime.timestamp(datetime.utcnow()):
#         insert = mission_future.get(start_time, None)
#         if insert is None:
#             mission_future[start_time] = [mission_data[mission]['titles']['en-US']]
#         else:
#             mission_future[start_time].append(mission_data[mission]['titles']['en-US'])
        
        # break
        # print(mission_data[mission]['start'])
# bundle = 'ar'

# language = 'en-US'
# default_language = 'en-US'

# # find bundle
# find_bundle = [cache['bundles'][i] for i in cache['bundles'] \
#     if bundle.lower() in cache['bundles'][i]['names'][default_language].lower() or \
#         # bundle.lower() in cache['bundles'][i]['names'][language].lower() or \
#             cache['bundles'][i]['names'][default_language].lower().startswith(bundle.lower())
# ]

# for bd in sorted(find_bundle, key=lambda c: c['names'][default_language]):
#     print(bd['uuid'])

# popular_skin =(
#         'prime', 'reaver', 'glitchpop', 'rgx', 'spectrum', 'magepunk',
#         'recon', 'sovereign', 'sentinels', 'blastx', 'ion', 'oni'
#     )
# tup = tuple(random.sample(popular_skin, len(popular_skin)))
# # random.shuffle(popular_skin)

# print(tup[:3])



# skindata = JSON.read('cache')
# skin_list = [skindata['skins'][x] for x in skindata['skins']]


# default_language = 'en-US'
# namespace = 'prime'
# namespace_split = str(namespace).lower().split()

# choice_list = {}


# # print(tuple(namespace_split))
# for skin in skin_list:
#     name: str = skin['names'][default_language]
#     name_split = name.split()
#     if name.lower().startswith(tuple(namespace_split)):
#         if len(namespace_split) > 1:
#             for item in name_split:
#                 if item.lower().startswith(namespace_split[1]):
#                     choice_list[name] = skin['uuid']
#         else:
#             choice_list[name] = skin['uuid']


# print(choice_list)
# listx = [x[1] for x in choice_list.items()]

# print(listx)


# import contextlib
# # language


# default_language = 'en-US'

# skindata = JSON.read('cache')
# skin_list = [skindata['skins'][x] for x in skindata['skins']]

# namespace = 'rgx fren'
# namespace_split = namespace.split()

# choice_list = {}

# for skin in skin_list:
#     name: str = skin['names'][default_language]
#     name_split = name.split()
#     with contextlib.suppress(IndexError):
#         if name.lower().startswith(namespace_split[0]):
#             if len(namespace_split) > 1:
#                 for item in name_split:
#                     if item.lower().startswith(namespace.split()[1]):
#                         choice_list[name] = skin['uuid']
#             else:
#                 choice_list[name] = skin['uuid']


# listx = [choice_list[skin['names'][default_language]] for skin in skin_list if skin['names'][default_language].lower().startswith(namespace_split[0]) ]



# return [app_commands.Choice(name=name, value=uuid) for name, uuid in sorted(choice_list.items(), key=lambda x: x[0])][:15]


# print(choice_list)


    # if name.find(namespace) != -1:
    #     print(name)


    # if re.search(f'^{name}', namespace):
    #     print(name)



    # if name.startswith(namespace):
    #     print(name)


    # if len(namespace) > 1:
    #     for i in name_split:
    #         print(i)
        
    # for i in namespace.split():
    #     print(i)
        # if i.startswith(tuple(name_split)) and not i.startswith('rgx'):
        #     print(name)
        # if i in name_split:
        #     print(i)
        #     print(name)

    

    # print(all([x for x in namespace_split]))
    # if all([x in name_split for x in namespace_split]):
    #     print(name)
    # if namespace in name_split:
    #     print(name)


# final = [skin['names'][default_language] for skin in sorted(skin_list, key=lambda c: c['names'][default_language]) \
    

#     # if namespace in skin['names'][default_language].lower() or \
#     #    [namespace[0] in skin['names'][default_language].lower() and skin['names'][default_language].lower().startswith(namespace)]
        
#     # if skin['names'][default_language].lower().split() in namespace.split()
#     # if any(xs in skin['names'][default_language].lower() for xs in namespace.split())
# ]

# print(final)

# import re
# from difflib import get_close_matches

# keyword = 'rgx z11'
# skin_list = ['rgx z11 pro phanthom', 'rgx z11 pro classic', 'prime vandal']

# keyword = ['rgx', 'phanthom']
# matching = [s for s in skin_list if any(xs in s for xs in keyword)]
# print(matching[0])


# keyword_split = keyword.split()

# for skin in skin_list:
#     skin_split = skin.split()
    # for keyword in keyword_split:
    #     if keyword in skin_split:
    #         print(skin)
    # if get_close_matches(keyword, list(skin)):
    #     print(skin)

    # skin_split = skin.split()
    # if bool(keyword_split.extend(skin_split)):
    #     print(skin)
# print(list(filter(lambda k: 'classic' in k, skin_list)))
    # skin_split = skin.split()
    # set_skin_split = set(skin_split)
    # set_keyword_split = set(keyword_split)
    # if len(set_skin_split.intersection(set_keyword_split)) != 0:
    #     print(skin)
    # if set(skin_split) & set(keyword_split):
    #     print(skin)

    # if keyword_split in skin_split:
    #     print(skin)

    # print(skin_split)
    # for word in keyword_split:
    #     if word in skin_split:
    #         print(skin)
            # break

    # str_match = list(filter(lambda x: 'rgx phanthom' in x, skin_list))
    # print(str_match)
    # key = keyword.split(' ')
    # if key in skin:
    #     print(skin)
    # if skin.find(keyword) != -1:
    #     print(skin)
    # if keyword.split(' '):
    #     # print(type(skin))
    #     # print(skin)
    #     # print('\n')
    #     print(keyword.lower())
    #     if skin.lower().find(keyword.lower()):
    #         print(skin)
    # if keyword in skin:
    #     print(skin)












#     'Astra': '41fb69c1-4189-7b37-f117-bcaf1e96f1bf',
#     'Breach': '5f8d3a7f-467b-97f3-062c-13acf203c006',
#     'Brimstone': '9f0d8ba9-4140-b941-57d3-a7ad57c6b417',
#     'Chamber': '22697a3d-45bf-8dd7-4fec-84a9e28c69d7',
#     'Cypher': '117ed9e3-49f3-6512-3ccf-0cada7e3823b',
#     'Fade': 'dade69b4-4f5a-8528-247b-219e5a1facd6',
#     'Jett': 'add6443a-41bd-e414-f6ad-e58d267f4e95',
#     'KAY/O': '601dbbe7-43ce-be57-2a40-4abd24953621',
#     'Killjoy': '1e58de9c-4950-5125-93e9-a0aee9f98746',
#     'Neon': 'bb2a4828-46eb-8cd1-e765-15848195d751',
#     'Omen': '8e253930-4c05-31dd-1b6c-968525494517',
#     'Phoenix': 'eb93336a-449b-9c1b-0a54-a891f7921d69',
#     'Raze': 'f94c3b30-42be-e959-889c-5aa313dba261',
#     'Reyna': 'a3bfb853-43b2-7238-a4f1-ad90e9e46bcc',
#     'Sage': '569fdd95-4d10-43ab-ca70-79becc718b46',
#     'Skye': '6f2a04ca-43e0-be17-7f36-b3908627744d',
#     'Sova': '320b2a48-4d9b-a075-30f1-1f93a9b638fa',
#     'Viper': '707eab51-4836-f488-046a-cda6bf494859',
#     'Yoru': '7f94d92c-4234-0a36-9646-3a87eb8b5c89'
# }


# for agent, uuid in AgentID.items():
#     print(agent)
#     print(uuid)



# # from enum import Enum 

# # class QueueID(Enum):
# #     COMPETITIVE = 'competitive'
# #     CUSTOM = 'custom'
# #     DEATHMATCH = 'deathmatch'
# #     ESCALATION = 'ggteam'
# #     BREEZE = 'newmap'
# #     REPLICATION = 'onefa'
# #     SNOWBALL_FIGHT = 'snowball'
# #     SPIKE_RUSH = 'spikerush'
# #     UNRATED = 'unrated'

# #     def __str__(self):
# #         return self.value


# # print(getattr(QueueID, 'COMPETITIVE'))

# # def get_value(values: str):
# #     values_strip = values.split('.')
# #     for i in values_strip:
# #         if i in MY_DICT:
# #             return MY_DICT[i]
# #         else:
# #             print('not found')
# #             return 'not found'
