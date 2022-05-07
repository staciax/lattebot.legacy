from enum import Enum

# ----- BADGE CONVERTER ----- #

def profile_converter(name: str) -> str:
  names_to_emojis = {
    "staff" : "<:staff:893347826036265061>",
    "partner" : "<:partner:893346589521870888>",
    "hypesquad" : "<:hypesquad:893346589417042021>",
    "bug_hunter" : "<:bug_hunter:893346589861621830>",
    "hypesquad_bravery" : "<:bravery:893346589198929941>",
    "hypesquad_brilliance" : "<:brillance:893346589538652230>",
    "hypesquad_balance" : "<:balance:893346589345738763>", 
    "early_supporter" : "<:early_supporter:893346589769334844>",
    "system" : "<:system_badge:893351489366540318>",
    "bug_hunter_level_2" : "<:bug_hunter_level_2:893346589559636009>",
    "verified_bot" : "<:verified_bot1:893349183812165656><:verified_bot2:893349211293253662>",
    "verified_bot_developer" : "<:verified_bot_developer:893350052800651276>",
    "early_verified_bot_developer" : "<:early_verified_bot_developer:893350037847965756>",
    "discord_certified_moderator" : "<:certified_moderator:893350659410251817>",
    "bot" : "<:bot_1:893349778346348544><:bot_2:893349787175378944>",
    "guildboost" : "<:boost:893356419192082484><:nitro:893346589337329735>",
    "nitro" : "<:nitro:893346589337329735>",   
  }
  return names_to_emojis.get(name)


# ----- STATUS INFO ----- #

def status_converter(name: str) -> str:
  names_to_status = {
    "online" : "<:online:896657842298310686>",
    "dnd" : "<:dnd:896657867246030888>",
    "idle" : "<:idle:896657886111989761>",
    "offline" : "<:offline:896657913291096074>",
  }
  return names_to_status.get(name)

# ----- EMOJI CONVERTER ----- #

def latte_emoji(name: str) -> str:
  names_to_emojis = {
    "member" : "<:member:904565339835232276>",
    "purplestar":"<a:purplestar:902673752976941066>",
    "purpleflower":"<:purpleflower:902672657881907260>",
    "cursor":"<a:cursor:896576387002032159>",
    "command":"<:bot_commands:902669882552881162>",
    "brownjump":"<a:brownjump:902686897439121428>",
    "greentick":"<:greentick:902669964174049343>",
    "redtick":"<:redtick:902669996960919552>",
    "sleeping":"<a:sleeping:902960651272589363>",
    "spotify":"<:Spotify:904418859937828874>",
    "latte_icon":"<:latte_icon_new:907030425011109888>",
    "mongo":"<:mongo:904509654086864917>",
    "python":"<:python:904565441761017907>",
    "bot_commands":"<:bot_commands:904565707981852723>",
    "dpy":"<:dpy:904565466633211925>",
    "postgresql":"<:postgresql:908211369743122443>",
    'py-cord': '<:pycord_icon:948811595998453841>',
    'game':'<:game:966129467653259324>',
    'youtube':'<:youtube1:966131531926089789>'

  }
  return names_to_emojis.get(name)

class LATTE_EMOJI(Enum):
  MEMBER = "<:member:904565339835232276>"
  PURPLESTAR = "<a:purplestar:902673752976941066>"
  PURPLEFLOWER = "<:purpleflower:902672657881907260>"
  CURSOR = "<a:cursor:896576387002032159>"
  COMMAND = "<:bot_commands:902669882552881162>"
  BROWNJUMP = "<a:brownjump:902686897439121428>"
  GREENTICK = "<:greentick:902669964174049343>"
  REDTICK = "<:redtick:902669996960919552>"
  SLEEPING = "<a:sleeping:902960651272589363>"
  SPOTIFY = "<:Spotify:904418859937828874>"
  LATTE_ICON = "<:latte_icon_new:907030425011109888>"
  MONGO = "<:mongo:904509654086864917>"
  PYTHON = "<:python:904565441761017907>"
  BOT_COMMANDS = "<:bot_commands:904565707981852723>"
  DPY = "<:dpy:904565466633211925>"
  POSTGRESQL = "<:postgresql:908211369743122443>"
  PYCORD = '<:pycord_icon:948811595998453841>'
  GAME = '<:game:966129467653259324>'
  YOUTUBE = '<:youtube1:966131531926089789>'
  LATTE_SUPPORT = '<:latte_support:941971854728511529>'
  MOLANG_COFFEE = '<:Molang_coffee:840678426867793921>'
  MISC = '<:misc:914142887854358588>'
  MIKU_MUSIC = '<:MikuMusic:958861859161767987>'
  LOVE_NOTE = '<:love_note:909498501799505930>'
  GIFT_BLUE = '<:gift_blue:903339694098628618>'
  VALORANT = '<:valorant_icon:955743009138429962>'
  LATTE = '<:a_latte_verify:861800747293212672>'
  MOD = '<:mod:970838278318211133>'
  JISHAKU = '<:jishaku_logo:972345525129060362>'
  STACIA = '<:stacia_icon:948850880617250837>'
  MOON = '<:Moon:969409166215102464>'
  RAIDEN = '<:chibiraidensmile:903361022943965215>'

  def __str__(self):
    return self.value