########################################
### add_style_description_geojson.py ###
######## Author: Wei-Jhih Chen #########
########## Update: 2023/03/29 ##########
########################################

import os
import sys
import argparse
import json
from typing import Optional
from pathlib import Path
from pydantic.main import BaseModel

STYLES = {
    'color_line': '#ff0000' ,
    'fill_opacity': 0.5 ,
}
# TITLE_KEY = 'lslno'
INFILE = '112_大規模崩塌警戒發布區_20230324.geojson'

# STYLES = {
#     'color_line': '#ffff00' ,
#     'fill_opacity': 0.5 ,
# }
# # TITLE_KEY = 'Islno'
# INFILE = '112_大規模崩塌影響範圍_20230324.geojson'

TITLE_KEY = 'name'
PROPERTIES = {
    'Warn_type': '警戒類型',
    'Warn_value': '警戒值(mm)'
}
ADD_DESCRIPTION = True

HOMEDIR = Path(r'C:\Users\wjchen\Documents\QPEplus')
INDIR = HOMEDIR/'geojson'/'Agency'/'SWCB_collapse'
INPATH = INDIR/INFILE
OUTPATH = INDIR/INFILE

def load_json(path):
    with open(path , encoding = 'UTF-8') as f:
        data = json.load(f)
    return data


def save_json(path , data):
    with open(path , 'w' , encoding = 'UTF-8' , newline = '') as f:
        json.dump(data , f)


def add_feature_styles(data , styles):
    for cnt_f , feature in enumerate(data['features']):
        type = feature['type']
        properties = feature['properties']
        geometry = feature['geometry']
        data['features'][cnt_f] = {}
        data['features'][cnt_f]['type'] = type
        if styles:
            for style in styles:
                data['features'][cnt_f][style] = styles[style]
        data['features'][cnt_f]['properties'] = properties
        data['features'][cnt_f]['geometry'] = geometry
    return data


def add_feature_description_SWCB(data , properties , title_key: str = None):
    for feature in data['features']:
        feature['properties']['description'] = \
            f"<table align=center border=1 cellpadding=2 cellspacing=0 style=\"white-space:nowrap\" FONT-SIZE:\"12px\"></table>"

        thead_text = ""
        tbody_text = ""

        idx = feature['properties']['description'].find('</table>')
        title = feature['properties'][title_key] if title_key else feature['properties']['name']
        thead_text += \
            "<thead>" + \
                "<tr width=\"2000px\">" + \
                    f"<th align=center bgcolor=#ffcc00 colspan=2>{title}</th>" + \
                "</tr>" + \
            "</thead><tbody></tbody>"
                
        for key in properties:
            if key == 'Warn_type':
                if feature['properties'][key] == 1:
                    type = '第1類型(同土石流一併發布)'
                elif feature['properties'][key] == 2:
                    type = '第2類型(單獨發布)'
                else:
                    type = '未分類'
                idx = feature['properties']['description'].find('</tbody>')
                tbody_text += \
                    "<tr>" + \
                        f"<td align=center bgcolor=#000 width=\"1000px\"><font color=#fff><b>{properties[key]}</b></font></td>" + \
                        f"<td align=left width=\"1000px\">{type}</td>" + \
                    "</tr>"
            else:
                if feature['properties'][key] is None:
                    value = "無"
                else:
                    value = feature['properties'][key]
                idx = feature['properties']['description'].find('</tbody>')
                tbody_text += \
                    "<tr>" + \
                        f"<td align=center bgcolor=#000 width=\"1000px\"><font color=#fff><b>{properties[key]}</b></font></td>" + \
                        f"<td align=left width=\"1000px\">{value}</td>" + \
                    "</tr>"
        
        idx = feature['properties']['description'].find('</table>')
        feature['properties']['description'] = feature['properties']['description'][:idx] + \
            thead_text + \
        feature['properties']['description'][idx:]

        idx = feature['properties']['description'].find('</tbody>')
        feature['properties']['description'] = feature['properties']['description'][:idx] + \
            tbody_text + \
        feature['properties']['description'][idx:]
    return data


def update_feature_properties(data , properties , title_key = None):
    if not title_key: title_key = 'name'
    for cnt , feature in enumerate(data['features']):
        try:
            title = feature['properties'][title_key]
        except KeyError:
            title = f'{cnt:03d}'
            print(f"No title key: '{title_key}', default title: {title}")
        
        for property in properties:
            properties[property] = feature['properties'][property]
        feature['properties'] = {}
        feature['properties']['name'] = title
        for property in properties:
            feature['properties'][property] = properties[property]
    return data


class MyArgs(BaseModel):
    file_path: Optional[str]
    output: Optional[str]
    add_styles: Optional[str]
    title_key: Optional[str]
    update_properties: Optional[str]
    add_description: bool


def get_argument(args = None):
    if not args:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path" , help = "GeoJSON File path.")
    parser.add_argument("-o" , "--output" , help = "Output path. (Default: same as input file_path)")
    parser.add_argument("-a" , "--add_styles" , help = "Add geomap styles. (Default: No styles)")
    parser.add_argument("-t" , "--title_key" , help = "Specify the title key. (Default: 'name')")
    parser.add_argument("-p" , "--update_properties" , help = "Retain the specified properties and delete the others.")
    parser.add_argument("-d" , "--add_description" , help = "Add popup description." , action = 'store_true')
    parsed_args = parser.parse_args(args)
    myargs = MyArgs(**parsed_args.__dict__)
    return myargs


def main(sysargv = None):
    if sysargv[1:]:
        parsed_args = get_argument(sysargv[1:])
        file_path = os.path.realpath(parsed_args.file_path)
        if parsed_args.output:
            output = os.path.realpath(parsed_args.output)
        else:
            output = file_path

        add_styles = parsed_args.add_styles
        title_key = parsed_args.title_key
        update_properties = parsed_args.update_properties
        add_description = parsed_args.add_description

        add_styles = eval(add_styles) if add_styles else None
        update_properties = eval(update_properties) if update_properties else None
    else:
        file_path = INPATH
        output = OUTPATH
        add_styles = STYLES
        title_key = TITLE_KEY
        update_properties = PROPERTIES
        add_description = ADD_DESCRIPTION
    
    try:
        data = load_json(file_path)
        if update_properties:
            data = update_feature_properties(data , update_properties , title_key = title_key)
            if add_description:
                data = add_feature_description_SWCB(data , update_properties)
        data = add_feature_styles(data , add_styles)
        save_json(output , data)
            
    except IOError as f:
        print('I/O Error:' , f)
    except json.decoder.JSONDecodeError:
        print('JSON Decode Error!')


if __name__ == '__main__':
   main(sys.argv)