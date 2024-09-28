function getBottomNavChecked() {
    return document.querySelector('[name="vbtn-radio"]:checked')
}
const fryTypes = window.fryTypes
const rating_slider=document.querySelector('#rating')
const rating_text=document.querySelector('#rating-text')
const rating_value=document.querySelector('#rating-value')

const image_upload_next=document.querySelector('#next-btn-rev-img')
const options_next=document.querySelector('#next-btn-rev-opts')

const review_submit_btn=document.querySelector('#review')
const review_modals=document.querySelector('.modals > .review-modals');

const is_fresh_box=document.querySelector('#freshOrFrozen')
const has_toppings_box=document.querySelector('#hasToppings')
const is_spiced_box=document.querySelector('#isSpiced')
const comment_box=document.querySelector('#comments')

const restaurant_thumbnail=document.querySelector('#restaurant-thumbnail')
const restaurant_name=document.querySelector('#restaurant-name')
const restaurant_address=document.querySelector('#restaurant-address')
const restaurant_rating=document.querySelector('#restaurant-rating')
const reviews_elm=document.querySelector('#restaurant-page .reviews')

const restaurant_nav_btn=document.querySelector('#bottom-nav-restaurant')
restaurant_nav_btn.addEventListener('click',()=>{
    if (restaurant_address.innerText) {
        moveBox('restaurant-page','right')
    } else {
        try {
            getBottomNavChecked().checked=false
            search_page_select.checked=true
        }catch{}
        moveBox('search-page','left')
    }
})

const signInForm=document.querySelector('#signinForm')
const signInUsername=document.querySelector('#signinUsername')
const signInPw=document.querySelector('#signinPassword')
const signInSubmit=document.querySelector('#signinSubmit')

signInForm.addEventListener('submit',e=>{
    e.preventDefault()
    const body=new FormData()
    body.append('username',signInUsername.value)
    body.append('password',signInPw.value)
    if (!signInUsername.value) {
        invalidFormInput('signin-page',signInUsername,'Invalid Input','No username provided.',null,'left')
        return
    }
    if (!signInPw.value) {
        invalidFormInput('signin-page',signInPw,'Invalid Input','No password provided.',null,'left')
        return
    }
    fetch('/api/register',{"method":"post","body":body}).then(request=>request.json()).then(result=>{
        if (result.status=='error') {
            invalidFormInput('signin-page',signInUsername,'Invalid Input',result.error,null,'right')
        } else {
            window.location.reload()
        }
    })
})

const search_page_results=document.querySelector('#search-page-results')
const search_page_filter=document.querySelector('#search-page-filter')

