function weather() {
  var location = document.getElementById("location");
  var apiKey = "dd5fe22c28edf8897ed7c467bac6bd92";
  var url = "https://api.forecast.io/forecast/";
   latitude = 40.862041;
   longitude = -73.885696

  navigator.geolocation.getCurrentPosition(success, error);

  function success(position) {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;

    location.innerHTML =
      "Latitude is " + latitude + "° Longitude is " + longitude + "°";

    $.getJSON(
      url + apiKey + "/" + latitude + "," + longitude + "?callback=?",
      function(data) {
        $("#temp").html(data.currently.temperature + "° F");
        $("#minutely").html(data.minutely.summary);
      }
    );
  }

  function error() {
    location.innerHTML = "GPS Signal Not Found --- Weather of Fordham University is presented";

    $.getJSON(
      url + apiKey + "/" + latitude + "," + longitude + "?callback=?",
      function(data) {
        $("#temp").html(data.currently.temperature + "° F");
        $("#minutely").html(data.minutely.summary);
      }
    );
  }

  location.innerHTML = "Locating...";
}

weather();
