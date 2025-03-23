function funcIUserinfo(ui) {
    if (ui.gender) {
        console.log(ui.name + " is a boy, " + "and he's age is " + ui.age);
    }
    else {
        console.log(ui.name + " is a girl, " + "and she's age is " + ui.age);
    }
}
var ui_king = {
    name: "king",
    age: 26,
    gender: true
};
console.log("IUserInfo: king");
funcIUserinfo(ui_king);
var ui_tina = {
    name: "tina",
    age: 18,
    gender: false
};
console.log("IUserInfo: tina");
funcIUserinfo(ui_tina);
