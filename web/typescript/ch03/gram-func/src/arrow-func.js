var userinfo = {
    uname: "king",
    printInfo: function () {
        var _this = this;
        return function () {
            return { name: _this.uname };
        };
    }
};
var ui = userinfo.printInfo();
console.log("User name is " + ui().name);
