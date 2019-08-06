from PIL import Image
import math
im = Image.open("6.jpg")
pix = im.load()
width = im.size[0]
height = im.size[1]
maxx=0
minx=100000
maxy=0
miny=100000
maxd=0
#print(width)
#print(height)
for x in range(width):
    maxy2 = 0
    miny2 = 100000
    for y in range(height):
        r, g, b = pix[x, y]
        if r >= 239 and g >= 239 and b >= 239:
                maxx = max(maxx,x)
                minx = min(minx,x)
                maxy2 = max(maxy2,y)
                miny2 = min(miny2,y)        	
        #print(r, g, b)
    if maxy2 - miny2 < 10000 and maxy2 - miny2 > maxd :
        maxd = maxy2 - miny2
        maxy = maxy2
        miny = miny2
print(maxx,minx,maxy,miny)
print((maxx + minx) / 2, (maxy + miny) / 2)
if abs((maxx + minx) / 2 - width / 2) <= 100:
    print("YES")
    if abs((maxx + minx) / 2 - width / 2) <= 100:
        print("END")
    elif ((maxy + miny) / 2 <= height / 2) :
        print("U")
    elif ((maxy + miny) / 2 > height / 2 and (maxy + miny) / 2 <= height) :
        print("D")
elif abs((maxx + minx) / 2 - width / 2) <= 100:
    print("YES")
    if ((maxx + minx) / 2 <= width / 2) :
        print("L")
    elif ((maxx + minx) / 2 > width / 2 and (maxx + minx) / 2 <= width) :
        print("R")
else:
    if ((maxx + minx) / 2 <= width / 2) :
        print("L")
    elif ((maxx + minx) / 2 > width / 2 and (maxx + minx) / 2 <= width) :
        print("R")
    else:
        print("NO")
    if ((maxy + miny) / 2 <= height / 2) :
        print("U")
    elif ((maxy + miny) / 2 > height / 2 and (maxy + miny) / 2 <= height) :
        print("D")
    else:
        print("NO")



