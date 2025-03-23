var funcArithmetic;
funcArithmetic = function (x, y, s) {
    var r;
    switch (s) {
        case "add":
            r = x + y;
            break;
        case "minus":
            r = x - y;
            break;
        case "multiply":
            r = x * y;
            break;
        case "divide":
            r = x / y;
            break;
        default:
            r = 0;
            break;
    }
    return r;
};
console.log("6 + 3 = " + funcArithmetic(6, 3, "add"));
console.log("6 - 3 = " + funcArithmetic(6, 3, "minus"));
console.log("6 * 3 = " + funcArithmetic(6, 3, "multiply"));
console.log("6 / 3 = " + funcArithmetic(6, 3, "divide"));
