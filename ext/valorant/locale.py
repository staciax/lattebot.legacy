import json
import contextlib
from typing import Dict

Locale = {
    'en-US': 'en-US', # american_english /
    'en-GB': 'en-US', # british_english /
    'zh-CN': 'zh-CN', # chinese
    'zh-TW': 'zh-TW', # taiwan_chinese
    'fr'   : 'fr-FR', # french
    'de'   : 'de-DE', # german
    'it'   : 'it-IT', # italian
    'ja'   : 'ja-JP', # japanese
    'ko'   : 'ko-KR', # korean
    'pl'   : 'pl-PL', # polish
    'pt-BR': 'pt-BR', # portuguese_brazil
    'ru'   : 'ru-RU', # russian
    'es-ES': 'es-ES', # spanish
    'th'   : 'th-TH', # thai /
    'tr'   : 'tr-TR', # turkish
    'vi'   : 'vi-VN', # vietnamese
}

def InteractionLanguage(local_code: str) -> str:
    return Locale.get(str(local_code), 'en-US')

def LocalRead(filename: str) -> Dict:
    data = {}
    try:
        with open(f"ext/valorant/languages/{filename}.json", "r", encoding='utf-8') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        return LocalRead('en-US')
    return data

def LocaleResponse(command_name: str, local_code: str) -> Dict:
    local_code = __verify_localcode(local_code)
    locale = {}
    with contextlib.suppress(KeyError):
        local_dict = LocalRead(local_code)
        locale = local_dict['commands'][str(command_name)]
    return locale

def LocaleErrorResponse(value: str, local_code: str) -> Dict:
    local_code = __verify_localcode(local_code)
    locale = {}
    with contextlib.suppress(KeyError):
        local_dict = LocalRead(local_code)
        locale = local_dict['errors'][value]
    return locale

# def LocaleErrorResponseTesting(values: str, local_code: str) -> Dict:
#     """
#     NOTE: example values: `AUTH.LOGIN_ERROR`
#     """
#     local_code = __verify_localcode(local_code)
#     locale = {}
#     value = values.split('.')
#     with contextlib.suppress(KeyError):
#         local_dict = LocalRead(local_code)
#         locale = local_dict['errors'][value[0]][value[1]]
#     return locale
    
def __verify_localcode(local_code: str) -> str:
    if local_code in ['en-US', 'en-GB']:
        return 'en-US'
    return local_code