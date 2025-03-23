interface IShape {
    girth: number;
}

interface ISquare extends IShape {
    shapeType: string;
    getGirth(): number;
}

class CSquare implements ISquare {
    shapeType: string;
    girth: number;
    constructor(sideLength: number) {
        this.girth = sideLength * 4;
        this.shapeType = "Square";
    }
    getGirth(): number {
        return this.girth;
    }
}

let cs: CSquare = new CSquare(6);
console.log(cs.shapeType + " sideLenght is 6, girth is " + cs.getGirth());
