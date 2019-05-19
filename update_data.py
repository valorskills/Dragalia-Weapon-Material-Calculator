#!/usr/bin/python
# jtbib: this is all derived from the README, provided by original author yujinred
import os
import sys
from pprint import pformat
import requests
import urllib.request
import time
import re

LOAD_WEAPON_DATA=True
LOAD_WEAPON_IMGS=False # NOTE: these are not optimized and might download more than necessary!
LOAD_MISSING_MAT_IMGS=True
THROTTLE_DELAY=0.5 # seconds delay between downloads


if LOAD_WEAPON_DATA:
    print("Loading weapon data")
    # Note: previously had rarity > 2, but you still need that data for some void weapons '&where=Rarity%3E2'
    # adding filter to index.html instead
    WEAPON_DATA_URL="https://dragalialost.gamepedia.com/api.php?action=cargoquery&format=json&limit=max&tables=Weapons&fields=Id%2C+BaseId%2C+FormId%2C+WeaponName%2C+Type%2C+Rarity%2C+ElementalType%2C+MinHp%2C+MaxHp%2C+MinAtk%2C+MaxAtk%2C+VariationId%2C+DecBaseId%2C+DecVariationId%2C+BulletBaseId%2C+BulletVariationId%2C+Skill%2C+SkillName%2C+SkillDesc%2C+IsPlayable%2C+FlavorText%2C+SellCoin%2C+SellDewPoint%2C+CraftNodeId%2C+ParentCraftNodeId%2C+CraftGroupId%2C+FortCraftLevel%2C+AssembleCoin%2C+DisassembleCoin%2C+DisassembleCost%2C+MainWeaponId%2C+MainWeaponQuantity%2C+CraftMaterialType1%2C+CraftMaterial1%2C+CraftMaterialQuantity1%2C+CraftMaterialType2%2C+CraftMaterial2%2C+CraftMaterialQuantity2%2C+CraftMaterialType3%2C+CraftMaterial3%2C+CraftMaterialQuantity3%2C+CraftMaterialType4%2C+CraftMaterial4%2C+CraftMaterialQuantity4%2C+CraftMaterialType5%2C+CraftMaterial5%2C+CraftMaterialQuantity5"
    WEAPON_DATA_OUTPUT="weapon_data.js"
    WEAPON_DATA_VAR="weapons"

    # MATERIAL_DATA_URL="https://dragalialost.gamepedia.com/api.php?action=cargoquery&format=json&limit=max&tables=Materials&fields=Id%2C+Name%2C+Obtain+"
    # MATERIAL_DATA_OUTPUT="material_data.js"
    # MATERIAL_DATA_VAR="materials"
    # better url: https://dragalialost.gamepedia.com/api.php?action=cargoquery&format=json&limit=max&tables=Materials&fields=Id%2C+Name%2C+Description

    JS_PARAMS=[
    (WEAPON_DATA_URL, WEAPON_DATA_OUTPUT, WEAPON_DATA_VAR),
    # edit 5/18/2019 don't use these as it causes other issues. it's tough to acquire the required images for source quests.
    #(MATERIAL_DATA_URL, MATERIAL_DATA_OUTPUT, MATERIAL_DATA_VAR)
    ]

    for (url, outputfile, var) in JS_PARAMS:
        with open(outputfile, 'w+') as f:
            json = requests.get(url).json()
            data = [x["title"] for x in json["cargoquery"]]
            data_str = str(data) 
            # jtbib note: pformat will break up long strings (flavortext) by default :( width param doesn't help
            # data_str = pformat(data, width=sys.maxsize)
            f.write('{} = {};'.format(var, data_str))


if LOAD_WEAPON_IMGS:
    print("Loading weapon images")
    # jtbib: added an end for this which corresponds to the first non-weapon image I found. it'll download one extra but that's ok.
    WEAPON_IMG_URL="https://dragalialost.gamepedia.com/api.php?action=query&format=json&prop=&list=allimages&aifrom=301001_01_19901.png&aito=3100001.png&aiprop=timestamp%7Curl&ailimit=max"
    WEAPON_IMG_DIR="images/weapons"



    json = requests.get(WEAPON_IMG_URL).json()
    for img_json in json['query']['allimages']:
        filename = '{}/{}'.format(WEAPON_IMG_DIR, img_json['name'])
        img_url = img_json['url']
        if os.path.isfile(filename):
            #print("Skipping file: " + filename)
            pass
        else:
            print("Downloading file: " + filename)
            urllib.request.urlretrieve(img_url, filename)
            time.sleep(THROTTLE_DELAY) # to avoid overloading gamepedia


if LOAD_MISSING_MAT_IMGS:
    print("Loading material images")
    # jtbib: didn't modify this url, but it does stop at an HMS portrati which definitely isn't required.
    # the start range is also not required (sunstones). I'm not actually sure how the existing images were chosen if not manually.
    # either way, this is generally not required for download
    MATERIAL_IMG_URL="https://dragalialost.gamepedia.com/api.php?action=query&format=json&prop=&list=allimages&aiprop=timestamp%7Curl&ailimit=max&aifrom={}&aito={}&*"
    MATERIAL_IMG_DIR="images/materials"

    BASE_IMG_FILE_URL="https://dragalialost.gamepedia.com/File:{}"
    # https://dragalialost.gamepedia.com/api.php?action=query&format=json&prop=&list=allimages&aiprop=timestamp%7Curl&ailimit=max&aifrom=111001001.png&aito=210001_01.png&*
    # json = requests.get(MATERIAL_IMG_URL).json()['query']['allimages']
    regex = re.compile('\s*"Id":\s*"(\d+)",.*')
    missing_imgs=[]
    with open('material_data.js') as f:
        for line in f:
            match = regex.search(line)
            if match:
                target_img='{}.png'.format(match.group(1))
                target_path='{}/{}'.format(MATERIAL_IMG_DIR, target_img)
                if os.path.isfile(target_path):
                    #print("Skipping file: " + target_path)
                    pass
                else:
                    missing_imgs += [target_img]
                    # print("Downloading file: " + target_path)
                    # target_url=BASE_IMG_FILE_URL.format(target_img)
                    # urllib.request.urlretrieve(target_url, target_path)
                    # time.sleep(THROTTLE_DELAY) # to avoid overloading gamepedia
    
    if missing_imgs:
        search_url = MATERIAL_IMG_URL.format(min(missing_imgs), max(missing_imgs))
        json = requests.get(search_url).json()
        for img_json in json['query']['allimages']:
            name = img_json['name']
            if name in missing_imgs:
                filename = '{}/{}'.format(MATERIAL_IMG_DIR, name)
                img_url = img_json['url']
                print("Downloading file: " + filename)
                urllib.request.urlretrieve(img_url, filename)
                time.sleep(THROTTLE_DELAY) # to avoid overloading gamepedia





# TO GENERATE BASE_64 DATA:
# rm weapon_base64.txt; for x in `ls -1 images/weapons/*`; do echo $x:"`base64 $x`" >> weapon_base64.txt ; done
# rm material_base64.txt; for x in `ls -1 images/materials/*`; do echo $x:"`base64 $x`" >> material_base64.txt ; done

# you'll want to manually copy these into dictionaries somehow