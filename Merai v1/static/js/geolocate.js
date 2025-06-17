function detectLocation(){
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(function(pos){
      document.getElementById('lat').value = pos.coords.latitude.toFixed(6);
      document.getElementById('lon').value = pos.coords.longitude.toFixed(6);
      var form = document.querySelector('form');
      if (form) form.submit();
    });
  } else {
    alert('Geolocation not supported');
  }
}