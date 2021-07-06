import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'authority': 'mvp.microsoft.com',
    'sec-ch-ua': '^\\^',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
}


def get_data(item):
  data={}
  profile_url=item.find('a').get('href')
  data['profile_url']='https://mvp.microsoft.com{}'.format(profile_url)
  print('scraping :{}'.format(profile_url))
  pr=requests.get('https://mvp.microsoft.com{}'.format(profile_url),headers=headers)
  prsoup=BeautifulSoup(pr.text,'html.parser')
  profile_page=prsoup.find('div',{"class":'content'})
  right_panel=profile_page.find('div',{"class":"ly rightPanel"})
  data['name']=right_panel.find('h1').text
  if data['name']=='Anonymous':
    left_panel=profile_page.find('div',{"class":"ly leftPanel"})
    try:
      info_panel=left_panel.find('div',{'class':'ly infoPanel '})
    except:
      info_panel=left_panel.find('div',{'class':'ly infoPanel'})
    data['Award_Categories']=info_panel.find_all('div',{"class":'ly infoContent'})[0].text
    data['First_year_awarded']=info_panel.find_all('div',{"class":'ly infoContent'})[1].text
    data['Number_of_MVP_Awards']=info_panel.find_all('div',{"class":'ly infoContent'})[2].text
  else:
    #country
    if right_panel.find('div',{'class':'country'}):
      data['country']=right_panel.find('div',{'class':'country'}).text
    else :
      data['country']=''
    #desc
    if right_panel.find('div',{'class':'desc'}):
      data['keywords']=right_panel.find('div',{'class':'desc'}).text.strip() 
    else :
      data['keywords']=''
    left_panel=profile_page.find('div',{"class":"ly leftPanel"})
    data['profile_image_url']='https://mvp.microsoft.com'+left_panel.find('div',{'class':'ly photoPanel'}).find_all('img')[-1].get('src')
    try:
      info_panel=left_panel.find('div',{'class':'ly infoPanel '})
    except:
      info_panel=left_panel.find('div',{'class':'ly infoPanel'})
    data['Award_Categories']=info_panel.find_all('div',{"class":'ly infoContent'})[0].text
    data['First_year_awarded']=info_panel.find_all('div',{"class":'ly infoContent'})[1].text
    data['Number_of_MVP_Awards']=info_panel.find_all('div',{"class":'ly infoContent'})[2].text

    linkedin_url=None
    for a in left_panel.find('div',{"class":'ly otherPanel'}).find_all('a'):
      if 'https://www.linkedin.com' in a.get('href'):
        linkedin_url=a.get('href')
        break
    data['linkedin_url']=linkedin_url
    script=str(profile_page.find_all('script')[5])
    data['activities_count']=int(script.count('/2021"')+script.count('/2020"'))
  return data

masterdata=[]

for p in range(1,6):
    params = (
        ('ps', '48'),
        ('pn', str(p)),
    )

    response = requests.get('https://mvp.microsoft.com/en-US/MVPSearch', headers=headers, params=params)
    soup=BeautifulSoup(response.text,'html.parser')
    items=soup.find('div',{'class':'MVPSearch'}).find_all('div',{'class':'profileListItem'})
    print('page :{}'.format(p))
    for item in items:

      data=get_data(item)
      masterdata.append(data)
## 
df=pd.DataFrame(masterdata)
df.to_csv('job.csv')
