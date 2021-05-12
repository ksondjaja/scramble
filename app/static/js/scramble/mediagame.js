if (window.safari) {
    history.pushState(null, null, location.href);
    window.onpopstate = function(event) {
        history.go(1);
    };
}

document.addEventListener('DOMContentLoaded', function(){

    var player = document.querySelector('#player');
    var playerarea = document.querySelector('.player');

    var playmedia = document.querySelectorAll('#play');

    var playall = document.querySelector('#playall');

    var totalsec = 0;
    var seconds = 0;
    var minutes = 0;
    // var isplaying = false;

    function timer(){
        totalsec++
        seconds++
        if(seconds==60){
            minutes++
            seconds=0;
        }
        document.querySelector('#time').innerHTML = `Elapsed ${("0" + minutes).slice(-2)}:${("0" + seconds).slice(-2)}`;
    }

    var time = setInterval(timer, 1000)
    var timebttn = true;

    document.querySelector('#displaytimer').onclick = function(){
        if(timebttn==true){
            timebttn = false;
            document.querySelector('#time').style.display = 'none';
            document.querySelector('#displaytimer').innerHTML = 'Show Timer';
        }else{
            timebttn = true;
            document.querySelector('#time').style.display = 'inline-block';
            document.querySelector('#displaytimer').innerHTML = 'Hide Timer';
        }
    }

    dropboxes = document.querySelectorAll('.dropbox');

    cards = document.querySelectorAll('.card');
    n = cards.length;

    var cheights = [];
    var cwidths = [];

    for(var i=0; i<n; i++){
        cheights.push(parseInt(cards[i].clientHeight));
        cwidths.push(parseInt(cards[i].clientWidth));
    }

    const cheight = Math.max.apply(Math, cheights);
    const cwidth = Math.max.apply(Math, cwidths);

    for(var i=0; i<n; i++){
        cards[i].style.height = cheight + 'px';
        cards[i].style.width = cwidth + 'px';
        dropboxes[i].style.height = cheight + 20 +'px';
        dropboxes[i].style.width = cwidth + 20 +'px';
    }

    var fill = [];
    var correct = [];

    var title = document.querySelector('.title').getBoundingClientRect();

    playerarea.style.top = 50 + parseInt(title.bottom) + 'px' ;

    var playerpos = playerarea.getBoundingClientRect();
    
    document.querySelector('.head').style.height = parseInt(title.bottom) + 'px';

    var col = window.innerWidth/2;
    var div = 5;

    if (parseInt(dropboxes[0].style.width) > (col/div)){
        div = Math.floor(col/parseInt(dropboxes[0].style.width));
        if(div == 0){
            div = 1;
        }
    }

    for(var i=0; i<n; i++){
        dropboxes[i].style.left = (cwidth+23)*(i%div) + col + 'px';
        dropboxes[i].style.top = (cheight+23)*Math.floor(i/div) + 50 + parseInt(playerpos.bottom) + 'px' ;
        cards[i].style.left = (cwidth+20)*(i%div) + 20 + 'px';
        fill.push(99);
        correct.push(i);
    }

    lastbox = dropboxes[n-1].getBoundingClientRect();

    for(var i=0; i<n; i++){
        cards[i].style.top = (cheight+20)*Math.floor(i/div) + 50 + parseInt(playerpos.bottom) + 'px';
    }


    playmedia.forEach(
        function(button){

            var content = button.dataset.seconds;
            var times = content.split(" ");
            var start = times[0]
            var end = times[1]
            // var isplaying = true;                   

            button.addEventListener('mouseenter', function(event){
                event.stopPropagation();
            })

            button.addEventListener('click', playVideo, !1)

            // template from https://stackoverflow.com/questions/47643091/html5-video-start-video-at-certain-time-and-play-for-x-amount-of-time
            
            function playVideo(event) {

                event.stopPropagation()

                button.style.background = 'rebeccapurple';

                function checkTime() {
                    if (player.currentTime >= end) {
                    player.pause();

                    button.style.background = 'mediumpurple';

                    // var isplaying = false;

                    } else {
                    /* call checkTime every 1/10th 
                        second until endTime */
                    setTimeout(checkTime, 1);
                    }
                }

                player.currentTime = start;
                player.play();
                checkTime();
                
            }
            
        }
    )

    
    
    cards.forEach(
        function(card){

            var dragItem = card;

            var active = false;
            var currentX;
            var currentY;
            var initialX;
            var initialY;
            var xOffset = 0;
            var yOffset = 0;

            var bin = null;
            var currbox = null;
            var cardi
            var ind

            // template from https://www.kirupa.com/html5/drag.htm

            document.addEventListener("touchstart", dragStart, false);
            document.addEventListener("touchend", dragEnd, false);
            document.addEventListener("touchmove", drag, false);

            document.addEventListener("mousedown", dragStart, false);
            document.addEventListener("mouseup", dragEnd, false);
            document.addEventListener("mousemove", drag, false);

            function dragStart(event) {

                if (event.type === "touchstart") {
                initialX = event.touches[0].clientX - xOffset;
                initialY = event.touches[0].clientY - yOffset;
                } else {
                initialX = event.clientX - xOffset;
                initialY = event.clientY - yOffset;
                }

                if (event.target === dragItem) {
                    active = true;

                    bin = null;
                    currbox = null;
                    cardi = parseInt(card.dataset.cindex);

                    dragItem.style.background='rebeccapurple';
                    document.body.append(dragItem);

                    if(fill.includes(cardi)){
                        ind = fill.indexOf(cardi);
                        fill[ind] = 99;
                        document.querySelector(`[data-bindex="${ind}"]`).style.background = "";
                    }

                }
            }

            

            function drag(event) {
                if (active) {
                
                // event.preventDefault();

                var choriz;
                var cvert;
                
                if (event.type === "touchmove") {
                    currentX = event.touches[0].clientX - initialX;
                    currentY = event.touches[0].clientY - initialY;

                    choriz = parseInt(event.touches[0].clientX);
                    cvert = parseInt(event.touches[0].clientY);
                } else {
                    currentX = event.clientX - initialX;
                    currentY = event.clientY - initialY;

                    choriz = parseInt(event.clientX);
                    cvert = parseInt(event.clientY);
                }

                xOffset = currentX;
                yOffset = currentY;

                setTranslate(currentX, currentY, dragItem);

                // console.log(choriz, cvert);

                dropboxes.forEach(function(box){

                    var boxxy = box.getBoundingClientRect();
                    // console.log(boxxy.left, boxxy.right, boxxy.top, boxxy.bottom);
                
                    if(boxxy.left < choriz && boxxy.right > choriz && boxxy.top < cvert && boxxy.bottom > cvert){
                        if(active===true){
                            if(box.style.background!="lightseagreen"){
                                box.style.background = "grey";
                                currbox = box;
                                bin = currbox;
                                // console.log('in')
                            }
                        }
                    }else{
                        if(box.style.background!="lightseagreen"){
                            box.style.background = "";
                            // console.log('out')
                        }
                    }
                    
                })

                }
            }

            function dragEnd(event) {
                initialX = currentX;
                initialY = currentY;

                active = false;

                card.style.background = 'mediumpurple';

                if(currbox!=null && currbox.style.background==="grey"){
                    if(bin==currbox){
                        currbox.style.background = "lightseagreen";
                        fill[currbox.dataset.bindex] = cardi;
                        // document.querySelector('.order').innerHTML = fill;
                        if(JSON.stringify(fill)===JSON.stringify(correct)){
                            document.querySelector('.check').innerHTML = "Success!";
                            clearInterval(time)
                            if(document.querySelector('#nextbutton').style.display=='none'){
                                // document.querySelector('#nextbutton').style.display='block';
                                document.querySelector('#submittimebutton').innerHTML = `<button id="timebutton" name="time" value=${totalsec}>Submit Time</button>`;
                                setTimeout(function(){
                                    document.querySelector('#timebutton').click();
                                },100)
                            }
                            // alert("Congratulations, you've won!");
                        }
                    }
                }

            }

            function setTranslate(xPos, yPos, el) {
                el.style.transform = "translate3d(" + xPos + "px, " + yPos + "px, 0)";
            }

            card.ondragstart = function(){
                return false;
            }
        }
    )

    // playall.addEventListener('click', function(){
    //     for(let i=0; i<n; i++){
    //         number = fill[i];
    //         if(number !== 99){
    //             console.log(number);
    //             console.log(isplaying);
    //             currcard = document.querySelector(`[data-cindex="${number}"]`);
    //             currbutton = currcard.querySelector('#play');

    //             currbutton.click();
    //             while(isplaying == true){
    //                 console.log(isplaying);
    //             }
    //             setTimeout(1000);
    //         }
    //     }
    // })
    //     async function processArray(fill){
    //         fill.forEach(number =>{
    //             if(number !== 99){
    //                 console.log(number);
    //                 currcard = document.querySelector(`[data-cindex="${number}"]`);
    //                 currbutton = currcard.querySelector('#play');
    //             }
    //             await currbutton.click();
    //         })
    //     }
    // })
        // for(let i=0; i<n; i++){
        //     // (function(){
        //         number = fill[i];
        //         if(number !== 99){
        //             console.log(number);
        //             currcard = document.querySelector(`[data-cindex="${number}"]`);
        //             currbutton = currcard.querySelector('#play');

        //             if((i+1)<n && fill[i+1] !== 99){
        //                 console.log(fill[i+1]);
        //                 nextcard = document.querySelector(`[data-cindex="${fill[i+1]}"]`);
        //                 nextbutton = nextcard.querySelector('#play');
        //                 secs = nextbutton.dataset.seconds.split(" ");
        //                 waittime = parseInt((parseFloat(secs[1]) - parseFloat(secs[0]))*1000);
        //             }else{
        //                 waittime = 0;
        //             }

        //             setTimeout(currbutton.click(), waittime);
        //             console.log(waittime);
        //         }
        //     // })(i);
        // }
    // })
    

});