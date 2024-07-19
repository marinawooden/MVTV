"use strict";

(function() {
  const INFO_TIMEOUT = 5000;
  const LANDING_STYLES = ["noise", "checker"];

  let isPlaying = true;
  let timerId;
  let hasInteracted; // has interacted with the page yet?

  window.addEventListener("load", init);

  function init() {
    const videoPlayer = document.getElementById('video-player');
    const videoInfo = document.getElementById('video-info');
    const videoHolder = document.getElementById('player-holder');
    const enterButton = document.getElementById('logo-main');
    let landingDrop = document.getElementById("landing-drop");

    landingDrop.classList.add(LANDING_STYLES[Math.floor(Math.random() * LANDING_STYLES.length)]);


    const socket = io();
    socket.on('video_info', startVideo);

    enterButton.addEventListener('click', (e) => {
      document.getElementById("landing-drop").classList.add('hidden');
      videoPlayer.play();
      hasInteracted = true;
      e.stopPropagation();
    });

    videoPlayer.addEventListener('ended', () => {
      videoInfo.querySelector(".meta").innerHTML = "";
      socket.emit('video_ended');
    });

    videoHolder.addEventListener('mousemove', function() {
      this.classList.add("active");

      if (timerId) {
        clearTimeout(timerId);
      }

      timerId = setTimeout(() => {
        this.classList.remove("active");
      }, INFO_TIMEOUT);
    });

    videoHolder.addEventListener('mouseleave', function() {
      this.classList.remove("active");
      if (timerId) {
        clearTimeout(timerId);
      }
    });

    videoInfo.addEventListener('click', () => {
      console.log(isPlaying);
      isPlaying ? videoPlayer.pause() : videoPlayer.play();
      videoInfo.classList.toggle("paused");
      isPlaying = !isPlaying;
    });
  }

  function startVideo(data) {
    const videoSource = document.getElementById('video-source');
    const videoPlayer = document.getElementById('video-player');
    
    populateVideoPlayer(data);
    videoSource.src = `/video_feed?start=0`;
    videoPlayer.load();

    hasInteracted && videoPlayer.play();
  }

  function populateVideoPlayer(data) {
    const videoInfo = document.querySelector('#video-info .meta');
    let titleText = document.createElement("h1");
    let artistText = document.createElement("p");
    let yearText = document.createElement("p");
    let labelText = document.createElement("p");

    videoInfo.innerHTML = "";

    titleText.textContent = `"${data.title}"`;
    artistText.textContent = data.artist;
    labelText.textContent = data.label;
    yearText.textContent = data.year;


    videoInfo.append(artistText, titleText, labelText, yearText);
  }
})();