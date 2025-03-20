/**
 * Say hello function
 */

function sayHelloTo(name) {
  const toSay = `Hello, ${name}!`;
  return toSay;
}

/**
 * Say goodbye function
 */

function sayByeTo(name) {
  const toSay = `Bye, ${name}!`;
  return toSay;
}

/**
 * main entry function
 */


console.log(sayHelloTo("world"));
console.log(sayByeTo("world"));
