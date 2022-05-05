# Standard 
import discord
from io import BytesIO

# Third
import requests
from PIL import Image, ImageDraw, ImageFont

def generate_image(skin_list):
    
    # background
    background = Image.open('ext/valorant/assets/bg.png')
    draw = ImageDraw.Draw(background)
    vp_png = Image.open('ext/valorant/assets/vp.png').resize([65, 65]).convert('RGBA')

    deluxe_icon = Image.open('ext/valorant/assets/Deluxe.png').resize([90, 90]).convert('RGBA')
    exclusive_icon = Image.open('ext/valorant/assets/Exclusive.png').resize([90, 90]).convert('RGBA')
    premium_icon = Image.open('ext/valorant/assets/Premium.png').resize([90, 90]).convert('RGBA')
    select_icon = Image.open('ext/valorant/assets/Select.png').resize([90, 90]).convert('RGBA')
    ultra_icon = Image.open('ext/valorant/assets/Ultra.png').resize([90, 90]).convert('RGBA')

    # font
    font_ = "ext/valorant/assets/Inter-Bold.ttf"
    font_size = ImageFont.FreeTypeFont(font_, 40)
    color_text = '#ffffff'

    def get_tier(url):
        uuid = url.split('/')[4]
        tier_data = {
            '60bca009-4182-7998-dee7-b8a2558dc369': {'color':'#382536', 'file': premium_icon},
            'e046854e-406c-37f4-6607-19a9ba8426fc': {'color':'#3d3823', 'file': exclusive_icon},
            '0cebb8be-46d7-c12a-d306-e9907bfc5a25': {'color':'#0d3135', 'file': deluxe_icon},
            '12683d76-48d7-84a3-4e09-6985794f0445': {'color':'#1f3347', 'file': select_icon},
            '411e4a55-4e59-7757-41f0-86a53f101bb5': {'color':'#3e422e', 'file': ultra_icon}
        }
        data = tier_data[uuid]
        return data
    
    skin_1 = skin_list['skin1']
    skin_2 = skin_list['skin2']
    skin_3 = skin_list['skin3']
    skin_4 = skin_list['skin4']

    skin_tier_1 = get_tier(skin_1['tier'])
    skin_tier_2 = get_tier(skin_2['tier'])
    skin_tier_3 = get_tier(skin_3['tier'])
    skin_tier_4 = get_tier(skin_4['tier'])

    # draw text backgrond
    draw.rounded_rectangle((30, 25, 535, 435), fill=skin_tier_1.get('color'), radius=15)
    draw.rounded_rectangle((570, 25, 1070, 435), fill=skin_tier_2.get('color'), radius=15)
    draw.rounded_rectangle((30, 470, 535, 880), fill=skin_tier_3.get('color'), radius=15)
    draw.rounded_rectangle((570, 470, 1070, 880), fill=skin_tier_4.get('color'), radius=15)

    # draw valorant point icon
    background.paste(vp_png, (340, 55), mask=vp_png)
    background.paste(vp_png, (880, 55), mask=vp_png)
    background.paste(vp_png, (340, 495), mask=vp_png)
    background.paste(vp_png, (880, 495), mask=vp_png)

    # draw skin price
    draw.text((420, 63), str(skin_1['price']), font=font_size, fill=color_text, align='left')    
    draw.text((960, 63), str(skin_2['price']), font=font_size, fill=color_text, align='left')
    draw.text((420, 505), str(skin_3['price']), font=font_size, fill=color_text, align='left')
    draw.text((960, 505), str(skin_2['price']), font=font_size, fill=color_text, align='left')

    # draw tier icon
    background.paste(skin_tier_1.get('file'), (46, 42), skin_tier_1.get('file'))
    background.paste(skin_tier_2.get('file'), (585, 42), skin_tier_2.get('file'))
    background.paste(skin_tier_3.get('file'), (46, 484), skin_tier_3.get('file'))
    background.paste(skin_tier_4.get('file'), (585, 484), skin_tier_4.get('file'))

    # draw skin name
    spacing_1 = 355
    for line in reversed(skin_1['name'].split(" ")):
        draw.text((60, spacing_1), line.upper(), fill = color_text, font=font_size)
        spacing_1 -= 43

    spacing_2 = 355
    for line in reversed(skin_2['name'].split(" ")):
        draw.text((600, spacing_2), line.upper(), fill = color_text, font=font_size)
        spacing_2 -= 43

    spacing_3 = 795
    for line in reversed(skin_3['name'].split(" ")):
        draw.text((60, spacing_3), line.upper(), fill = color_text, font=font_size)
        spacing_3 -= 43

    spacing_4 = 795
    for line in reversed(skin_4['name'].split(" ")):
        draw.text((600, spacing_4), line.upper(), fill = color_text, font=font_size)
        spacing_4 -= 43

    # fetch skin icon
    skin1 = requests.get(skin_1['icon'])
    skin2 = requests.get(skin_2['icon'])
    skin3 = requests.get(skin_3['icon'])
    skin4 = requests.get(skin_4['icon'])

    # skin icon to file
    skin1_png = Image.open(BytesIO(skin1.content)).rotate(angle=-45, expand=True, center=(255,90))
    skin2_png = Image.open(BytesIO(skin2.content)).rotate(angle=-45, expand=True, center=(255,90))
    skin3_png = Image.open(BytesIO(skin3.content)).rotate(-45, expand=True, center=(255,90))
    skin4_png = Image.open(BytesIO(skin4.content)).rotate(-45, expand=True, center=(255,90))

    # draw skin icon
    background.paste(skin1_png,(45, -20), skin1_png)
    background.paste(skin2_png,(580, -20), skin2_png)
    background.paste(skin3_png,(45, 430), skin3_png)
    background.paste(skin4_png, (580, 430), skin4_png)

    buffer = BytesIO()
    background.save(buffer, 'png')
    # background.show()
    buffer.seek(0)
    file=discord.File(buffer, filename='store-offers.png')
    return file