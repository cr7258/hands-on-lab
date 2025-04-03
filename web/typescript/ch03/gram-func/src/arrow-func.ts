let userinfo = {
    uname: "king",
    printInfo: function () {
        // 箭头函数会继承其定义时的上下文 this，而不是调用时的上下文。
        // 在这个例子中，this 指向的是 userinfo 对象，所以 this.uname 的值是 king
        return () => {
            return { name: this.uname }
        }
    }
}

let ui = userinfo.printInfo()
console.log("User name is " + ui().name)
