from flask import *
import random,string,json,shutil,os,threading,datetime
import db,maps,image,relevance
_reset=False
if _reset:
    try:os.remove('database.db')
    except:0
    try:shutil.rmtree('usercontent/uploads')
    except:0
db.initDB('database.db')
db.executeFile('.sql')



Flask.secret_key='so, do you like fries?! Well... I do, so yeah. And btw this is the 53C3T key!!!'
FRY_TYPES=[
    'Regular Fries',
    'Steak Fries',
    'Shoestring Fries',
    'Crinkle Fries',
    'Waffle Fries',
    'Wedges',
    'Tater Tots',
    'Cottage Fries',
    'Sweet Potato Fries',
    'Curly Fries',
]
app = Flask(__name__)
REVIEW_COMMENTS_REQUIRED=True
DATE_FORMAT='%d-%m-%y'
DATETIME_FORMAT=DATE_FORMAT+'/%H:%M:%S.%f'

def genid(a:int=1024,b:int=2**24,*,number:bool=True,strLenMin:int=5,strLenMax:int=16):return random.randint(a,b) if number else"".join([random.choice(string.ascii_letters+string.digits) for x in range(random.randint(strLenMin,strLenMax))])
def getDate():return datetime.datetime.now().strftime(DATE_FORMAT)
def getDatetime():return datetime.datetime.now().strftime('%d-%m-%y/%H:%M:%S.%f')
def textToDatetime(dt):return datetime.datetime.strptime(dt,DATETIME_FORMAT)
def dateToText(date:datetime.datetime,isDatetime=False):return f"{['January','February','March','April','May','June','July','August','September','October','November','December'][date.month-1]} {date.day}, {date.year}{f' at {date.hour}:{date.minute}:{date.second}'if isDatetime else''}"
def getRestaurant(id,*,includeRating=False):
    r=db.execute('SELECT * FROM RESTAURANTS WHERE ID=? LIMIT 1',(id,)).fetchone()
    print('RRRRR',r)
    if r:
        rdict={
            "id":r[0],
            "name":r[1],
            "address":r[2],
            "thumbnail":r[3],
            "lat":r[4],
            "lon":r[5]
        }
        if includeRating:
            reviews=db.execute('SELECT RATING FROM REVIEWS WHERE RESTAURANT=?',(id,)).fetchall()
            s=sum([rev[0] for rev in reviews])
            l=len(reviews)
            rdict['reviews']=l
            rdict['rating']=s/l if l>0 else 0
            rdict['score']=((rdict['rating']/2.5))**l
        return rdict
    return {}
def getReview(id):
    r=list(db.execute('SELECT * FROM REVIEWS WHERE ID=? LIMIT 1',(int(id),)).fetchone())
    r[5]=bool(r[5])
    r[6]=bool(r[6])
    r[7]=bool(r[7])
    return r
def _addRestaurantAuto(id,thumb,google_data):
    place=google_data
    if not google_data:
        place=maps.getPlace(id,['geometry','name','formatted_address']) # TODO put nesciscary fields
    name=place['name']
    address=place['formatted_address']
    l=place['geometry']['location']
    lat=l['lat']
    lon=l['lng']
    db.execute('INSERT INTO RESTAURANTS VALUES (?,?,?,?,?,?)',(id,name,address,thumb,lat,lon))
def addRestaurantAuto(id,thumb,*,google_data:dict=None):
    if google_data:_addRestaurantAuto(id,thumb,google_data)
    else:
        t=threading.Thread(target=_addRestaurantAuto,args=(id,thumb,google_data))
        t.start()
def post(image_ids:list[str],rating:int,type:str,fresh:bool,toppings:bool,spiced:bool,restaurant:str,comments:str,reviewer_id:int=None): # TODO implement users
    review_id=genid()
    def addRelevancyThread(rid,comments):
        # I put it in a thread because it takes up time
        # about 4 seconds, so it is fast to review.
        # but if I get a server, it should be faster
        rel=relevance.getRelevancy(comments)
        db.execute('UPDATE REVIEWS SET RELEVANCE=?,RELEVANCE_REASON=? WHERE ID=?',(rel['relevance'],rel['reason'],rid))
    db.execute(f'INSERT INTO REVIEWS VALUES ({"?,"*12}?)',(
        review_id,
        json.dumps(image_ids),
        rating,
        restaurant,
        comments,
        type,
        fresh*1,
        toppings*1,
        spiced*1,
        getDatetime(),
        reviewer_id,
        100,
        ""
    ))
    rel_thread=threading.Thread(target=addRelevancyThread,args=(review_id,comments))
    rel_thread.start()
    return review_id
def getUser(id):
    # return db.execute('SELECT * FROM UESRS WHERE ID=?',(id,))
    return {"id":id,"name":'Jack Rushmore'} # because i dont have users yet
def er(e):return{"status":"error","error":e}

@app.route('/')
def index():
    return render_template('index.html',fry_types=FRY_TYPES,userIsAdmin=True)

