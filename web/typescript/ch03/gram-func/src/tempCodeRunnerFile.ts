let userinfo = {
    uname: "king",
    printInfo: function () {
        return () => {
            return { name: this.uname }
        }
    }
}

let ui = userinfo.printInfo()
console.log("User name is " + ui().name)
