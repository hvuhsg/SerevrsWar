function drawScoreBoard(){
    push();
    colorMode(RGB, 255);
    rectMode(CORNER);
    var squareColor = color(128, 128, 128);
    squareColor.setAlpha(128 + 128 * sin(0.3));
    fill(squareColor);
    rect(width - 210, 10, 200, 300);

    var counter = 0;
    textSize(20);

    var nplayers = Array();

    for (const [name, player] of Object.entries(players)) {
        nplayers.push({"score": 0, "name": name});
        for (const [mapKey, tile] of Object.entries(player.tiles)){
            nplayers[nplayers.length-1].score += CalculateTilePower(mapKey);
        }
    }

    nplayers.sort(compare);
    nplayers.reverse();

    for (player in nplayers){
        player = nplayers[player];    
        fill(players[player.name].color);
        text(counter + ".   " + player.name + ` ${player.score}`, width - 190, 50+counter*40);
        counter += 1;
    }
    textSize(12);
    fill(0);
    pop();
}


function compare( player_a, player_b ) {
    if ( player_a.score < player_b.score ){
      return -1;
    }
    if ( player_a.score > player_b.score ){
      return 1;
    }
    return 0;
  }