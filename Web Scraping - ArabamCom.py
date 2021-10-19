# -*- coding: utf-8 -*-

from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def strip_col(x):
    if x.dtype == object:
        x = x.str.strip()
    return(x)


#sayfalar arasında gezin ve ilan linklerini topla
url = "https://www.arabam.com/ikinci-el/otomobil?city="
for j in range(82,0,-1):
  links = []
  print(str(j)+" şehir başladı")
  for i in range(50):
      try:    
        print(str(j)+" plakalı il - "+str((i+1)*50)+" sayfa")
        url1 = url+str(j)+"&take=50&page="+str(i+1)
        req = Request(url1)
        req.add_header('User-agent', 'your bot 0.1')
        html =urlopen(req)
        soup = BeautifulSoup(html, "html.parser")  
        href = [div.a.get('href') for div in soup.find_all(class_='pr10 fade-out-content-wrapper')]
        links.append(href)
      except:
        print("hata")
  links = [j for sub in links for j in sub]
  print(str(j)+" plakalı il - sayfalama bitti.")
  link = []
  for i, value in enumerate(links):
      get_url = "https://www.arabam.com" + value
      link.append(get_url)  
  print(str(len(link))+" araç bulunmaktadır.")
  print("2.aşama başladı")
  fiyat = []
  konum = []
  ozellik = []
  for i, value in enumerate(link):
      try:
          print(str(j+1)+" il "+str(i+1)+"/"+str(len(link)) +" araç verisi çalışıyor.")
          req = Request(value)
          req.add_header('User-agent', 'your bot 0.1')
          link_html = urlopen(req)
          link_soup = BeautifulSoup(link_html, "html.parser")
          price = link_soup.find("p", {"class" : "font-default-plusmore bold ls-03"})
          if price == None:
              price = link_soup.find("p", {"class" : "color-red4 font-semi-big bold fl w66"})
              if price == None:
                  fiyat.append("None")
              else:
                  fiyat.append(price.text) 
          else:
              fiyat.append(price.text)
          location = link_soup.find("p", {"class" : "one-line-overflow font-default-minus pt4 color-black2018 bold"})
          if location == None:
              konum.append("None")
          else:
              konum.append(location.text)
          info = link_soup.find("ul",{"class":"w100 cf mt12 detail-menu"})
          if info == None:
              ozellik.append("None")
          else:
              ozellik.append(info.text)
      except:
          print("Hata")
    

  print("2.aşama bitti")
  print("3.aşama başladı")
  df = pd.DataFrame(list(zip(fiyat, konum, ozellik)), 
               columns =['Fiyat', 'Konum','Ozellik']) 
  
  #None değerlerini sildik ve indexi düzelttik
  df = df[df.Ozellik != 'None'].reset_index()
  loc = df["Konum"].str.split("/", n = 1, expand = True)
  df.drop(columns=["Konum"], inplace=True)

  #Düzenlenmiş "konum" kolonu
  loc.drop(columns=[1],inplace=True)

  # Araç özelliklerini sütunlara ayırdık
  new = df["Ozellik"].str.split(":", n = 14, expand = True)

  # Sütunlara ayırdığımız özellikleri düzenledik ve düzenledigimiz konum, fiyat bilgilerini ekledik
  new["Ilan_no"] = new[1].str.replace('İlan Tarihi', '')
  new["Ilan_tarihi"] = new[2].str.replace('Marka', '')
  new["Marka"] = new[3].str.replace('Seri', '')
  new["Seri"] = new[4].str.replace('Model', '')
  new["Model"] = new[5].str.replace('Yıl', '')
  new["Yıl"] = new[6].str.replace('Yakıt Tipi', '')
  new['Yıl'] = [str(x)[:5] for x in new['Yıl']]
  new["Yakıt_tipi"] = new[7].str.replace('Vites Tipi', '')
  new["Vites_tipi"] = new[8].str.replace('Motor Hacmi', '')
  new["Motor_hacmi"] = new[9].str.replace('Motor Gücü', '')
  new["Motor_hacmi"] = new["Motor_hacmi"].str.replace("cc", "")
  new["Motor_gücü"] = new[10].str.replace('Kilometre', '')
  new['Motor_gücü'] = [str(x)[:3] for x in new['Motor_gücü']] 
  new['Motor_hacmi'] = [str(x)[:5] for x in new['Motor_hacmi']]
  new["Motor_gücü"] = new["Motor_gücü"].str.replace("hp", "")
  new["Kilometre"] = new[11].str.replace('Boya-değişen', '')
  new["Kilometre"] = new["Kilometre"].str.replace("km", "")
  new["Kilometre"] = new["Kilometre"].str.replace(",", ".")
  new["Boya-değişen"] = new[12].str.replace('Takasa Uygun', '')
  new["Takasa_uygun"] = new[13].str.replace('Kimden', '')
  new["Kimden"] = new[14]
  new["Konum"]=loc[0]

  new["Fiyat"] = df["Fiyat"].str.replace(".", "")
  new["Fiyat"] = new["Fiyat"].str.replace("TL", "")
  new["Kilometre"] = new["Kilometre"].str.replace('.', '')

  new.drop(columns=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], axis=1, inplace=True)

  # 'Object' olan kolonların sağ ve solundaki boşlukları sildik
  new = new.apply(strip_col)

  patternEUR = "EUR"
  patternUSD = "USD"

  USD = new['Fiyat'].str.contains(patternUSD)
  EUR = new['Fiyat'].str.contains(patternEUR)

  new = new[~USD]
  new = new[~EUR]

  #Satırları kaymış ve eksik bilgilere sahip olan kolonları dropladık
  new = new[new.Yıl != 'LPG']
  new = new.replace(to_replace='None', value=np.nan).dropna()
  new = new[new.Yıl != 'Benz'].reset_index()
  new.drop(columns=["index"], inplace=True)

  new["Motor_gücü"] = new["Motor_gücü"].replace(to_replace='-', value=np.nan)
  new["Motor_hacmi"] = new["Motor_hacmi"].replace(to_replace='-', value=np.nan)
  new["Motor_gücü"].fillna(new["Motor_gücü"].mode().values[0], inplace = True)
  new["Motor_hacmi"].fillna(new["Motor_hacmi"].mode().values[0], inplace = True)



  new.to_excel("arabam-"+str(j)+".xlsx")
  print("3.aşama bitti")
  print(str(j)+" şehir bitti.")

frames=[]
for i in range(1,82,1):
    try:
        df=pd.read_excel("arabam-"+str(i)+".xlsx")
        tmpdf=pd.DataFrame(df)           
        frames.append(tmpdf)        
    except:
        print("Hata: "+str(i)+" şehir")
        
result = pd.concat(frames)
result.to_excel("arabam-ALL-V1.xlsx")
