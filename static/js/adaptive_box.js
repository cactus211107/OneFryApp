(()=>{
    window._abhistory=[]
    const container = document.querySelector('.adaptive-box-container')
    const moving_container = document.querySelector('.adaptive-boxes')
    const elm_boxes = []
    const boxes = [];
    let current_box = 'home'
    function _add_box_vars() {
        for (const e of elm_boxes) { // clears them
            elm_boxes.pop()
            boxes.pop()
        }
        for (const box of document.querySelectorAll('.adaptive-box')) {
            elm_boxes.push(box)
            boxes.push(box.id)
        }
    }
    function get_box_bounds() {
        return document.querySelector('.adaptive-box:not(.hidden)').getBoundingClientRect()
    }
    function insertBefore(elm,elm2) { // inserts elm2 before elm1
        elm.parentNode.insertBefore(elm,elm2)
    }
    function getBox(name) {
        return document.querySelector('#'+name)
    }
    async function _change_box(box_name,dir) {
        if(box_name==current_box){return}
        const box = getBox(box_name)
        const cur_box=getBox(current_box)
        const isUp=dir === 'up'
        const isDown=dir === 'down'
        const isLeft=dir === 'left'
        const isRight=dir === 'right'

        dir=dir.toLowerCase()
        if(!(isUp || isDown || isLeft || isRight)){throw new Error("Adaptive-Box: Invalid Adaptive-Box Direction")}
        if(!box){throw new Error("Adaptive-Box: Box does not exist")}

        window._abhistory.push({direction:dir,box_name:box_name})
        let transform=`translate(0px,${isUp?-get_box_bounds().height:0}px)`

        let scrollHeight1=box.scrollHeight
        let scrollHeight2=cur_box.scrollHeight

        moving_container.classList.add('no-trans')
        moving_container.style.transform=transform
        insertBefore(getBox(current_box),box)
        insertBefore(box,getBox(current_box))

        for (const e of elm_boxes) {
            if (e.id!=current_box && e.id!=box_name) {
                e.classList.add('hidden')
            } else {
                e.classList.remove('hidden')
            }
        }
        insertBefore(getBox(current_box),box) 
        moving_container.style.transform=transform
        let key = {
            right:'row',
            down:'column',
            left:'row-reverse',
            up:'column-reverse'
        }

        moving_container.style.flexDirection=key[dir]
        box.scroll(0,scrollHeight1)
        cur_box.scroll(0,scrollHeight2)
        await wait(100) //
        moving_container.classList.remove('no-trans')


        trans(isRight+isLeft*-1,isDown+isUp*0)
        
        current_box=box_name
    }

    function _trans(x,y) {
        moving_container.style.setProperty('transform',`translate(${x}px,${y}px)`)
    }
    function trans(multx,multy) {
        _trans(get_box_bounds().width*-multx,get_box_bounds().height*-multy)
    }
    document.addEventListener("adaptiveBoxMove", function (e) {
        _change_box(e.detail.name,e.detail.dir)
      });
      _add_box_vars()
})()
function moveBox(box_name,direction='right') {
    let e=new CustomEvent("adaptiveBoxMove", {
        detail: {
          name: box_name,
          dir: direction,
        },
      });
    document.dispatchEvent(e)
}
function getCheckedFooter() {
    return document.querySelector('[name="vbtn-radio"]:checked')   
}
function refreshAdaptiveButtons() {
    for (const b of document.querySelectorAll('input[data-ab-name],button[data-ab-name]')) {
        b.addEventListener(b.tagName=='INPUT'?'input':'click',()=>{
            moveBox(b.getAttribute('data-ab-name'),b.getAttribute('data-ab-dir')||'right')
        })
    }
}
refreshAdaptiveButtons()