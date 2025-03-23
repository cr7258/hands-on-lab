interface IGirth {
    girth: number;
}

interface IArea {
    area: number;
}

interface IShapeB extends IGirth, IArea {
    shapeType: string;
    getGirth(): number;
    getArea(): number;
}

class CSquareB implements IShapeB {
    shapeType: string;
    girth: number;
    area: number;
    constructor(sideLength: number) {
        this.shapeType = "Square";
        this.girth = 4 * sideLength;
        this.area = sideLength * sideLength;
    }
    getGirth(): number {
        return this.girth;
    }
    getArea(): number {
        return this.area;
    }
}

let csB: CSquareB = new CSquareB(6);
console.log(csB.shapeType + " sideLenght is 6, girth is " + csB.getGirth() + ", area is " + csB.getArea());
