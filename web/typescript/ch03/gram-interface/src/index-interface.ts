interface INumIndexArray {
    [index: number]: string;
}

let myNumArr: INumIndexArray;
myNumArr = ["king", "tina", "cici"];
for(let i in myNumArr) {
    console.log(myNumArr[i]);
}

interface IStrNumIndexArray {
    [index: string]: string|number;
}

let myStrNumArr: IStrNumIndexArray;
myStrNumArr = {"width": "32px", "height": "32px", "length": 8};

console.log("Image Szie:");
console.log("width is : " + myStrNumArr["width"]);
console.log("height is : " + myStrNumArr["height"]);
console.log("length is : " + myStrNumArr["length"]);
