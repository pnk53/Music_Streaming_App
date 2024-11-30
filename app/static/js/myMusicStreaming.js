let progress = document.getElementById("progress")
let song = document.getElementById("song")

song.onloadedmetadata = function(){
    progress.max = song.duration;
    progress.value = song.currentTime;
}

function play(){
    song.play();
    document.getElementById("controlIcon1").style.backgroundColor='#fff';
    document.getElementById("playButton").setAttribute('fill','#302b63');
    document.getElementById("controlIcon2").style.backgroundColor='#302b63';
    document.getElementById("pauseButton").setAttribute('fill','#fff');
}
function pause(){
    song.pause();
    document.getElementById("controlIcon2").style.backgroundColor='#fff';
    document.getElementById("pauseButton").setAttribute('fill','#302b63');
    document.getElementById("controlIcon1").style.backgroundColor='#302b63';
    document.getElementById("playButton").setAttribute('fill','#fff');
}

if(song.play()){
    setInterval(()=>{
        progress.value = song.currentTime;
    },1000)
}
progress.onchange = function(){
    song.currentTime = progress.value
    play();
}