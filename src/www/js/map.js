let szoff = -43;
let xoff = 0, yoff = 0;
let rxoff = -960, ryoff = -404;

let dim;
let _width;
let _height;

let minShowText = 50; // From witch dim size start show text on the tiles
let defultColor;

let map = Object();
let playersMap = Object();
let me;
let players = Object();

let showPower = true;
let loading = false;


function drawBoard(){
    push();

    xoff = abs(xoff);
    yoff = abs(yoff);

    for (var i = 0; i < (width / dim)+3; i++){
        for (var j = 0; j < (height / dim)+3; j++){
            var x = ((i * dim) + xoff) % (_width + dim) - dim;
            var y = ((j * dim) + yoff) % (_height + dim) - dim;

            let x_index = round((_width - x)/dim + rxoff / dim);
            let y_index = round((_height - y)/dim + ryoff / dim);

            drawTile(x, y, x_index, y_index);
        }
    }
    pop();
}


function drawTile(x, y, x_index, y_index){
    let mapKey = `${x_index},${y_index}`;

    var name = null;
    let power = "N/A";
    let tileColor = color(169, 169, 169);

    if (mapKey in map){
        power = map[mapKey].power;
        name = map[mapKey].owner;
        tileColor = getPlayerColor(name);
    }
    else if(!loading){
        loadMap(x_index, y_index, 35);
    }
    
    fill(tileColor);
    rect(x, y, dim, dim);
    fill(color(0, 0, 0));

    if (dim >= minShowText){
        let the_text;
        if (showPower){
            the_text = power.toString();
        }else{
            the_text = `${x_index},${y_index}`
        }
        text(the_text, x + dim/2 - the_text.length*2, y + dim/2);
    }
}


function moveToCoords(){
    let params = getURLParams();
    var i = int((width / dim)+2);
    var j = int((height / dim)+2);

    if (!params.x){
        params.x = 0;
    }
    if (!params.y){
        params.y = 0;
    }

    let ix = int(params.x) + round(width / dim / 2);
    let iy = int(params.y) + round(height / dim / 2);

    var x = ((i * dim) + xoff) % (_width + dim) - dim;
    var y = ((j * dim) + yoff) % (_height + dim) - dim;
    
    rxoff = ix*dim - (_width - x);
    ryoff = iy*dim - (_height - y);
}


function doubleClicked() {
    showPower = !showPower;
    console.log(rxoff, ryoff, szoff);
    updated = 80;
}

function mouseDragged() {
    xoff += mouseX - pmouseX;
    yoff += mouseY - pmouseY;
    rxoff += mouseX - pmouseX;
    ryoff += mouseY - pmouseY;
    updated = 80;
}

function mouseWheel(event){
    szoff -= event.delta;
    szoff = constrain(szoff, -80, 60);

    dim = max(100 + szoff, 20)
    _width = width + (dim - width % dim);
    _height = height + (dim - height % dim);
    updated = 80;
}