const restaurant_input=document.querySelector('#restaurant-search')
const restaurant_search_results=document.querySelector('#restaurant-search-results')
restaurant_input.addEventListener('input',async ()=>{
    if (!restaurant_input.value){
        restaurant_search_results.innerHTML=''
        return
    }
    const results=await performTextSearch(restaurant_input.value);
    restaurant_search_results.innerHTML=''
    if (!results)return;
    for (const result of results) {
        const id='r'+Math.random().toString().replace('.',0)
        const elm=document.createElement('div')
        elm.className='restaurant-search-result'
        elm.id=id
        elm.innerHTML=`
            <div class="restaurant-info d-flex flex-column">
                <div class="border-0 outline text-truncate">${result.name}</div>
                <div class="restaurant-address text-truncate">${result.address}</div>
            </div>
            <div class="restaurant-image d-flex align-items-center justify-content-center bg-secondary rounded-1">
                <img src="${result.photo}" alt="🍟">
            </div>`
        elm.addEventListener('click',()=>{
            let r=result;
            console.log(r)
            review_selected_restaurant=r.id
            document.querySelector('#review-restaurant-final').innerText=r.name
            document.querySelector('#restaurant-image-final').src=r.photo
            document.querySelector('#review-restaurant-address-final').innerText=r.address
        })
        restaurant_search_results.append(elm)
    }
})
function getFryTypeElm() {
    return document.querySelector('[name="fryType"]:checked')
}
async function getRestaurant(id) {
    let data=await fetch('/api/restaurant/'+id).then(r=>r.json()).then(_=>{return _})
    return data
}
let review_selected_restaurant = ''
let selected_restaurant=''
let restaurant_reviews_start=0;
let restaurant_reviews_stop=20;
function getRestauantReviews(id,start,stop,sort,callback,cur_review=-1) {
    fetch(`/api/reviews/${id}?start=${start}&stop=${stop}&sort=${sort}&current_review=${cur_review}&date=human`).then(response=>response.json()).then(callback)
}
function addRestaurantReviews(id,start,stop,sort,cur_review=-1) {
    getUserReviews()
    review_modals.innerHTML=''
    reviews_elm.innerHTML=''
    getRestauantReviews(id,start,stop,sort,result=>{
        console.log(result)
        if (result.status!='ok')return;
        for (const review of result.reviews) {
            addReview(reviews_elm,review)
        }
    })
}
const rating_to_text=[
    ["Bad","Do not go"],
    ["Meh","Not worth driving for"],
    ["Good","Would drive from across town"],
    ["Excellent","Worth taking a long drive"],
    ["Legendary","Worth driving from anywhere"]
]
function update_rating_text() {
    let r=rating_to_text[Math.min(Math.max(rating_slider.value-1,0),4)];
    rating_text.innerText=r[0];
    rating_value.innerText=r[1];
}
function invalidFormElm(elm,title,content,parent,dir='top') {
    $(elm).popover({
        title:title,
        content:content,
        trigger: 'manual',
        container:parent,
        html: true,
        customClass:"text-bg-warning",
        placement:dir,
    });
    $(elm).popover('show')
    parent.addEventListener('click',()=>{
        $(elm).popover('hide')
    })
    // if (hides)setTimeout(()=>{x.hide()},hideAfter*1e3)
    // return x
    
}
function addReview(parent,review) {
    parent.innerHTML+=`<div class="review" id="review-${review.id}">
                <section class="top-review">
                    <div class="reviewer-name">${review.reviewer.name}</div>
                    <div class="review-date">${review.reviewDate}</div>
                </section>
                <section class="bottom-review">
                    <section class="left-review">
                        <div class="review-image-thumb" data-bs-toggle="modal" data-bs-target="#modal-${review.id}"> <!-- When any elm with that tag clicked, it opens a bootstrap modal with the images in a carousel. -->
                            <img src="/usercontent/uploads/${review.images[0]}.webp" alt>
                        </div>
                    </section>
                    <section class="right-review">
                        <div class="comments">${review.comments}</div>
                    </section>
                </section>
            </div>`
    review_modals.innerHTML+=`<div class="modal fade" id="modal-${review.id}" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h1 class="modal-title fs-5" id="exampleModalLabel">Images</h1>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                Carousel of images will be here.
                            </div>
                        </div>
                    </div>
                </div>`
}
rating_slider.addEventListener('input',update_rating_text)
update_rating_text()

const illegal = setInterval(()=>{
    // illegalism
    try {
        document.querySelector('.gmnoprint').parentElement.remove()
        document.querySelector('img[alt="Google"]').parentElement.remove()
    }catch{}
},100)

