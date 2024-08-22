from flask import *
import random,string,json,shutil,os,threading,datetime
import db,maps,image
_reset=True
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

def genid(a:int=1024,b:int=2**24,*,number:bool=True,strLenMin:int=5,strLenMax:int=16):return random.randint(a,b) if number else"".join([random.choice(string.ascii_letters+string.digits) for x in range(random.randint(strLenMin,strLenMax))])
def getDate():return datetime.datetime.now().strftime('%D-%M-%Y')
def getDatetime():return datetime.datetime.now().strftime('%D-%M-%Y %H:%M:%S.%d')
def getRestaurant(id):
    r=db.execute('SELECT * FROM RESTAURANTS WHERE ID=? LIMIT 1',(id,)).fetchone()
    if r:
        return {
            "id":r[0],
            "name":r[1],
            "address":r[2],
            "lat":r[3],
            "lon":r[4]
        }
    return False
def getReview(id):
    r=list(db.execute('SELECT * FROM REVIEWS WHERE ID=? LIMIT 1',(int(id),)).fetchone())
    r[5]=bool(r[5])
    r[6]=bool(r[6])
    r[7]=bool(r[7])
    return r
def _addRestaurantAuto(id,thumb):
    place=maps.getPlace(id,['geometry','name','formatted_address']) # TODO put nesciscary fields
    name=place['name']
    address=place['formatted_address']
    l=place['geometry']['location']
    lat=l['lat']
    lon=l['lng']
    db.execute('INSERT INTO RESTAURANTS VALUES (?,?,?,?,?,?)',(id,name,address,thumb,lat,lon))
def addRestaurantAuto(id,thumb):
    t=threading.Thread(target=_addRestaurantAuto,args=(id,thumb))
    t.start()
def post(image_ids:list[str],type:str,fresh:bool,toppings:bool,spiced:bool,restaurant:str,comments:str,reviewer_id:int=None): # TODO implement users
    review_id=genid()
    db.execute(f'INSERT INTO REVIEWS VALUES ({"?,"*9}?)',(
        review_id,
        json.dumps(image_ids),
        restaurant,
        comments,
        type,
        fresh*1,
        toppings*1,
        spiced*1,
        getDatetime(),
        reviewer_id,
    ))
    return review_id
def getUser(id):
    # return db.execute('SELECT * FROM UESRS WHERE ID=?',(id,))
    return {"id":id,"name":'Jack Rushmore'} # because i dont have users yet



@app.route('/')
def index():
    return render_template('index.html',fry_types=FRY_TYPES)

@app.route('/review',methods=['POST'])
def review_api():
    def er(e):return{"status":"error","error":e}
    f=request.form.get
    images=request.files.getlist('images')
    restaurant=f('restaurant')
    comments=f('comments')
    fry_type=f('fryType')
    fresh=f('isFresh','n')
    toppings=f('hasToppings','n')
    spiced=f('isSpiced','n')
    if 'n' in [fresh,toppings,spiced]:
        return er('Fresh, Toppings, Spiced must exist')
    if fry_type not in FRY_TYPES:
        return er(f'Fry type "{fry_type}" is not valid.')
    for img in images: # initial checks
        if not img.mimetype.startswith('image/'):
            return er("All uploaded files must be images.")
    if not maps.exists(restaurant):
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
        addRestaurantAuto(restaurant,f'usercontent/uploads/{img_ids[0]}.webp')
    reviewer=0
    rev_id=post(img_ids,fry_type,fresh,toppings,spiced,restaurant,comments,reviewer)
    return {
        "status":"ok",
        "restaurant":getRestaurant(restaurant),
        "review":review_get_api(rev_id),
        "user":getUser(reviewer)
    }

@app.route('/getreview/<id>',methods=['GET'])
def review_get_api(id):
    review=getReview(id)
    if review:
        return {
            "status":"ok",
            "id":review[0],
            "images":json.loads(review[1]),
            "restaurant":review[2],
            "comments":review[3],
            "fryType":review[4],
            "fresh":review[5],
            "toppings":review[6],
            "spiced":review[7],
            "reviewDate":review[8],
        }
    return {
        "status":"error",
        "error":"Review does not exist."
    }

    
@app.route('/usercontent/<path:path>')
def usercontent(path):
    return send_file(os.path.join('usercontent',path))

    



@app.context_processor
def inject_maps_api_key():return {
    'maps_key': maps.key,
    }

def run(*,run_on_network:bool=False,local_port:int=4096,network_port:int=80,debug:bool=False):app.run('0.0.0.0'if run_on_network else None,network_port if run_on_network else local_port,debug)


run(run_on_network=False,debug=True)