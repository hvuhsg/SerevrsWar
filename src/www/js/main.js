let token;
let updated = 400;
let time = Date.now();

function preload() {
    let params = getURLParams();
    token = params.token;
    loadMe();
    loadMap(0, 0, 35);
}

function setup() {
    createCanvas(windowWidth - 15, windowHeight - 15);
    setupWebSocket();
    defultColor = color(169, 169, 169);
    dim = Math.max(100 + szoff, 20);
    _width = width + (dim - width % dim);
    _height = height + (dim - height % dim);
    moveToCoords();
}

function draw() {
    if ((Date.now() - time) / 1000 >= me["game"]["power_growth_rate"]){
        time = Date.now();
        updated += 10;
    }
    if (!updated){
        return
    }
    updated -= 1;
    background(255);
    drawBoard();
    drawScoreBoard();
    showFrameRate();
}

function showFrameRate() {
    push();
    let fps = frameRate();
    fill(255);
    stroke(0);
    text("FPS: " + fps.toFixed(0), 10, height - 10);
    pop();
}