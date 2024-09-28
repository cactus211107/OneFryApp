from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import random,string,json,shutil,os,threading,datetime,time,typing as t
import db,maps,image,relevance
_reset=0
if _reset:
    try:os.remove('database.db')
    except:0
    try:shutil.rmtree('usercontent/uploads')
    except:0
db.initDB('database.db')
db.executeFile('.sql')

with open('session.key') as f:Flask.secret_key=f.read()
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
def xm(n,s=','):return(("?"+s)*(n-1))+"?"
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
            reviews=db.execute('SELECT RATING,RELEVANCE FROM REVIEWS WHERE RESTAURANT=?',(id,)).fetchall()
            s=sum([rev[0] for rev in reviews])
            s2=sum([rev[1] for rev in reviews])
            l=len(reviews)
            rdict['reviews']=l
            rdict['rating']=s/l if l>0 else 1
            rdict['score']=((rdict['rating']/2.5))**l
            rdict['relevance']=s2/l if l>0 else 1
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
    db.execute(f'INSERT INTO RESTAURANTS VALUES ({xm(6)})',(id,name,address,thumb,lat,lon))
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
    db.execute(f'INSERT INTO REVIEWS VALUES ({xm(14)})',(
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
        "",
        0
    ))
    rel_thread=threading.Thread(target=addRelevancyThread,args=(review_id,comments))
    rel_thread.start()
    return review_id
def generateToken(id):
    return f"{id}.{genid(number=False)}.{int(time.time())}"
def createUser(name,password,loginType,id=None,token=None,join_date=None):
    id=id or genid(number=False)
    token=token or generateToken(id)
    join_date=join_date or getDatetime()
    password=generate_password_hash(password)
    db.execute(f'INSERT INTO USERS VALUES ({xm(6)})',(id,token,name,password,loginType,join_date))
    return id
def getUser(id,includePassword=False,includesToken=False):
    u=db.execute('SELECT * FROM USERS WHERE ID=? LIMIT 1',(id,)).fetchone()
    # return {"id":id,"name":'Jack Rushmore'} # because i dont have users yet
    return {
        "id":u[0],
        **({"token": u[1]} if includesToken else {}),
        "name":u[2],
        **({"password": u[3]} if includePassword else {}),
        **({"loginType": u[4]} if includePassword else {}),
        "joined":u[5],
    }
def setReviewState(id,state:t.Literal['unprocessed','processed','hidden','deleted']):
    state=('unprocessed','processed','hidden','deleted').index(state)
    db.execute('UPDATE REVIEWS SET STATE=? WHERE ID=?',(state,id))
def deleteReview(id,justHidden=False):
    if justHidden:
        setReviewState(id,'deleted')
        return
    db.execute('DELETE FROM REVIEWS WHERE ID=?',(id,))
def getUserFromToken(cookie_token):
    u=db.execute('SELECT ID FROM USERS WHERE TOKEN=? LIMIT 1',(cookie_token,)).fetchone()
    if db.isError(u):
        return None
    return getUser(u[0])
def logout(session):
    if 'token' in session:
        session.pop('token')
def isLoggedIn(session):
    if 'token' in session:
        return bool(getUserFromToken(session['token']))
    return False
def er(e):return{"status":"error","error":e}

@app.route('/')
def index():
    return render_template('index.html',
                           fry_types=FRY_TYPES,
                           isLoggedIn=isLoggedIn(session),
                           user=getUserFromToken(session.get('token')),
                           userIsAdmin=True
                           )

@app.route('/review',methods=['POST'])
def review_api():
    if not isLoggedIn(session):
        return er('You must be logged in to review.')
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
    if not restaurant:
        return er('No restaurant provided.')
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
    reviewer=getUserFromToken(session.get('token'))['id']
    rev_id=post(img_ids,rating,fry_type,fresh,toppings,spiced,restaurant,comments,reviewer)
    return {
        "status":"ok",
        "restaurant":getRestaurant(restaurant,includeRating=True),
        "review":review_get_api(rev_id,d2t=True),
        "user":getUser(reviewer)
    }

@app.route('/api/getreview/<id>',methods=['GET'])
def review_get_api(id,d2t=False,includesState=False,stringState=True):
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
            "relevance":review[11],
            **({"state":('unprocessed','processed','hidden','deleted')[review[12]] if stringState else review[12]}if includesState else{})
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
    u={}
    if session.get('token'):
        u=getUserFromToken(session.get('token'))
    review_id=request.args.get('current_review',type=str)
    human_readable_date=request.args.get('date')=='human'


    if getRestaurant(id):
        order_by='REVIEW_DATE' if sort in ['newest','oldest'] else 'RATING' if sort in ['highest','lowest'] else 'RELEVANCE'
        dir='ASC' if sort in ['oldest','lowest'] else 'DESC'
        reviews = db.execute(f'''
            SELECT ID
            FROM REVIEWS
            WHERE RESTAURANT = ?
            ORDER BY 
                CASE 
                    WHEN ID = ? THEN 1  -- Current review_id first
                    WHEN REVIEWER = ? THEN 2  -- Reviews by the current user second
                    ELSE 3  -- Other reviews
                END, 
                {order_by} {dir}
            LIMIT ?''', (id, review_id, u.get('id','not_a_user'), stop)).fetchall()
        start=min(start,len(reviews)-1)
        stop=min(stop,len(reviews)-1)
        reviews=reviews[start:]
        return {"status":"ok","start":start,"stop":stop,"reviews":[review_get_api(review[0],human_readable_date) for review in reviews]}

@app.route('/api/userreviews/<id>')
def api_user_reviews(id):
    reviews=db.execute('SELECT ID FROM REVIEWS WHERE REVIEWER=?',(id,)).fetchall()
    reviews=[getReview(r[0]) for r in reviews]
    return reviews


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

@app.route('/api/register',methods=['POST'])
def api_register_user():
    username=request.form.get('username')
    password=request.form.get('password')
    if not username:
        return er('No username provided')
    if not password:
        return er('No password provided')
    user=db.execute('SELECT * FROM USERS WHERE NAME=? LIMIT 1',(username,)).fetchone()
    print(user)
    if user: # User exists
        if check_password_hash(user[3],password):
            session['token']=user[1]
            return{"status":"ok"}
        return er('Invalid Log In Credentials')
    id=createUser(username,password,0) # loginType=0 : Email (basic login bc no email yet)
    user=getUser(id,includesToken=1)
    session['token']=user['token']
    user.pop('token')
    return{"status":"ok","user":user}
    


@app.route('/usercontent/<path:path>')
def usercontent(path):
    return send_file(os.path.join('usercontent',path))

    

@app.before_request
def before_request():
    if not isLoggedIn(session):
        logout(session)

@app.context_processor
def inject_maps_api_key():return {
    'maps_key': maps.key,
    'str':str,
    'int':int,
    'float':float,
    'bool':bool,
    'list':list,
    'dict':dict
    }

def run(*,run_on_network:bool=False,local_port:int=4096,network_port:int=80,debug:bool=False):app.run('0.0.0.0'if run_on_network else None,network_port if run_on_network else local_port,debug)


run(run_on_network=False,debug=True)