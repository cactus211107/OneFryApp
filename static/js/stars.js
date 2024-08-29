function displayStars(parent,filledStars,totalStars,fillColor,backgroundColor) {
    for (let i = 0; i < totalStars; i++) {
        let r=Math.random().toString().replace('.','69')
        let percent_filled=Math.min(filledStars,1)*100
        parent.innerHTML+=`
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="256px" height="256px" viewBox="0 0 32 32" class="star">
            <defs>
            <linearGradient id="grad${i+r}">
                <stop offset="${percent_filled}%" stop-color="${fillColor}"></stop>
                <stop offset="${percent_filled}%" stop-color="${backgroundColor}"></stop>
                <stop offset="${100-percent_filled}%" stop-color="${backgroundColor}"></stop>
            </linearGradient>
            </defs>
            <path fill="url(#grad${i+r})" d="M20.388,10.918L32,12.118l-8.735,7.749L25.914,31.4l-9.893-6.088L6.127,31.4l2.695-11.533L0,12.118
        l11.547-1.2L16.026,0.6L20.388,10.918z"></path>
        </svg>
        `
        filledStars-=1
    }
}
function ratingStars(parent,stars) {
    displayStars(parent,stars,5,'#ffce00','#ababab')
}