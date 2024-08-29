function getBottomNavChecked() {
    return document.querySelector('[name="vbtn-radio"]:checked')
}
const fryTypes = window.fryTypes
const rating_slider=document.querySelector('#rating')
const rating_text=document.querySelector('#rating-text')
const rating_value=document.querySelector('#rating-value')

const image_upload_next=document.querySelector('#next-btn-rev-1-1')
const options_next=document.querySelector('#next-btn-rev-2-1')

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

const restaurant_input=document.querySelector('#restaurant-search')
function getFryTypeElm() {
    return document.querySelector('[name="fryType"]:checked')
}

let restaurant = 'ChIJN1t_tDeuEmsRUsoyG83frY4'

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
function addReview(parent,review,reviewer) {
    parent.innerHTML+=`<div class="review" id="review-${review.id}">
                <section class="top-review">
                    <div class="reviewer-name">${reviewer}</div>
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
// document.createElement('input').addEventListener('toggle')
search_page_select.addEventListener('click',()=>{
    moveBox("search-page",'left')
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
        restaurant:restaurant,
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
function _putRestaurant(data) {
    restaurant_thumbnail.src=data.thumbnail
    restaurant_name.innerText=data.name
    restaurant_address.innerText=data.address

    restaurant_rating.innerHTML=''
    ratingStars(restaurant_rating,data.rating)
    restaurant_rating.innerHTML+=`<span>(${data.reviews} review${data.reviews==1?'':'s'})</span>`
}
function resetReviewForm() {
    dropzone.removeAllFiles()
    rating_slider.value=3
    getFryTypeElm().checked=false
    is_fresh_box.checked=false
    is_spiced_box.checked=false
    has_toppings_box.checked=false
    restaurant=''
    document.querySelector('.selected-restaurant').innerHTML=
    `   <div class="restaurant-info d-flex flex-column">
            <input id="restaurant" readonly value="No Restaurant Selected" class="border-0 outline">
            <div id="restaurant-address-review" class="restaurant-address">Fry Rd, Pennsylvania, USA</div>
        </div>
        <div class="restaurant-image d-flex align-items-center justify-content-center bg-secondary rounded-1">
            <i class="bi bi-shop"></i>
            <img src="" alt="" id="restaurant-image">
        </div>
    `
    comment_box.value=''
    restaurant_input.value=''
}
review_submit_btn.addEventListener('click',e=>{                         if(!e.isTrusted)return;
    const values=getReviewValues()

    if (values.rating<1||values.rating>5) { // checks
        invalidFormInput('review-2-1',rating_slider,'Invalid Input!',"Rating not between 1 and 5",'left','bottom')
        return
    }
    if (values.files.length<1) {
        invalidFormInput('review-1-1',document.querySelector('.dropzone'),'Invalid Input!',"A file must be uploaded",'left','bottom')
        return
    }
    if (!fryTypes.includes(values.fry_type)) {
        invalidFormInput('review-2-1',getFryTypeElm(),'Invalid Input!',`Invalid Fry Type "${values.fry_type}"`,'left','right')
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
            invalidFormElm(review_submit_btn,'Invalid Input!',result.error)
        }
        if (result.status=='ok') {
            const reviews_elm=document.querySelector('#restaurant-page .reviews')
            reviews_elm.innerHTML=''
            review_modals.innerHTML=''
            addReview(reviews_elm,result.review,result.user.name)
            moveBox('restaurant-page','up')

            resetReviewForm()
            _putRestaurant(result.restaurant)
            try {
                getBottomNavChecked().checked=false
            }catch{}
        }
    })
})













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
    acceptedFiles: 'image/*',
    dictDefaultMessage: "Drag files here or click to upload.",
    clickable: true,
    autoProcessQueue: false,
    addRemoveLinks: true,
    thumbnailMethod:"contain",
    dictRemoveFile: '✕',
});
const onchange_dropzone=()=>{
    image_upload_next.disabled=!dropzone.files.length
}
dropzone.on("addedfile",onchange_dropzone)
dropzone.on("removedfile",onchange_dropzone)

for (const radio of document.querySelectorAll('[name="fryType"]')) {
    radio.addEventListener('input',()=>{
        options_next.disabled=!getFryTypeElm()
    })
}