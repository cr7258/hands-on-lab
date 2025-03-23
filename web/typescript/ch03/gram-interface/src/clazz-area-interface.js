var CSquareB = /** @class */ (function () {
    function CSquareB(sideLength) {
        this.shapeType = "Square";
        this.girth = 4 * sideLength;
        this.area = sideLength * sideLength;
    }
    CSquareB.prototype.getGirth = function () {
        return this.girth;
    };
    CSquareB.prototype.getArea = function () {
        return this.area;
    };
    return CSquareB;
}());
var csB = new CSquareB(6);
console.log(csB.shapeType + " sideLenght is 6, girth is " + csB.getGirth() + ", area is " + csB.getArea());
