var websocket;
var client_id = "GUI-ID";
var token = "9e2e6311-b12a-48e2-850d-a8e0d6315eb7";
var wsHost = 'ws://' + `localhost:8000/ws?token=${token}&client_id=${client_id}`;
var apiHost = "http://localhost:8000"


function setupWebSocket(){
    websocket = new WebSocket(wsHost);
    websocket.onmessage = updateMap;
}


function loadMap(x=0, y=0, range_view=35){
    loading = true;
    let url = apiHost + '/map?' + `x=${x}&y=${y}&range_view=${range_view}&token=${token}&client_id=${client_id}`;
  httpGet(url, 'json', false, function(response) {
    map = Object.assign(map, response);
    loading = false;
    for(mapKey in response){
        var name = response[mapKey].owner;
        if(name){
            if (!players[name]){
                players[name] = {tiles: Object()};
                getPlayerColor(name);
            }
            players[name].tiles[mapKey] = response[mapKey];
        }
    }
  });
}

function loadMe(){
    let url = apiHost + '/me?' + `token=${token}`;
  httpGet(url, 'json', false, function(response) {
    me = response;
    map = Object.assign(map, response);
  });
}

function updateMap(event){
    var updatedTile = event.data;
    
    console.log(JSON.parse(updatedTile));
    var tile = JSON.parse(updatedTile);
    var tile1 = Object();
    var mapKey = `${tile.x},${tile.y}`;
    tile1[mapKey] = tile;
    map = Object.assign(map, tile1);
    var name = tile.owner;
    if(name){
        if (!players[name]){
            players[name] = {tiles: Object()};
            getPlayerColor(name);
        }
        players[name].tiles[mapKey] = tile;
    }
}