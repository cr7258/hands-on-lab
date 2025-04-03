function funcUser(firstName, lastName) {
    if (firstName === void 0) { firstName = "king"; }
    var restInfo = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        restInfo[_i - 2] = arguments[_i];
    }
    return "User Info: " + firstName + " " + lastName + " " + restInfo.join(" ");
}
console.log(funcUser());
console.log(funcUser("Tina", "Wang"));
console.log(funcUser(undefined, undefined, "male", "26"));
