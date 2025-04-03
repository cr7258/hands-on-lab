function funcUser (
    firstName: string = "king",
    lastName?: string,
    ...restInfo: string[]){
        return "User Info: " + firstName + " " + lastName + " " + restInfo.join(" ");
}

console.log(funcUser());
console.log(funcUser("Tina", "Wang"));
console.log(funcUser(undefined, undefined, "male", "26"));
// User Info: king undefined 
// User Info: Tina Wang 
// User Info: king undefined male 26