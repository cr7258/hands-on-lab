var CGetSet = /** @class */ (function () {
    function CGetSet(theName) {
        this._name = theName.trim();
    }
    Object.defineProperty(CGetSet.prototype, "name", {
        // 通过 get 修饰符定义了属性 _name 存取器的方法 get()
        get: function () {
            return this._name;
        },
        set: function (theName) {
            theName = theName.trim();
            if (theName && theName.length > 0) {
                this._name = theName;
            }
            else {
                console.log("Err - string is empty");
            }
        },
        enumerable: false,
        configurable: true
    });
    return CGetSet;
}());
var gs = new CGetSet(" Get&Set");
console.log(gs.name);
gs.name = " reset Get&Set";
console.log(gs.name);
