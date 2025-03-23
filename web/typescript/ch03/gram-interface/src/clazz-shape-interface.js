var CSquare = /** @class */ (function () {
    function CSquare(sideLength) {
        this.girth = sideLength * 4;
        this.shapeType = "Square";
    }
    CSquare.prototype.getGirth = function () {
        return this.girth;
    };
    return CSquare;
}());
var cs = new CSquare(6);
console.log(cs.shapeType + " sideLenght is 6, girth is " + cs.getGirth());
