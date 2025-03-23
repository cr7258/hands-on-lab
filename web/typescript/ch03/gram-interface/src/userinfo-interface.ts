interface IUserInfo {
    name: string;
    age?: number;
    readonly gender: boolean;
}

function funcIUserinfo(ui: IUserInfo) {
    if(ui.gender) {
        console.log(ui.name + " is a boy, " + "and he's age is " + ui.age)
    } else {
        console.log(ui.name + " is a girl, " + "and she's age is " + ui.age)
    }
}

const ui_king: IUserInfo = {
    name: "king",
    age: 26,
    gender: true
}
    
console.log("IUserInfo: king")
funcIUserinfo(ui_king)

const ui_tina: IUserInfo = {
    name: "tina",
    age: 18,
    gender: false
}
    
console.log("IUserInfo: tina")
funcIUserinfo(ui_tina)
