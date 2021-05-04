document.addEventListener('DOMContentLoaded', function(){
    var player = document.querySelector('#player');

    play = document.querySelectorAll('.play');

    play.forEach(
        function(button){

            var content = button.dataset.seconds;
            var times = content.split(" ");
            var start = times[0]
            var end = times[1]                   

            button.addEventListener('click', playVideo, !1)

            // template from https://stackoverflow.com/questions/47643091/html5-video-start-video-at-certain-time-and-play-for-x-amount-of-time
            
            function playVideo(e) {

                function checkTime() {
                    if (player.currentTime >= end) {
                    player.pause();

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
});