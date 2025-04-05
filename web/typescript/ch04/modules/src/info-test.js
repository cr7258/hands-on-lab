"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// 不使用花括号导入默认导出（default export）的类
// name-module.ts 中使用 "export default class InfoNameValidator" 导出的类
var name_module_1 = require("./name-module");
var age_module_1 = require("./age-module");
var gender_module_1 = require("./gender-module");
var strTest = ["king", "king_88", "he", "hello_typescript", "26", "123", "male"];
var validators = {};
validators["name"] = new name_module_1.default();
validators["age"] = new age_module_1.default();
validators["gender"] = new gender_module_1.default();
strTest.forEach(function (s) {
    for (var info in validators) {
        console.log("\"".concat(s, "\" - ").concat(validators[info].isInfoValid(s) ? "matches" : "does not match", " ").concat(info));
    }
});