@app.route('/review',methods=['POST'])
def review_api():
    f=request.form.get
    images=request.files.getlist('images')
    rating=f('rating',-1,type=int)
    if rating==-1:
        return er('Rating could not be converted to an integer.')
    restaurant=f('restaurant',type=str)
    comments=f('comments',type=str)
    fry_type=f('fryType',type=str)
    fresh=f('isFresh',False,type=bool)
    toppings=f('hasToppings',False,type=bool)
    spiced=f('isSpiced',False,type=bool)
    if 1>rating>5:
        return er('Rating must be between 1 and 5.')
    if fry_type not in FRY_TYPES:
        return er(f'Fry type "{fry_type}" is not valid.')
    for img in images: # initial checks
        if not img.mimetype.startswith('image/'):
            return er("All uploaded files must be images.")
    gd=maps.getPlace(restaurant) #gd==google data
    if type(gd.get('geometry'))!=dict:
        return er(f'Place id "{restaurant}" does not exist.')
    if not comments and REVIEW_COMMENTS_REQUIRED:
        return er("Comments are required.\nThat is where you write your review.")
    
    finished_imgs=[]
    img_ids=[]
    os.makedirs('usercontent/temp',exist_ok=True)
    os.makedirs('usercontent/uploads',exist_ok=True)
    try: # Saving images with error handling
        for img in images:
            id=genid(number=False)
            ext=img.mimetype.split('/')[1]
            temp_path=f'usercontent/temp/{id}.'+ext
            save_path=f'usercontent/uploads/{id}.webp'
            img.save(temp_path)
            finished_imgs.append((save_path,temp_path))
            img_ids.append(id)
            image.compress_image(temp_path,save_path)
            os.remove(temp_path)
    except Exception as e:
        print(e)
        for img in finished_imgs:
            try:os.remove(img[0])
            except:0
            try:os.remove(img[1])
            except:0
        return er('Error when compressing / saving images.')
    
    if not getRestaurant(restaurant):
        addRestaurantAuto(restaurant,f'usercontent/uploads/{img_ids[0]}.webp',google_data=gd)
    reviewer=0
    rev_id=post(img_ids,rating,fry_type,fresh,toppings,spiced,restaurant,comments,reviewer)
    return {
        "status":"ok",
        "restaurant":getRestaurant(restaurant,includeRating=True),
        "review":review_get_api(rev_id,d2t=True),
        "user":getUser(reviewer)
    }

@app.route('/api/getreview/<id>',methods=['GET'])
def review_get_api(id,d2t=False):
    review=getReview(id)
    if review:
        return {
            "status":"ok",
            "id":review[0],
            "images":json.loads(review[1]),
            "rating":review[2],
            "restaurant":review[3],
            "comments":review[4],
            "fryType":review[5],
            "fresh":review[6],
            "toppings":review[7],
            "spiced":review[8],
            "reviewDate":dateToText(textToDatetime(review[9])) if d2t else review[9],
            "reviewer":getUser(review[10]),
            "relevance":review[11]
        }
    return {
        "status":"error",
        "error":"Review does not exist."
    }

@app.route('/api/reviews/<id>',methods=['GET'])
def restaurant_reviews_api(id):
    start=request.args.get('start',0,type=int)
    if start<0:
        start=0
    stop=request.args.get('stop',20,type=int)
    if stop<=start:
        stop=start+1
    sort=request.args.get('sort','relevance').lower()
    if sort not in ['newest','oldest','highest','lowest','relevance']:
        sort='relevance'
    if getRestaurant(id):
        order_by='REVIEW_DATE' if sort in ['newest','oldest'] else 'RATING' if sort in ['highest','lowest'] else 'RELEVANCE'
        dir='ASC' if sort in ['oldest','lowest'] else 'DESC'
        reviews=db.execute(f'SELECT ID FROM REVIEWS WHERE RESTAURANT=? ORDER BY {order_by} {dir} LIMIT ?',(id,stop)).fetchall()
        start=min(start,len(reviews)-1)
        stop=min(stop,len(reviews)-1)
        reviews=reviews[start:]
        return {"status":"ok","start":start,"stop":stop,"reviews":[review_get_api(review[0]) for review in reviews]}

@app.route('/api/restaurant/<id>')
def restaurant_get_api(id):
    return getRestaurant(id,includeRating=True)

@app.route('/api/restaurants')
def all_restaurants_api():
    # TODO: Add bounds (provided by client) `... WHERE LAT < LAT_MAX AND LAT > LAT_MIN AND LON < LON_MAX AND LON > LON_MIN`
    rs=db.execute('SELECT ID,NAME,LAT,LON FROM RESTAURANTS').fetchall()
    return [{
        "id":r[0],
        "name":r[1],
        "lat":r[2],
        "lon":r[3],
    } for r in rs]

@app.route('/api/search/restaurants')
def api_restaurant_search():
    query=request.args.get('query')
    results=request.args.get('results',5,int)
    sort=request.args.get('sort','default')
    if not query:return er("You must provide a query.")
    if results<1:return er("Results cannot be less than 1.")
    if sort not in ['highest','lowest','most','least','default']:sort='highest'

    restaurants=db.execute("SELECT ID FROM RESTAURANTS WHERE NAME LIKE '%' || ? || '%' LIMIT ?",(query,results)).fetchall()
    restaurants=sorted([getRestaurant(restaurant[0],includeRating=True) for restaurant in restaurants],key=lambda x:x['reviews'] if sort in ['most','least'] else x['rating'] if sort in ['highest','lowest'] else x['score'],reverse=sort in ['most','highest'])

    return {"status":"ok","results":restaurants}


@app.route('/usercontent/<path:path>')
def usercontent(path):
    return send_file(os.path.join('usercontent',path))

    



@app.context_processor
def inject_maps_api_key():return {
    'maps_key': maps.key,
    }

def run(*,run_on_network:bool=False,local_port:int=4096,network_port:int=80,debug:bool=False):app.run('0.0.0.0'if run_on_network else None,network_port if run_on_network else local_port,debug)


run(run_on_network=False,debug=True)