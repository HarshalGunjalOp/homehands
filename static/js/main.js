  // Function to fade out flash messages after 10 seconds
  setTimeout(function() {
    var flashes = document.querySelectorAll('.flashes li');
    flashes.forEach(function(flash) {
      flash.style.opacity = '0';  // Start fading out
      setTimeout(function() {
        flash.style.display = 'none';  // Remove from display after fade out
      }, 500);  // Delay for fade-out effect (adjust as needed)
    });
  }, 5000);  // 10 seconds before fade out starts
