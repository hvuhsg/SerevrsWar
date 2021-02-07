function getPlayerColor(name){
    let tileColor = defultColor;
    if (!name){
        return tileColor;
    }
    if (name in players && players[name].color){
        tileColor = players[name].color;
    }else{
        tileColor = color(stringToColour(name));
        // r = constrain(stringToHash(name + "r00"), 80, 150);
        // g = constrain(stringToHash(name + "g000"), 80, 150);
        // b = constrain(stringToHash(name + "b00"), 80, 150);
        // tileColor = color(r, g, b);
        if (!players[name]){
            players[name] = {};
        }
        players[name].color = tileColor;
    }
    return tileColor;
}

// function stringToHash(string) {
//     return string.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0)
// } 

var stringToColour = function(str) {
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 6) - hash * 1.3);
    }
    var colour = '#';
    for (var i = 0; i < 3; i++) {
      var value = (hash >> (i * 8)) & 0xAA;
      colour += ('00' + value.toString(16)).substr(-2);
    }
    return colour;
  }