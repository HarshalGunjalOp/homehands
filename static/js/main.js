function checkResolution() {
  const screenWidth = window.screen.width;
  const viewportWidth = window.innerWidth;

  // Check if the screen width or viewport width is 1920px or greater
  if (screenWidth >= 1920 && viewportWidth >= 1920) {
      document.getElementById('content').style.display = 'block';
      document.getElementById('custom-message').style.display = 'none';
  } else {
      document.getElementById('content').style.display = 'none';
      document.getElementById('custom-message').style.display = 'block';
  }
}
window.onload = checkResolution;
window.onresize = checkResolution;



setTimeout(function() {
  var flashes = document.querySelectorAll('.flashes li');
  flashes.forEach(function(flash) {
    flash.style.opacity = '0';  
    setTimeout(function() {
      flash.style.display = 'none';  
    }, 500);  
  });
}, 5000);  