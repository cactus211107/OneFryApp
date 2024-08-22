import requests,json
with open('maps.key') as f:key=f.read()

place_url='https://maps.googleapis.com/maps/api/place/'
def _placeapi(suf,method='GET')->dict:return requests.request(method,place_url+suf+'&key='+key).json()

def getPlace(maps_id:str,fields:list|tuple=[]):return _placeapi(f'details/json?place_id={maps_id}{"&fields="+",".join(fields) if fields else ""}')['result']
def getPlaceText(query:str,fields:list|tuple=[]):return _placeapi(f'textsearch/json?query={query}{"&fields="+",".join(fields) if fields else ""}')['results'][0]
def exists(maps_id:str):
    return _placeapi(f'details/json?place_id={maps_id}&fields=place_id')['status'].upper()=='OK'

if __name__ == '__main__': # testing
    print(json.dumps(getPlace('ChIJN1t_tDeuEmsRUsoyG83frY4')))
    # print(getPlaceText('massimos pizza'))