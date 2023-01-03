import requests
import random
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from bs4 import BeautifulSoup
import pandas as pd
from urllib3.util.ssl_ import create_urllib3_context


class LowesSearchLinksScraper:
  def __init__(self,keyword):
    self.keyword = keyword
    self.data = []
    self.execute()

  def execute(self):
    url = self.get_url(offset=0,adjustedNextOffset=0)
      # response = self.get_response(url)
    # self.get_details(response)
    self.get_product_details(url, scraped_product_count=0, offset=0,adjustedNextOffset=0)
    #self.write_csv()

  def write_csv(self):
      df = pd.DataFrame(self.data)
      df.to_csv(str(self.keyword)+".csv", index=False)
  def get_url(self,offset,adjustedNextOffset):
    url = f"https://www.lowes.com/search/products?searchTerm={self.keyword}&offset={offset}&adjustedNextOffset={adjustedNextOffset}&nearByStores=2512&ac=false"
    return url

  def get_headers(self):
    headers = {
        # 'Cookie': 'dbidv2=8a78db4a-929a-4fb1-838a-0cf8654dd5d0; EPID=OGE3OGRiNGEtOTI5YS00ZmIxLTgzOGEtMGNmODY1NGRkNWQw; sn=1985; sd=%7B%22id%22%3A%221985%22%2C%22zip%22%3A%2299701%22%2C%22city%22%3A%22Fairbanks%22%2C%22state%22%3A%22AK%22%2C%22name%22%3A%22Fairbanks%20Lowe\'s%22%2C%22region%22%3A%2214%22%7D; mdLogger=false; kampyle_userid=214c-434b-92a2-d8e3-ab62-368f-ca9c-55ad; ph_aid=7c1819e5-c8a7-4b33-b1fd-2b3d6d361e4f-c4aa7611c4bf7-42394536397ec-c890ea005bc33; zipcode=99701; nearbyid=1985; zipstate=AK; AMCV_5E00123F5245B2780A490D45%40AdobeOrg=-1303530583%7CMCIDTS%7C20353%7CMCMID%7C06790261715728494701226529254517509332%7CMCAAMLH-1695902808%7C12%7CMCAAMB-1695902808%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCOPTOUT-1695305208s%7CNONE%7CvVersion%7C3.3.0; salsify_session_id=e42aed4a-bf61-423b-b31c-e3428fd6185a; _gcl_au=1.1.1384537775.1695298023; audience=DIY; _tt_enable_cookie=1; _ttp=MpVNa4ReSR3cRfRmfeRyGL6cSo1; _pin_unauth=dWlkPVpESmhOelJqTUdZdE5qUTNZUzAwTURVNUxUa3hNak10TXpJNU5ESTVOMlJrT0dFNA; _fbp=fb.1.1695298063381.1970757761; BVBRANDID=eeff4e72-e2e4-4e7b-8b13-5be4383bd0fe; session_id=111568f2-7742-4fda-a1a0-534dee9faea1; region=central; g_amcv_refreshed=1; bm_sz=33D7C769017438A1CA005C77093ABF0D~YAAQJUYDF34bAqWLAQAANRWrtxWs4RlhOY5RnlU7+DTk9DLj8OhOoZMmAAZyxJdN5oVlMUwD6CPwOCGKj6GC9pkqGZqIXzujd+oFjs+S8zt3moJ43+3CtkUHMjiKb/tuLfMrDc6aH8ztxZ6GncQVJcAL7kskoME9i5yzan4B2ZtMXBUepMNiVKQSntjBVL2Dlj7Ypr7iCZPyGJ+A0UY5qrBsPicSdqc8dbJO3Q0+vEdqHc05DLbLSi7CwBu4mkSHJbs1vheeMZoP9rmgieLGNQPvoIab+BOp/cFseDImUl4vqQ==~3425845~4404018; _abck=DFA77B82293FE18ADDA8E76B0207FE67~0~YAAQJUYDF3wbAqWLAQAANRWrtwrdt18TjL3yVqFW6/e+OCWGpz4pGGjklEF/looa+fv1TEGaXZd1PGVUIHRvZ/1vyIYxXLHHfML+ErcinxEDF5IaWLvK8PDDO1wsnGOhpE1R80/X7yvlCOA+fWDcxxCwPgC66hkxbwb/FaskNwirOipANtNUCj+FB6HBZlJ1S4+AEA6NZhZpagy5ugonKrxyvJf7WUYtGtBs8YkyKLPM4Y7VOwWJ2ES8eWxy2XvF1kxqHHOR9788m0hDPvmcz9bsGvAN7GSjT/gu7I2J31nrebW5KKD4ncDBbHrdacdXFf9xlQscZruo549ujBj7r3mzAMHTk9zn2pjQhw+04WeR2iMyk4SOOpCN3mMAM/pact6FuP3CkRPqKfYr5E8+hakAQ4el43wblDSMaY+laHluy6WJW3k+czd2PvUDC3PXAjADv8fTjdA=~-1~-1~-1; al_sess=FuA4EWsuT07UWryyq/3foK2odEFCox6DkOAvzb77hdpU/10fLcxb3DEgFHFR1zLU; ak_bmsc=589CCF46D2541A58D2E048470D5648D4~000000000000000000000000000000~YAAQJUYDF/UbAqWLAQAAVyOrtxUUe+fup4AGaHRTK1CyzeC/W0DHF/ka/5nh7vYecFJh/fQrOgACGAUAxql/I2dyNHOcBy9C1u8crXACgO16lRrgmaCU0NWp2nqxkN27FLgXdsbnRPznEYsz4rU3amGmq97H7pQHFbWa/WcingjLjTjI/hgl7/bz6zALi92SmBYvclSbEqbIK8YwxWqwQDIN2bW2RYQ+2jjkD6PRpWf+hHavo4ZJgF+kwwtNxphdhCbYmqb/ceIikhMZYAl1GPe+Ltfi9mI6I9mC41RsGFLWVxOCxSPW5ljBJRy7XCt2ny9nyHAs8KWouRJhxeTMRoTNyE4oibZ9GxS61rpZB3nj4WwwKPyry4nHj+Zy0DS74hk5wrS/S5UtsseJhHNL5n6U7416QJK9me7h3Ieygha0HQvDOC3vQbfHhqc/eiEFWriILzzVcKRHwG9TYdue4djT+Emd8iOOHqbide6GtryVwt6ab9WcM/lsLKPi1nvFNpzIMM8+AtRQBiOlTnFzOncOJ6zUePRJLj4tD/5XO+R4o41I/AXpC+mbQzFLbZes6lWK5Mks9ejvD47/i8EsZ4KCSXvhFz3Psy7kuU94sQ2vmVsxKaZ3UUWFLpWuzTIm8h3S; AMCVS_5E00123F5245B2780A490D45%40AdobeOrg=1; IR_gbd=lowes.com; largeViewOw=List; __gads=ID=a76eac8d6a64e6e1:T=1695298003:RT=1699597817:S=ALNI_Ma5_Wibl3_BjZ9ZMNRj4QnPB_GcLA; __gpi=UID=00000c51f1966f5b:T=1695298003:RT=1699597817:S=ALNI_Mb35vnmbDV8cKKid8ghfO3lXwOVcA; _lgsid=1699597815995; seo-partner=gDTMXB9g7l46qsQ3gCM3qCMsoDgSmXpC; sbsd=sEZ0agIAkHSoLLUbNX/GnKzMfX1Nsr4aMX06VJsWWvaeRhPku0naz7ETylwO8PWENeUOjtdnYNNzlOJSlVehmzYkmOxi7QB2mg+3RSgFedy+nXBA7fc3RYTiuwIgILBI2Mcq58nJ3aU/Pu4ECtSIurw==; AKA_A2=A; akavpau_cart=1699598342~id=56188c126e63d6cf81980da3c33a8940; p13n=%7B%22zipCode%22%3A%2299701%22%2C%22storeId%22%3A%221985%22%2C%22state%22%3A%22AK%22%2C%22audienceList%22%3A%5B%22WPRO%22%5D%7D; g_previous=%7B%22gpvPageLoadTime%22%3A%220.00%22%2C%22gpvPageScroll%22%3A%223%7C4%7C0%7C12265%22%2C%22gpvSitesections%22%3A%22tools%2Chand_tools%2Csockets_socket_adapters%2Csockets_socket_sets%22%2C%22gpvSiteId%22%3A%22desktop%22%2C%22gpvPageType%22%3A%22product-display%22%7D; fs_lua=1.1699598046728; fs_uid=#Q8RZE#80ea6f8a-f11d-4f00-9015-8a540c6c3000:ae9e23a4-8963-4f24-b6aa-76be1038d549:1699595006439::4#2cbce093#/1720856482; IR_12374=1699598051463%7C0%7C1699598051463%7C%7C; IR_PI=0797604e-c40d-3b46-a503-10e1854d4dbe%7C1699684451463; kampyleUserSession=1699598052131; kampyleUserSessionsCount=107; kampyleSessionPageCounter=1; kampyleUserPercentile=2.292125833854408; _uetsid=bc8c8df07ecb11ee960867bb56e8ed43; _uetvid=d8b1b190221911ee8f7e11b174e2fa16; prodNumber=1; akavpau_default=1699598412~id=c3cd32964918e6ee0ab073077bbd973c; akaalb_prod_dual=1699684512~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=a4b2944ad31dd4f1cda2f3de68399c14; bm_sv=346F339B4E58447410E9D02780A0CA06~YAAQJUYDFxyKBKWLAQAAZhfxtxVcUimN9/SkMNjqTwY95T2vpSpgDzQvjmonLCqg4eh7kxF0ypb9wTxqxwU7/O4zDeeu23W7wDqDqKb3UseRwV8YqLbohxKPArW2W5wlPj4OZpnhbNYiuO/Qt+XDOCXdBzTcv3R7sSNjD3s8ZMY/UXULmn5v09w0EOEoAWNy9YpbOZvBpBaFPpi8XS8ZYc5zFhWSpLIoh6/vUqaXO3GaHRrFH6xcCUGYMLqd4n2Z~1; RT="z=1&dm=lowes.com&si=50d49bd9-9d04-41f8-b91f-287fa41545fa&ss=los8nk7q&sl=1&tt=5rn&bcn=%2F%2F684d0d41.akstat.io%2F&ld=50ii&nu=47zbxtll&cl=6igp"; _abck=DFA77B82293FE18ADDA8E76B0207FE67~-1~YAAQPaIauAKOr02LAQAADQJRhQpqDNiBaSVfdmmM9JV36jzHvATUCA6cTYIZxVktLG3H8znMAe20KSGmsuDOwxN+nuepK3Uf2UxZaFwU9PhlzkdCcuJFnoEHbJr27jhtGtxLGo3aGD8pK7wLXu/gYO9H2VVuYnTOzAkO+gM0MRnpIHWnfC0G3x8GK8V7UrwiDUOK1uSuPsOJFOiO+g0VRB6vcgR4ymonTiN0z9ziJHDJ8s+93JYmOc2CrQbf8CIq1vnnlr8GCoe653v4Vx6MtGbOekam5wc/IR8jWKdg21CXfWFYBAFIdaoH0AyF6afkU245HG8yzNwkPv6Pc0su3FMaMLA/6hCn2445W7Zf0FNKoabLEiySUR/umusn1kSWmrPiTXQdGkzipGz4FGD/y9vWSCXovKkbyLoZ7iehe3JjxHhtph8vGof/TUxSBpIn2DDZacZ7IJA=~0~-1~-1; sbsd=s7EdUS/KAlflm3bk0AxXZQoHlDhvB6INvNfQMtmpniDPyZpjCXelyv8hjhtREz8JS5tYP9e9PklPB0ahJRe1uQimvOLhVXcVcw4vYphDTyNSBeINJX3vnswCf3vvn1rSlM44g0LSR0jzak7JhoT8RQA==; akaalb_prod_dual=1699684817~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=55287f2eda81cf6591b3f3832237a307; akavpau_default=1699598717~id=8a98d6284e97144fb43c8d24bf633e88; al_sess=brukgPJGNBK59A5xZcXk0WWH4RTsvA0dlAy8d5I0glLwitorUNgCCYwZg6bfDWAE',
        # 'Cookie': 'dbidv2=8a78db4a-929a-4fb1-838a-0cf8654dd5d0; EPID=OGE3OGRiNGEtOTI5YS00ZmIxLTgzOGEtMGNmODY1NGRkNWQw; mdLogger=false; kampyle_userid=214c-434b-92a2-d8e3-ab62-368f-ca9c-55ad; ph_aid=7c1819e5-c8a7-4b33-b1fd-2b3d6d361e4f-c4aa7611c4bf7-42394536397ec-c890ea005bc33; AMCV_5E00123F5245B2780A490D45%40AdobeOrg=-1303530583%7CMCIDTS%7C20353%7CMCMID%7C06790261715728494701226529254517509332%7CMCAAMLH-1695902808%7C12%7CMCAAMB-1695902808%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCOPTOUT-1695305208s%7CNONE%7CvVersion%7C3.3.0; salsify_session_id=e42aed4a-bf61-423b-b31c-e3428fd6185a; _gcl_au=1.1.1384537775.1695298023; audience=DIY; _tt_enable_cookie=1; _ttp=MpVNa4ReSR3cRfRmfeRyGL6cSo1; _pin_unauth=dWlkPVpESmhOelJqTUdZdE5qUTNZUzAwTURVNUxUa3hNak10TXpJNU5ESTVOMlJrT0dFNA; _fbp=fb.1.1695298063381.1970757761; BVBRANDID=eeff4e72-e2e4-4e7b-8b13-5be4383bd0fe; session_id=111568f2-7742-4fda-a1a0-534dee9faea1; g_amcv_refreshed=1; bm_sz=33D7C769017438A1CA005C77093ABF0D~YAAQJUYDF34bAqWLAQAANRWrtxWs4RlhOY5RnlU7+DTk9DLj8OhOoZMmAAZyxJdN5oVlMUwD6CPwOCGKj6GC9pkqGZqIXzujd+oFjs+S8zt3moJ43+3CtkUHMjiKb/tuLfMrDc6aH8ztxZ6GncQVJcAL7kskoME9i5yzan4B2ZtMXBUepMNiVKQSntjBVL2Dlj7Ypr7iCZPyGJ+A0UY5qrBsPicSdqc8dbJO3Q0+vEdqHc05DLbLSi7CwBu4mkSHJbs1vheeMZoP9rmgieLGNQPvoIab+BOp/cFseDImUl4vqQ==~3425845~4404018; _abck=DFA77B82293FE18ADDA8E76B0207FE67~0~YAAQJUYDF3wbAqWLAQAANRWrtwrdt18TjL3yVqFW6/e+OCWGpz4pGGjklEF/looa+fv1TEGaXZd1PGVUIHRvZ/1vyIYxXLHHfML+ErcinxEDF5IaWLvK8PDDO1wsnGOhpE1R80/X7yvlCOA+fWDcxxCwPgC66hkxbwb/FaskNwirOipANtNUCj+FB6HBZlJ1S4+AEA6NZhZpagy5ugonKrxyvJf7WUYtGtBs8YkyKLPM4Y7VOwWJ2ES8eWxy2XvF1kxqHHOR9788m0hDPvmcz9bsGvAN7GSjT/gu7I2J31nrebW5KKD4ncDBbHrdacdXFf9xlQscZruo549ujBj7r3mzAMHTk9zn2pjQhw+04WeR2iMyk4SOOpCN3mMAM/pact6FuP3CkRPqKfYr5E8+hakAQ4el43wblDSMaY+laHluy6WJW3k+czd2PvUDC3PXAjADv8fTjdA=~-1~-1~-1; al_sess=FuA4EWsuT07UWryyq/3foK2odEFCox6DkOAvzb77hdpU/10fLcxb3DEgFHFR1zLU; AMCVS_5E00123F5245B2780A490D45%40AdobeOrg=1; IR_gbd=lowes.com; largeViewOw=List; seo-partner=gDTMXB9g7l46qsQ3gCM3qCMsoDgSmXpC; DECLINED_DATE=1699598217376; region=central; sn=1119; sd=%7B%22id%22%3A%221119%22%2C%22zip%22%3A%2230341%22%2C%22city%22%3A%22Chamblee%22%2C%22state%22%3A%22GA%22%2C%22name%22%3A%22Chamblee%20Lowe\'s%22%2C%22region%22%3A%223%22%7D; _lgsid=1699602102154; kampyleUserSession=1699602108206; kampyleUserSessionsCount=110; kampyleUserPercentile=75.7049983558026; zipcode=30341; nearbyid=1119; zipstate=GA; bm_mi=AE79B6F7696AC7CEF0AE6FC2E98B45C5~YAAQJUYDF3tRB6WLAQAAIzE6uBUGVYkRCU9Qnk3ZmEm7ey/e+8O3rqTohnbFoSFiDB+JSZxnit8CPItWXDAZ/hHmdctGf/fvwXFLS5uaIqJF9EFeQzuhSPEE0ButMmX6Psb0O1RoyX56vKZf7yhTXJ3BTf+jLwfkumHQe2ebnvyUX51vynNsMslwF9Qv1McpiUydhzNp3J2/ucyQ72qTDhKKyba/O6CXRV95cNoHLa3I5EaR1+3HNq+9+O74DwNDtnrw+f/Pso6eBHvBKRxEUE7mM+VAms8seKSnPuPAG4GePT4fJiINHuFIiohEFs2h~1; AKA_A2=A; sbsd=sMFiXmre4oYUrdI+emZo8bPk3PS/shb4CkY8eidzJ4WPa80X4P6jwFCCzOy4ze15Ljgx9H94wlClLj9Beavv2Wq7EEPkiU1t/ENcOhK1KcGirlrpfAxLx185QpiejDkCsIHuX/NL7zF9Ur8NdBzFZOg==; akavpau_cart=1699603209~id=78066786b7fca31dc0c9041f7a14a617; ak_bmsc=7847DC20AE376BD59F88BA61933877B8~000000000000000000000000000000~YAAQJUYDFwNTB6WLAQAAZkw6uBVCw4oUr3aEHeHa7ai74zRI3ejfmyj3sJRF8ApUhY6CEJphFwDRePx5I705TnFTrN2uO0b79DYzWWv2NK9P0m0RaYXwWbl0ppLBhbfhfXVogNseyDLviujy280kRBqSTPdzkcn/dn/F4F6odfOXJ0dbOKsqqidyTnQX3D8yym3J10MgakqWJrDWI9dLUIdhj8W7vHifrOf97b7Kb08BygJGPLRuf+axnmJNjEYD8xsmefZEKBpZ5UmIEc29yXPRSQmsottfOzoOfDU4d6Cc1I2Ogc80sBdkkArziakoLQQdp0GBcnmH9BLBI/xSEBc3MXfIDqFq35ArGa8EiOQet9uUsYKVX58HYl0TCTakeREzHXoFut2YLqrL2/epeCiqnxXCnGvCJV9hce7pRhzAbUTM14LviEMUiQY/JcUfCrDKsnK0M6bPnqZ6gM3sHs/efccOObUJp2HYco6OyPdI47h0hLkAlEe8hKcF9MH2YLiklHrzY5FyHNLR3ZD2foWBfr98xBz93QID+lAGWYivX1xJcge9v5CVZOKFRhk5anUlX5xP99Cr78BBXVwwasi5DDKtSzXcXsbX4otZX+eSg6zp33QuxINjc1HIh3z7ilakYAXcwwesrX0k0tvLPlrbdzqPSysw009qVFanMEyo/a4WzUaUNnNbQYyOlTdy9/MYKbtD66h7qLdp1L61yG4GrV2FDKI8yhNjagr5by/PjbAIEUE4; p13n=%7B%22zipCode%22%3A%2230341%22%2C%22storeId%22%3A%221119%22%2C%22state%22%3A%22GA%22%2C%22audienceList%22%3A%5B%22WPRO%22%5D%7D; __gads=ID=a76eac8d6a64e6e1:T=1695298003:RT=1699602912:S=ALNI_Ma5_Wibl3_BjZ9ZMNRj4QnPB_GcLA; __gpi=UID=00000c51f1966f5b:T=1695298003:RT=1699602912:S=ALNI_Mb35vnmbDV8cKKid8ghfO3lXwOVcA; g_previous=%7B%22gpvPageLoadTime%22%3A%220.00%22%2C%22gpvPageScroll%22%3A%223%7C4%7C0%7C12526%22%2C%22gpvSitesections%22%3A%22tools%2Chand_tools%2Csockets_socket_adapters%2Csockets_socket_sets%22%2C%22gpvSiteId%22%3A%22desktop%22%2C%22gpvPageType%22%3A%22product-display%22%7D; fs_lua=1.1699602913246; fs_uid=#Q8RZE#80ea6f8a-f11d-4f00-9015-8a540c6c3000:dddc6e90-1e77-4624-88bd-222bff615959:1699602103449::2#2cbce093#/1720856482; IR_12374=1699602917494%7C0%7C1699602917494%7C%7C; IR_PI=0797604e-c40d-3b46-a503-10e1854d4dbe%7C1699689317494; kampyleSessionPageCounter=2; _uetsid=bc8c8df07ecb11ee960867bb56e8ed43; _uetvid=d8b1b190221911ee8f7e11b174e2fa16; prodNumber=1; akavpau_default=1699603244~id=4a8238a3180c20b1158e44bd26007537; akaalb_prod_dual=1699689344~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=0007ecd07e49c7a9f266857e1213252e; bm_sv=A83BAA100EAFC633A3F1ACFECD0C09ED~YAAQJUYDF8xXB6WLAQAAbtM6uBVrr8BJuAjAf4j2TYWVzVPGT0MAZKVxpjTUgptCfUDfC8PctuXRMR7/z+Cr4U54x0sVTxoYIhyYPbuW4wH3/QCpntQstrI5fdMtMzKs4mGlxz7v5NsbeqkVOTENRryOtQp0dk0Qc/MtE3AefI+hBeF8VejdubZftNXmZ1uZr6/DCrrRSRq5lsPN7LZGHK5y6w1muh/AkHwEmYC2IN+OYGwZwzVs/ojGKfmUQeZC~1; RT="z=1&dm=lowes.com&si=50d49bd9-9d04-41f8-b91f-287fa41545fa&ss=los8nk7q&sl=6&tt=wkg&bcn=%2F%2F684d0d41.akstat.io%2F&ld=31bpu&nu=47xp91kh&cl=32339"; _abck=DFA77B82293FE18ADDA8E76B0207FE67~-1~YAAQPaIauAKOr02LAQAADQJRhQpqDNiBaSVfdmmM9JV36jzHvATUCA6cTYIZxVktLG3H8znMAe20KSGmsuDOwxN+nuepK3Uf2UxZaFwU9PhlzkdCcuJFnoEHbJr27jhtGtxLGo3aGD8pK7wLXu/gYO9H2VVuYnTOzAkO+gM0MRnpIHWnfC0G3x8GK8V7UrwiDUOK1uSuPsOJFOiO+g0VRB6vcgR4ymonTiN0z9ziJHDJ8s+93JYmOc2CrQbf8CIq1vnnlr8GCoe653v4Vx6MtGbOekam5wc/IR8jWKdg21CXfWFYBAFIdaoH0AyF6afkU245HG8yzNwkPv6Pc0su3FMaMLA/6hCn2445W7Zf0FNKoabLEiySUR/umusn1kSWmrPiTXQdGkzipGz4FGD/y9vWSCXovKkbyLoZ7iehe3JjxHhtph8vGof/TUxSBpIn2DDZacZ7IJA=~0~-1~-1; sbsd=s7EdUS/KAlflm3bk0AxXZQoHlDhvB6INvNfQMtmpniDPyZpjCXelyv8hjhtREz8JS5tYP9e9PklPB0ahJRe1uQimvOLhVXcVcw4vYphDTyNSBeINJX3vnswCf3vvn1rSlM44g0LSR0jzak7JhoT8RQA==; akaalb_prod_dual=1699689407~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=1d70a9faf5d6518ff28d87aa89acbbd0; akavpau_default=1699603307~id=425de2e11bc3e345d3728d453bf246ef; al_sess=brukgPJGNBK59A5xZcXk0WWH4RTsvA0dlAy8d5I0glLwitorUNgCCYwZg6bfDWAE',
        # 'Cookie': 'dbidv2=8a78db4a-929a-4fb1-838a-0cf8654dd5d0; EPID=OGE3OGRiNGEtOTI5YS00ZmIxLTgzOGEtMGNmODY1NGRkNWQw; mdLogger=false; kampyle_userid=214c-434b-92a2-d8e3-ab62-368f-ca9c-55ad; ph_aid=7c1819e5-c8a7-4b33-b1fd-2b3d6d361e4f-c4aa7611c4bf7-42394536397ec-c890ea005bc33; AMCV_5E00123F5245B2780A490D45%40AdobeOrg=-1303530583%7CMCIDTS%7C20353%7CMCMID%7C06790261715728494701226529254517509332%7CMCAAMLH-1695902808%7C12%7CMCAAMB-1695902808%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCOPTOUT-1695305208s%7CNONE%7CvVersion%7C3.3.0; salsify_session_id=e42aed4a-bf61-423b-b31c-e3428fd6185a; _gcl_au=1.1.1384537775.1695298023; audience=DIY; _tt_enable_cookie=1; _ttp=MpVNa4ReSR3cRfRmfeRyGL6cSo1; _pin_unauth=dWlkPVpESmhOelJqTUdZdE5qUTNZUzAwTURVNUxUa3hNak10TXpJNU5ESTVOMlJrT0dFNA; _fbp=fb.1.1695298063381.1970757761; BVBRANDID=eeff4e72-e2e4-4e7b-8b13-5be4383bd0fe; session_id=111568f2-7742-4fda-a1a0-534dee9faea1; g_amcv_refreshed=1; al_sess=FuA4EWsuT07UWryyq/3foK2odEFCox6DkOAvzb77hdpU/10fLcxb3DEgFHFR1zLU; AMCVS_5E00123F5245B2780A490D45%40AdobeOrg=1; IR_gbd=lowes.com; largeViewOw=List; DECLINED_DATE=1699598217376; region=central; kampyleUserSession=1699602108206; kampyleUserSessionsCount=110; kampyleUserPercentile=75.7049983558026; _lgsid=1699610746959; bm_sz=2659E0311E50BE68CE5BB0034D8839F5~YAAQJUYDF0TKC6WLAQAAiWeyuBVQ/Y2wdBVzkHfwhKqBNGojuxir6aMzjCUGElBbwzxSx8aPq67s3s+Km192PwxczE50Dnqe4qX+J9eUcbk/+7phpSdDngE5SDIwZ3Wrorc7FefFqz0SWhgIe6VYBOnVGMJ+0Bd5WGrE/lozrsueds2cAKwPNMBUC6/h8ESWrg5OT//t2njwkfEbSO/36DGh1qemRB8w7AO5WVsLCkoYn0W8BqlGtqaP9nuyhyqSG1etukDxLBxORb8RSyQokTGqAnA7II473Ad58HS26TR3QQ==~4403768~4404805; _abck=DFA77B82293FE18ADDA8E76B0207FE67~0~YAAQJUYDF0HKC6WLAQAAiWeyuAqWjdxFGgdOsL6INyV0ZLkluX6GzCkkR3WtgXWQljHzoTqW4x8BXxPtKVOSRG87Q++XenfIqrjY/vcAGJ4iMwARSOQa1zJaszLkZbZAQUJkyigNSXDoahiGjiiTt1htTelvsAaEgON8gBZTdGv60MorplaIuCRsrlj+JyUQfuGwz6p03pB8FPHuShFc2vrGCB/ukFB66jC4HnXbjStHhySuzOzNsSnrJsdLkzGXm7S6PEvUjB8sPEfvXBoEW96aHw1iqkkTxxqy8djX2PD8neO1bkwmyyA+zOBlP6VknZJsTjUsrgvoP7KhFIuwh55m9tgH8NDhlqYM0xsr6fjaEJGkEUjBg87FLo7vyN1xSlha6RBZ2GAM+ejlvKdiHo7+uCS9eS9Ye+L7vUf2UbhaRPSyYlopPfN9bHWxAi/ZQ3tuu5JgfAM=~-1~-1~-1; sn=1108; sd=%7B%22id%22%3A%221108%22%2C%22zip%22%3A%2297223%22%2C%22city%22%3A%22Tigard%22%2C%22state%22%3A%22OR%22%2C%22name%22%3A%22Tigard%20Lowe\'s%22%2C%22region%22%3A%2214%22%7D; AKA_A2=A; sbsd=s0MZZA/mdNZ1JgWs4Fb7S62C9GQWjqisfU6twjUjh+JRsQBiuqccLhAics9t8y/W027QZpl/dnU7c+SdtigMP7Le63sVyVyYdAmxmwhHeV3OssaYD1MEyXM26r0UI9XJ2h6+rESAD+MDZHzKl8Qo6zw==; seo-partner=gDTMXB9g7l46qsQ3gCM3qCMsoDgSmXpC; akavpau_cart=1699611089~id=dced5e7abcec717cd4dbed8df3aa3514; ak_bmsc=A16880CC44937783AE66C05FC5F0827E~000000000000000000000000000000~YAAQJUYDF+LLC6WLAQAAJoeyuBVNCiYfsIlxW07HZ7gm307Id5zv01kkMwPPD4OP22ex8ANeJCBVqLG87N+6P/Xgz88sgP/CTAAn8gBXiFZpqEdEsGiftK3oEbcBVNzlAFzSSXfDGafJd4BUR72L+79gehaNmjsGQRHSUu8t85gYmWn59stjlJajI0vzpiqfJk4wGT3fgsIRTo2I9LxyOazgRBiETD4bIJBdq375kWLi2F5lVmq3QGyODdI5lRF4XGtS3uNbx2vlgREeNLsIh2MaPiVj3GtG8bZXdIWjCVfdlRLOwZ1U+A248LCjLZ+fYEi+wK1zrt8qPrnGtA62XW8MvFMn7T24cP34xOmXDyO8X6DLK5s+/wXkmJuIn2m6ND/1E+PpBtItIef3cTrxwhZRMN0j3Q/lJSdnHKDOKe8rvAPaE5f1mJOldILKeuFlL/nUu7L5CffNvgwuDI+RDKeG10HkAkjR9ZOROIdI4PE3zUL2xwb0fKhIdAe4UjPvflW6B8h+kS1GOw774Pxe2O9Vo6rzNmNL+nJO8SL7jigePH04WCBXSUz7e6XXDlFwXp7Pqmbz8DTuTdZ7SAt4fp4yYCVzOql0/1J8DO1kWSGfHjjOWq9+726DaC2kuPO22P90L7QthoMnqs0lHJEQLXR+aGyKtr8wLgtRBVnKdXfeqhJNS3XlM3AyWb4ndqVGg48nISQtj4Q5jnFtXmf73ZiM; p13n=%7B%22zipCode%22%3A%2297223%22%2C%22storeId%22%3A%221108%22%2C%22state%22%3A%22OR%22%2C%22audienceList%22%3A%5B%22WPRO%22%5D%7D; __gads=ID=a76eac8d6a64e6e1:T=1695298003:RT=1699610792:S=ALNI_Ma5_Wibl3_BjZ9ZMNRj4QnPB_GcLA; __gpi=UID=00000c51f1966f5b:T=1695298003:RT=1699610792:S=ALNI_Mb35vnmbDV8cKKid8ghfO3lXwOVcA; zipcode=97223; nearbyid=1108; zipstate=OR; g_previous=%7B%22gpvPageLoadTime%22%3A%220.00%22%2C%22gpvPageScroll%22%3A%225%7C6%7C0%7C14019%22%2C%22gpvSitesections%22%3A%22tools%2Chand_tools%2Csockets_socket_adapters%2Csockets_socket_sets%22%2C%22gpvSiteId%22%3A%22desktop%22%2C%22gpvPageType%22%3A%22product-display%22%7D; fs_lua=1.1699610807289; fs_uid=#Q8RZE#80ea6f8a-f11d-4f00-9015-8a540c6c3000:be18bc41-96f1-4d3c-b561-f5dc3e07de29:1699610681587::2#2cbce093#/1720856482; IR_12374=1699610813140%7C0%7C1699610813140%7C%7C; IR_PI=0797604e-c40d-3b46-a503-10e1854d4dbe%7C1699697213140; kampyleSessionPageCounter=4; _uetsid=bc8c8df07ecb11ee960867bb56e8ed43; _uetvid=d8b1b190221911ee8f7e11b174e2fa16; prodNumber=3; akavpau_default=1699611120~id=4cb083d1fb5691c2b6f65bb4e21fdf2c; akaalb_prod_dual=1699697220~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=50eabfe4cdd492a4e149a434f1f4c2c3; bm_sv=E28BDE33FDA7D82459C1C79F3BAC56D7~YAAQJUYDFyzRC6WLAQAA8QCzuBVDaTXb5s8k4iFjioRvsvUyxoUXSKQinAXuAJM43GlbiPE3Pd2xKm/NEFHiNo9MOcL65PfUH6cDQ6HhSFC5sybZi26DmHwH9FUqNdn0XFJi/1Rl11nIAkhY+Wfl0V/9qwr99wVN/OCbjAbh81U4IzyqOYE7yooBFqJKwqhJcUstlSos0Mopi8FtTYhidpSQAY0Nrd5CJWRn0Jbem4Kk/BmHNCNf9z4TsB2gVoBY~1; RT="z=1&dm=lowes.com&si=50d49bd9-9d04-41f8-b91f-287fa41545fa&ss=losgdm28&sl=1&tt=fya&bcn=%2F%2F684d0d43.akstat.io%2F&ld=gf9&nu=47zbxtll&cl=tip"; _abck=DFA77B82293FE18ADDA8E76B0207FE67~-1~YAAQPaIauAKOr02LAQAADQJRhQpqDNiBaSVfdmmM9JV36jzHvATUCA6cTYIZxVktLG3H8znMAe20KSGmsuDOwxN+nuepK3Uf2UxZaFwU9PhlzkdCcuJFnoEHbJr27jhtGtxLGo3aGD8pK7wLXu/gYO9H2VVuYnTOzAkO+gM0MRnpIHWnfC0G3x8GK8V7UrwiDUOK1uSuPsOJFOiO+g0VRB6vcgR4ymonTiN0z9ziJHDJ8s+93JYmOc2CrQbf8CIq1vnnlr8GCoe653v4Vx6MtGbOekam5wc/IR8jWKdg21CXfWFYBAFIdaoH0AyF6afkU245HG8yzNwkPv6Pc0su3FMaMLA/6hCn2445W7Zf0FNKoabLEiySUR/umusn1kSWmrPiTXQdGkzipGz4FGD/y9vWSCXovKkbyLoZ7iehe3JjxHhtph8vGof/TUxSBpIn2DDZacZ7IJA=~0~-1~-1; sbsd=s7EdUS/KAlflm3bk0AxXZQoHlDhvB6INvNfQMtmpniDPyZpjCXelyv8hjhtREz8JS5tYP9e9PklPB0ahJRe1uQimvOLhVXcVcw4vYphDTyNSBeINJX3vnswCf3vvn1rSlM44g0LSR0jzak7JhoT8RQA==; akaalb_prod_dual=1699697261~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=040d8ea86b6bd7cfe6ce448a8eaf2a7f; akavpau_default=1699611161~id=142cdfda3ac71d4a976dcb7ab5977236; al_sess=brukgPJGNBK59A5xZcXk0VCvz9/6AuxD50uOB9kEq+Q/0+FnRTognkazZMEaxaDZ',
        'Cookie': 'dbidv2=8a78db4a-929a-4fb1-838a-0cf8654dd5d0; EPID=OGE3OGRiNGEtOTI5YS00ZmIxLTgzOGEtMGNmODY1NGRkNWQw; mdLogger=false; kampyle_userid=214c-434b-92a2-d8e3-ab62-368f-ca9c-55ad; ph_aid=7c1819e5-c8a7-4b33-b1fd-2b3d6d361e4f-c4aa7611c4bf7-42394536397ec-c890ea005bc33; AMCV_5E00123F5245B2780A490D45%40AdobeOrg=-1303530583%7CMCIDTS%7C20353%7CMCMID%7C06790261715728494701226529254517509332%7CMCAAMLH-1695902808%7C12%7CMCAAMB-1695902808%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCOPTOUT-1695305208s%7CNONE%7CvVersion%7C3.3.0; salsify_session_id=e42aed4a-bf61-423b-b31c-e3428fd6185a; _gcl_au=1.1.1384537775.1695298023; audience=DIY; _tt_enable_cookie=1; _ttp=MpVNa4ReSR3cRfRmfeRyGL6cSo1; _pin_unauth=dWlkPVpESmhOelJqTUdZdE5qUTNZUzAwTURVNUxUa3hNak10TXpJNU5ESTVOMlJrT0dFNA; _fbp=fb.1.1695298063381.1970757761; BVBRANDID=eeff4e72-e2e4-4e7b-8b13-5be4383bd0fe; session_id=111568f2-7742-4fda-a1a0-534dee9faea1; g_amcv_refreshed=1; al_sess=FuA4EWsuT07UWryyq/3foK2odEFCox6DkOAvzb77hdpU/10fLcxb3DEgFHFR1zLU; AMCVS_5E00123F5245B2780A490D45%40AdobeOrg=1; IR_gbd=lowes.com; largeViewOw=List; DECLINED_DATE=1699598217376; region=central; kampyleUserSession=1699602108206; kampyleUserSessionsCount=110; kampyleUserPercentile=75.7049983558026; _lgsid=1699610746959; bm_sz=2659E0311E50BE68CE5BB0034D8839F5~YAAQJUYDF0TKC6WLAQAAiWeyuBVQ/Y2wdBVzkHfwhKqBNGojuxir6aMzjCUGElBbwzxSx8aPq67s3s+Km192PwxczE50Dnqe4qX+J9eUcbk/+7phpSdDngE5SDIwZ3Wrorc7FefFqz0SWhgIe6VYBOnVGMJ+0Bd5WGrE/lozrsueds2cAKwPNMBUC6/h8ESWrg5OT//t2njwkfEbSO/36DGh1qemRB8w7AO5WVsLCkoYn0W8BqlGtqaP9nuyhyqSG1etukDxLBxORb8RSyQokTGqAnA7II473Ad58HS26TR3QQ==~4403768~4404805; _abck=DFA77B82293FE18ADDA8E76B0207FE67~0~YAAQJUYDF0HKC6WLAQAAiWeyuAqWjdxFGgdOsL6INyV0ZLkluX6GzCkkR3WtgXWQljHzoTqW4x8BXxPtKVOSRG87Q++XenfIqrjY/vcAGJ4iMwARSOQa1zJaszLkZbZAQUJkyigNSXDoahiGjiiTt1htTelvsAaEgON8gBZTdGv60MorplaIuCRsrlj+JyUQfuGwz6p03pB8FPHuShFc2vrGCB/ukFB66jC4HnXbjStHhySuzOzNsSnrJsdLkzGXm7S6PEvUjB8sPEfvXBoEW96aHw1iqkkTxxqy8djX2PD8neO1bkwmyyA+zOBlP6VknZJsTjUsrgvoP7KhFIuwh55m9tgH8NDhlqYM0xsr6fjaEJGkEUjBg87FLo7vyN1xSlha6RBZ2GAM+ejlvKdiHo7+uCS9eS9Ye+L7vUf2UbhaRPSyYlopPfN9bHWxAi/ZQ3tuu5JgfAM=~-1~-1~-1; AKA_A2=A; seo-partner=gDTMXB9g7l46qsQ3gCM3qCMsoDgSmXpC; ak_bmsc=A16880CC44937783AE66C05FC5F0827E~000000000000000000000000000000~YAAQJUYDF+LLC6WLAQAAJoeyuBVNCiYfsIlxW07HZ7gm307Id5zv01kkMwPPD4OP22ex8ANeJCBVqLG87N+6P/Xgz88sgP/CTAAn8gBXiFZpqEdEsGiftK3oEbcBVNzlAFzSSXfDGafJd4BUR72L+79gehaNmjsGQRHSUu8t85gYmWn59stjlJajI0vzpiqfJk4wGT3fgsIRTo2I9LxyOazgRBiETD4bIJBdq375kWLi2F5lVmq3QGyODdI5lRF4XGtS3uNbx2vlgREeNLsIh2MaPiVj3GtG8bZXdIWjCVfdlRLOwZ1U+A248LCjLZ+fYEi+wK1zrt8qPrnGtA62XW8MvFMn7T24cP34xOmXDyO8X6DLK5s+/wXkmJuIn2m6ND/1E+PpBtItIef3cTrxwhZRMN0j3Q/lJSdnHKDOKe8rvAPaE5f1mJOldILKeuFlL/nUu7L5CffNvgwuDI+RDKeG10HkAkjR9ZOROIdI4PE3zUL2xwb0fKhIdAe4UjPvflW6B8h+kS1GOw774Pxe2O9Vo6rzNmNL+nJO8SL7jigePH04WCBXSUz7e6XXDlFwXp7Pqmbz8DTuTdZ7SAt4fp4yYCVzOql0/1J8DO1kWSGfHjjOWq9+726DaC2kuPO22P90L7QthoMnqs0lHJEQLXR+aGyKtr8wLgtRBVnKdXfeqhJNS3XlM3AyWb4ndqVGg48nISQtj4Q5jnFtXmf73ZiM; sn=1738; sd=%7B%22id%22%3A%221738%22%2C%22zip%22%3A%2260174%22%2C%22city%22%3A%22Saint%20Charles%22%2C%22state%22%3A%22IL%22%2C%22name%22%3A%22ST.%20Charles%20Lowe\'s%22%2C%22region%22%3A%224%22%7D; sbsd=sh2Ass5DPV4Qfx7ySRxDMO4Wydaw9f2yH56+AT5iwZ1Etv5kHo0rumK+3HsBuOF8rBuQ9Ivr+QTVPdZXTel96cVM0+36X1+wq/XL9YdsKO8rYO8oH+J5BJvlIhYrUQe0tikXHSH72StBb2oxeceYhiw==; akavpau_cart=1699612001~id=3d764d3d821d7fc8b3e920cad2151d52; p13n=%7B%22zipCode%22%3A%2260174%22%2C%22storeId%22%3A%221738%22%2C%22state%22%3A%22IL%22%2C%22audienceList%22%3A%5B%22WPRO%22%5D%7D; __gads=ID=a76eac8d6a64e6e1:T=1695298003:RT=1699611703:S=ALNI_Ma5_Wibl3_BjZ9ZMNRj4QnPB_GcLA; __gpi=UID=00000c51f1966f5b:T=1695298003:RT=1699611703:S=ALNI_Mb35vnmbDV8cKKid8ghfO3lXwOVcA; g_previous=%7B%22gpvPageLoadTime%22%3A%220.00%22%2C%22gpvPageScroll%22%3A%225%7C6%7C0%7C13468%22%2C%22gpvSitesections%22%3A%22tools%2Chand_tools%2Csockets_socket_adapters%2Csockets_socket_sets%22%2C%22gpvSiteId%22%3A%22desktop%22%2C%22gpvPageType%22%3A%22product-display%22%7D; fs_lua=1.1699611705686; fs_uid=#Q8RZE#80ea6f8a-f11d-4f00-9015-8a540c6c3000:be18bc41-96f1-4d3c-b561-f5dc3e07de29:1699610681587::3#2cbce093#/1720856482; zipcode=60174; nearbyid=1738; zipstate=IL; IR_12374=1699611710563%7C0%7C1699611710563%7C%7C; IR_PI=0797604e-c40d-3b46-a503-10e1854d4dbe%7C1699698110563; kampyleSessionPageCounter=6; _uetsid=bc8c8df07ecb11ee960867bb56e8ed43; _uetvid=d8b1b190221911ee8f7e11b174e2fa16; prodNumber=4; akavpau_default=1699612029~id=0676fe52d984caab0b01e53995cbf851; akaalb_prod_dual=1699698129~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=4a299a1532bc417512c023cfbc8b5eab; bm_sv=E28BDE33FDA7D82459C1C79F3BAC56D7~YAAQXsMzuElq062LAQAAGODAuBUyXEVyBbbtaWmZ09qr+FX5I9HWmP+n9AmdH5xcUvDoB8n5IaXI5xZAEhgE4YOIEGQsZArQl3FEjJ/rfBG3x2julP4nUYT/2mc9fv1Rma4/FMwDz9DawvYpC8AOT/VucA0z8GwntmWlnYPOUepl7Zm0VhFoZgUq4hKCw70OZQMhUejCIdehzUgccuUcgdDaz3GWCI7kxcXrVm/homaBsirbTROFMpZ1SDVr+Wiy~1; RT="z=1&dm=lowes.com&si=50d49bd9-9d04-41f8-b91f-287fa41545fa&ss=losgdm28&sl=2&tt=ktr&bcn=%2F%2F684d0d43.akstat.io%2F&ld=jpkp&nu=47xp91kh&cl=kbs4"; _abck=DFA77B82293FE18ADDA8E76B0207FE67~-1~YAAQPaIauAKOr02LAQAADQJRhQpqDNiBaSVfdmmM9JV36jzHvATUCA6cTYIZxVktLG3H8znMAe20KSGmsuDOwxN+nuepK3Uf2UxZaFwU9PhlzkdCcuJFnoEHbJr27jhtGtxLGo3aGD8pK7wLXu/gYO9H2VVuYnTOzAkO+gM0MRnpIHWnfC0G3x8GK8V7UrwiDUOK1uSuPsOJFOiO+g0VRB6vcgR4ymonTiN0z9ziJHDJ8s+93JYmOc2CrQbf8CIq1vnnlr8GCoe653v4Vx6MtGbOekam5wc/IR8jWKdg21CXfWFYBAFIdaoH0AyF6afkU245HG8yzNwkPv6Pc0su3FMaMLA/6hCn2445W7Zf0FNKoabLEiySUR/umusn1kSWmrPiTXQdGkzipGz4FGD/y9vWSCXovKkbyLoZ7iehe3JjxHhtph8vGof/TUxSBpIn2DDZacZ7IJA=~0~-1~-1; sbsd=s7EdUS/KAlflm3bk0AxXZQoHlDhvB6INvNfQMtmpniDPyZpjCXelyv8hjhtREz8JS5tYP9e9PklPB0ahJRe1uQimvOLhVXcVcw4vYphDTyNSBeINJX3vnswCf3vvn1rSlM44g0LSR0jzak7JhoT8RQA==; akaalb_prod_dual=1699698228~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=17~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=c74b84bbf3ec0cfea921ef64bb7b6eb6; akavpau_default=1699612128~id=8047111b36388fb5a5afe6a8bc73a5c0; al_sess=brukgPJGNBK59A5xZcXk0cKgr1oFEn1AKnPLmh3m7BGCYKVzjvbgMZtINlfLuOR/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://www.lowes.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    return headers
  def get_response(self,url):
      # print(url)
      headers = self.get_headers()
      payload = {}
      # session = requests.Session()
      # session.mount('https://', CustomSSLAdapter())
      # response = session.get(url, headers=headers)
      host = 'brd.superproxy.io'
      port = 22225
      username = 'brd-customer-hl_4ac99c27-zone-residential_proxy_ramesh_test-gip-18bb44708fe00000'
      password = '4ktga8eol00j'
      session_id = random.random()
      proxy_url = ('http://{}-session-{}:{}@{}:{}'.format(username, session_id, password, host, port))
      proxies = {'http': proxy_url, 'https': proxy_url}
      #response = requests.get(url, headers=headers, proxies=proxies, verify=False)
      #response = requests.get(url, headers=headers, proxies=proxies)
      response = requests.request("GET", url, headers=headers, data=payload)
      print(response.text)
      return response

  def get_product_details(self,url, scraped_product_count,offset,adjustedNextOffset):
      response = self.get_response(url)
      print(response.text)
      response = response.json()
      total_product_count = response["itemCount"]
      elements = response["itemList"]
      for element in elements:
          #scraped_product_count = scraped_product_count+1
          row = {}
          row["product_count"] = total_product_count
          try:
              row["sku"] = element["product"]["description"]
          except:
              row["sku"] = None
          try:
              row["brand"] = element["product"]["brand"]
          except:
              row["brand"] = None
          try:
              row["modelId"] = element["product"]["modelId"]
          except:
              row["modelId"] = None
          try:
              row["product_url"] = element["product"]["pdURL"]
          except:
              row["product_url"] = None
          try:
              row["rating"] = element["product"]["rating"]
          except:
              row["rating"] = None
          try:
              row["reviewCount"] = element["product"]["reviewCount"]
          except:
              row["reviewCount"] = None
          try:
              row["sponsored"] = element["product"]["sponsored"]
          except:
              row["sponsored"] = None
          try:
              row["sellingPrice"] = element["location"]["price"]["sellingPrice"]
          except:
              row["sellingPrice"] = None
          try:
              row["baseprice"] = element["location"]["price"]["pricingDataList"][0]["basePrice"]
          except:
              row["baseprice"] = None
          try:
              row["finalPrice"] = element["location"]["price"]["pricingDataList"][0]["finalPrice"]
          except:
              row["finalPrice"] = None
          try:
              row["retailPrice"] = element["location"]["price"]["pricingDataList"][0]["retailPrice"]
          except:
              row["retailPrice"] = None
          try:
              row["isStock"] = element["location"]["promotionObj"]["isStockItem"]
          except:
              row["isStock"] = None
          try:
              row["delivery date"] = element["location"]["promotionObj"]["pickUpPrmsDate"]
          except:
              row["delivery date"] = None
          try:
              row["Total Quantity"] = element["location"]["itemInventory"]["itemAvailList"][1]["totalQty"]
          except:
              row["Total Quantity"] = None
          try:
              row["OnHand Quantity"] = element["location"]["itemInventory"]["itemAvailList"][1]["onhandQty"]
          except:
              row["OnHand Quantity"] = None
          try:
              row["Selected Store"] = response["selectedStore"]["storeName"]
          except:
              row["Selected Store"] = None
          try:
              row["zipcode"] = response["selectedStore"]["zipcode"]
          except:
              row["zipcode"] = None
          self.data.append(row)
      self.write_csv()
      if scraped_product_count < total_product_count:
          print(scraped_product_count)
          print(total_product_count)
          scraped_product_count = scraped_product_count + 24
          offset = offset+24
          adjustedNextOffset = adjustedNextOffset+24
          url = self.get_url(offset,adjustedNextOffset)
          self.get_product_details(url, scraped_product_count,offset,adjustedNextOffset)


keywords= ["paint+brush"]
for keyword in keywords:
    scraper = LowesSearchLinksScraper(keyword)