const search_page_select=document.querySelector('#radio-btn3')
const search_input=document.querySelector('#search')
search_input.addEventListener('input',()=>{
    if (!search_input.value) {
        search_page_results.innerHTML=''
        return
    }
    // &search_page_filter.value
    fetch(`/api/search/restaurants?query=${search_input.value}`).then(response=>response.json()).then(result=>{
        search_page_results.innerHTML=''
        console.log(result)
        if (result.status!=='ok') {
            return
        }
        for (const restaurant of result.results) {
            const elm=document.createElement('div')
            const id='r'+Math.random().toString().replace('.',0)
            elm.className='restaurant-search-result'
            elm.id=id
            elm.innerHTML=`
                <div class="restaurant-image d-flex align-items-center justify-content-center bg-secondary rounded-1">
                    <img src="${restaurant.thumbnail}" alt="🍟">
                </div>
                <div class="restaurant-info d-flex flex-column">
                    <div class="border-0 outline text-truncate">${restaurant.name}</div>
                    <div class="stars">
                        ${ratingStarsText(restaurant.rating)}
                        (${restaurant.reviews} review${restaurant.reviews.length!==1?'s':''})
                    </div>
                    <div class="restaurant-address text-truncate">${restaurant.address}</div>
                </div>
                `
            elm.addEventListener('click',()=>{
                _putRestaurant(restaurant)
                moveBox('restaurant-page','right')
            })
            search_page_results.append(elm)
        }
    })
})
search_input.addEventListener('focus',()=>{
    moveBox("search-page",'left')
})
search_page_select.addEventListener('click',()=>{
    search_input.focus()
})


function getReviewValues() {
    return {
        files:dropzone.files,
        rating:parseInt(rating_slider.value),
        fry_type:getFryTypeElm().value,
        fresh:is_fresh_box.checked,
        hasToppings:has_toppings_box.checked,
        isSpiced:is_spiced_box.checked,
        restaurant:review_selected_restaurant,
        comments:comment_box.value
    }
}
async function invalidFormInput(page,elm,error_title,error_content,box_dir='left',popover_dir='top') {
    let epage=$("#"+page)
    moveBox(page,box_dir)
    await wait(1000)
    invalidFormElm(elm,error_title,error_content,epage[0],dir=popover_dir)
    console.error(error_content)
    // throw new Error("Rating not between 1 and 5");
}
function _putRestaurant(data,cur_review=-1) {
    restaurant_thumbnail.src=data.thumbnail
    restaurant_name.innerText=data.name
    restaurant_address.innerText=data.address

    restaurant_rating.innerHTML=''
    ratingStars(restaurant_rating,data.rating)
    restaurant_rating.innerHTML+=`<span>(${data.reviews} review${data.reviews==1?'':'s'})</span>`
    addRestaurantReviews(data.id,0,20,'relevance',cur_review)
}
function resetReviewForm() {
    dropzone.removeAllFiles()
    rating_slider.value=3
    getFryTypeElm().checked=false
    is_fresh_box.checked=false
    is_spiced_box.checked=false
    has_toppings_box.checked=false
    review_selected_restaurant=''
    document.querySelector('.selected-restaurant').innerHTML=
    `   <div class="restaurant-info d-flex flex-column">
            <div id="review-restaurant-final" class="border-0 outline text-truncate">No Restaurant Selected</div>
            <div id="review-restaurant-address-final" class="restaurant-address text-truncate">Fry Rd, Pennsylvania, USA</div>
        </div>
        <div class="restaurant-image d-flex align-items-center justify-content-center bg-secondary rounded-1">
            <i class="bi bi-shop"></i>
            <img src="" alt="" id="restaurant-image-final">
        </div>
    `
    comment_box.value=''
    restaurant_input.value=''
    restaurant_search_results.innerHTML=''
}
review_submit_btn.addEventListener('click',e=>{                         if(!e.isTrusted)return;
    const values=getReviewValues()

    if (values.rating<1||values.rating>5) { // checks
        invalidFormInput('review-2',rating_slider,'Invalid Input!',"Rating not between 1 and 5",'left','bottom')
        return
    }
    if (values.files.length<1) {
        invalidFormInput('review-3',document.querySelector('.dropzone'),'Invalid Input!',"A file must be uploaded",'left','bottom')
        return
    }
    if (!fryTypes.includes(values.fry_type)) {
        invalidFormInput('review-2',getFryTypeElm(),'Invalid Input!',`Invalid Fry Type "${values.fry_type}"`,'left','right')
        return
    }
    const formData=new FormData();
    for (const file of values.files) {
        formData.append('images',file)
    }
    formData.append('isFresh',values.fresh)
    formData.append('hasToppings',values.hasToppings)
    formData.append('isSpiced',values.isSpiced)
    formData.append('fryType',values.fry_type)
    formData.append('rating',values.rating)
    formData.append('restaurant',values.restaurant)
    formData.append('comments',values.comments)
    
    // formData.append()
    fetch('/review',{method:"POST",body:formData}).then(response=>response.json()).then(result=>{
        console.log(result)
        if (result.status=='error') {
            invalidFormInput('review-4',review_submit_btn,'Invalid Input!',result.error,)
        }
        if (result.status=='ok') {
            selected_restaurant=result.restaurant.id
            reviews_elm.innerHTML=''
            review_modals.innerHTML=''
            addReview(reviews_elm,result.review)
            moveBox('restaurant-page','up')

            resetReviewForm()
            _putRestaurant(result.restaurant,result.review.id)
            try {
                getBottomNavChecked().checked=false
            }catch{}
            restaurant_reviews_start=0;
            restaurant_reviews_stop=20;
            // addRestaurantReviews(selected_restaurant,restaurant_reviews_start,restaurant_reviews_stop,'newest',result.review.id) // TODO add sort dropdown
            displayRestaurantMapIcons()
        }
    })
})
function getUserReviews(id=undefined) {
    if (!id) {
        id=window.user.id
    }
    fetch('/api/userreviews/'+id).then(r=>r.json()).then(reviews=>{
        window.user.reviews=reviews
    })
}
if (window.user.loggedIn) {
    getUserReviews()
}











