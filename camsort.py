"""
Script to rename and sort camera stills in current working directory based on timestamp
Also compresses using jpegtran if possible
i-ghost
"""

import os
import re
import calendar
import subprocess
from progressmeter import ProgressMeter

try:
    import Image, ImageFont, ImageDraw
    def txt_img(image, text, font="//usr//share//fonts//truetype//DroidSansMono.ttf", size=14):
	BLACK = "#000000"
        FONT = ImageFont.truetype(font, 14, encoding="unic")
        LINEWIDTH = 20
        img = Image.open(image)
        imgbg = Image.new("RGBA", img.size, BLACK)
        mask = Image.new("L", img.size, BLACK)
        draw = ImageDraw.Draw(img)
        drawmask = ImageDraw.Draw(mask)
        drawmask.line((0, img.size[1] - (LINEWIDTH / 2), 85, img.size[1] - (LINEWIDTH / 2)), fill="#999999", width=LINEWIDTH)
        img.paste(imgbg, mask=mask)
        draw.text((10, ((img.size[1] - LINEWIDTH) + 2)), text, font=FONT, fill="#ffffff")
        img.save(image, "JPEG", quality=100)
except:
    txt_img = None
    print("PIL not available: timestamps will not be written to images!")
    
if subprocess.call(["which", "jpegtran"], stdout=open(os.devnull, "w")) == 0:
    jpegtran = True

total_files = len([i for i in os.listdir(os.getcwd()) if i.endswith(".jpg") and os.path.isfile(i)])
progressbar = ProgressMeter(total=total_files, unit="images")

for i in os.listdir(os.getcwd()):
    progressbar.update(1)
    total_files -= 1
    if os.path.getsize(i) == 0:
        # zero byte file, discard
        os.remove(i)
        continue
    if i.endswith(".jpg"):
        match = re.search(r"(\w+)(\(\w+\))\w(\d)\w(\d+)\w(\d+)", i, re.IGNORECASE)
        #match.group(1) # Hex string ?
        #match.group(2) # Camera name
        #match.group(3) # Unknown bool
        #match.group(4) # Timestamp (yyyymmddhhmmss)
        #match.group(5) # Progressive counter, used for sorting
        if match:
            camera = {
                "name" : match.group(2).lstrip("(").rstrip(")"),
                # Timestamp
                "year" : int(match.group(4)[:4]),
                "month" : int(match.group(4)[4:6]),
                "date" : match.group(4)[6:8],
                "hour" : match.group(4)[8:10],
                "minute" : match.group(4)[10:12],
                "second" : match.group(4)[12:14],
                "bool" : int(match.group(3))
                    }
                    
                # the actual weekday derived from date
            camera["weekday"] = calendar.weekday(camera["year"], camera["month"], int(camera["date"]))
                
            DIR_LEAF = "%s//%s//%d//%s//%s_%s" % (
                    os.getcwd(),
                    camera["name"],
                    camera["year"],
                    calendar.month_abbr[camera["month"]],
                    camera["date"],
                    calendar.day_abbr[camera["weekday"]]
                    )
                    
            final_file_name = "%s-%s-%s.jpg" % (camera["hour"], camera["minute"], camera["second"])
            if not os.path.exists(DIR_LEAF):
                os.makedirs(DIR_LEAF) # os.renames() provides this, but having it here saves having multiple conditionals below
                
            if txt_img:
		try:
                    txt_img(i, final_file_name[:-4].replace("-", ":"))
                except IOError:
                    os.remove(i)
                    continue
            
            if jpegtran:
                subprocess.call(["jpegtran", "-o", "-copy", "none", "-progressive", "-outfile", os.path.join(DIR_LEAF, final_file_name), i], stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
                os.remove(i)
            else:
                os.rename(i, os.path.join(DIR_LEAF, final_file_name))
