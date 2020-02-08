# -*- coding: utf-8 -*-
"""
Create Graphic from Instagram Hashtag's Colors

@author: zwieselthier
"""
import pandas as pd
import time
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import colorgram
import math

#%% Opens image from URL and reads color
# Input Image URL, Number of Colors to Grab from each photo
# Output List of RGB Colors

def RGB_from_url(url, num_colors):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    colors = colorgram.extract(img, num_colors)
    
    color_list = []
    for x in colors:
       color_list.append( (x.rgb.r, x.rgb.g, x.rgb.b) )
    return color_list



#%% Web Scrape and Inputs
chromedriver = r"chromedriver.exe" #Link to Chromedriver

#inputs
hashtag = input('Hashtag \n#') #Hashtag to anaylze (without the # symbol)
num_colors = int(input('Number of Colors per Photo \n'))


url = f'https://www.instagram.com/explore/tags/{hashtag}'
driver = webdriver.Chrome(chromedriver)
driver.get(url)

for x in [1,50, 100, 150]: #Scrolls down to grab more images Dont belive this actually works when not logged in
    driver.execute_script(f"window.scrollTo(0, 10000 * {x})")
    time.sleep(.1)

#%%
soup = BeautifulSoup(driver.page_source) #Grab HTML

driver.close()
    
image_list = [] # create empty list to save img urls
for link in soup.find_all('img'): #Grab Image URLS from HTML
    image_list.append(link.get('srcset'))

#Clean up and Create Dataframe
df = pd.DataFrame(image_list, columns = ['srcset'])
df.dropna(inplace = True)
df = df['srcset'].str.split(' ',expand=True)[0].to_frame()
df = df[df[0].str.contains("https:")]

#%% Analze each URL Photo for colors and add to list
print('Analyzing Photos')
i = 0
colors = []
for link in df[0]:
    print( '\r' + str(i+1) + '/' + str(len(df)) , end = '' )
    colors = colors + RGB_from_url(link, int(num_colors)) 
    i = i + 1

#%% Create Graphic

im = Image.new('RGB', (1000, 250), (255, 255, 255))
draw = ImageDraw.Draw(im)

i = 0
width = math.ceil(1000 / len(colors))
for color in colors:
    draw.line((i*width, 0, i*width, 300), fill= colors[i], width=width)
    i = i + 1
im.show()
im.save(f'{hashtag}.jpg', "JPEG")