Dropzone.autoDiscover = false;

// Dropzone configuration
var dropzone = new Dropzone(".dropzone", {
    url: "/file/post", // just a fake path
    paramName: "file",
    maxFilesize: 15, // unit is megabytes
    maxThumbnailFilesize:15,
    maxFiles: 10,
    thumbnailWidth:240,
    thumbnailHeight:240,
    acceptedFiles: 'image/*,image/heic,image/heif',
    dictDefaultMessage: "Drag files here or click to upload.",
    clickable: true,
    autoProcessQueue: false,
    addRemoveLinks: true,
    thumbnailMethod:"contain",
    dictRemoveFile: '✕',
});
(()=>{
    const onchange_dropzone = () => {
        image_upload_next.disabled = !dropzone.files.length;
    };
    // HELP! for some reason no exif exists, when it actually does
    const fileChangedHandler = (file) => {
        EXIF.getData(file, function () {
            console.log('Exif',EXIF.getAllTags(this));
        });
    };
    function convertDMSToDD(dms, ref) {
        const degrees = dms[0];
        const minutes = dms[1];
        const seconds = dms[2];
        const dd = degrees + minutes / 60 + seconds / 3600;
        return ref === "S" || ref === "W" ? -dd : dd;
    }  
    dropzone.on("addedfile", async e=>{
        onchange_dropzone()
        if (e.type=='image/heic'||e.type=='image/heif') {
            await wait(50)
            e.previewElement.querySelector('img').src='/static/media/loading.gif'
            let url = await convertHEIC(e)
            e.previewElement.querySelector('img').src=url
        }
    });
    dropzone.on("removedfile", onchange_dropzone);
})()


for (const radio of document.querySelectorAll('[name="fryType"]')) {
    radio.addEventListener('input',()=>{
        options_next.disabled=!getFryTypeElm()
    })
}
function displayRestaurantMapIcons() {
    fetch('/api/restaurants').then(response=>response.json()).then(result=>{
        remove_all_restaurant_map_icons()
        display_restaurant_buttons_on_map(result)
    })
}
displayRestaurantMapIcons()