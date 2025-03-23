function getCounter() {
    var counter = function (s) {
        console.log(s);
    };
    var counter2 = function (s) {
        console.log(s);
    };
    counter.current = 0;
    counter.interval = 1;
    counter.count = function () {
        counter.current += counter.interval;
        console.log("Now current count is " + counter.current);
    };
    counter.setInterval = function (i) {
        counter.interval = i;
        console.log("Now interval change to " + counter.interval);
    };
    counter.reset = function () {
        counter.current = 0;
        console.log("Now current count reset to 0");
    };
    return counter;
}
var c = getCounter();
c("Counter TypeScript App:");
c(111);
c.count(); // 1
c.setInterval(5); // 5
c.count(); // 6
c.count(); // 11
c.reset(); // 0
c.setInterval(1); // 1
c.count(); // 1
