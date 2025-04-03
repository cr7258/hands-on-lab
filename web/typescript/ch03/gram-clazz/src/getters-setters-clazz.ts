class CGetSet {
    private _name: string;
    constructor(theName: string) {
        this._name = theName.trim();
    }
    // 通过 get 修饰符定义了属性 _name 存取器的方法 get()
    get name(): string {
        return this._name;
    }
    set name(theName: string) {
        theName = theName.trim();
        if (theName && theName.length > 0) {
            this._name = theName;
        } else {
            console.log("Err - string is empty");
        }
    }
}

let gs = new CGetSet(" Get&Set");
console.log(gs.name);
gs.name = " reset Get&Set";
console.log(gs.name);
