interface ICounter {
    // function interface
    (s: string): void;
    // property interface
    current: number;
    interval: number;
    // class interface
    count(): void;
    setInterval(i: number): void;
    reset(): void;
}

function getCounter(): ICounter {
    // <ICounter> 是对紧随其后的匿名函数进行类型断言。它告诉编译器，该函数应该被视为符合 ICounter 接口的对象。
    let counter = <ICounter>function (s: string): void {
        console.log(s);
    };
    counter.current = 0;
    counter.interval = 1;
    counter.count = function (): void {
        counter.current += counter.interval;
        console.log("Now current count is " + counter.current);
    };
    counter.setInterval = function (i: number): void {
        counter.interval = i;
        console.log("Now interval change to " + counter.interval);
    };
    counter.reset = function (): void {
        counter.current = 0;
        console.log("Now current count reset to 0");
    };
    return counter;
}

let c = getCounter();
c("Counter TypeScript App:")
c.count(); // 1
c.setInterval(5); // 5
c.count(); // 6
c.count(); // 11
c.reset(); // 0
c.setInterval(1); // 1
c.count(); // 1
