function preload() {
    loadMap(0, 0, 35);
}

function setup() {
    let params = getURLParams();
    createCanvas(windowWidth - 15, windowHeight - 15);
    setupWebSocket();
    defultColor = color(169, 169, 169);
    dim = Math.max(100 + szoff, 20);
    _width = width + (dim - width % dim);
    _height = height + (dim - height % dim);
    token = params.token;
    moveToCoords();
}

function draw() {
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