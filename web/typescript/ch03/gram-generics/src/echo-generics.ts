function echo<T>(arg: T): T {
    return arg;
}

console.log("echo<number>(): " + echo<number>(123));
console.log("echo<string>(): " + echo<string>("hello"));
console.log("echo(): " + echo(123));
console.log("echo(): " + echo("hello"));
