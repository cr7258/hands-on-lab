// 使用花括号 {} 导入具名导出（named export）的接口
// info-module.ts 中使用 "export interface IInfoValidation" 导出的接口
import { IInfoValidation } from "./info-module";

// 不使用花括号导入默认导出（default export）的类
// name-module.ts 中使用 "export default class InfoNameValidator" 导出的类
import InfoNameValidator from "./name-module";
import InfoAgeValidator from "./age-module";
import InfoGenderValidator from "./gender-module";

let strTest = ["king", "king_88", "he", "hello_typescript", "26", "123", "male"]
let validators: { [s: string]: IInfoValidation } = {}
validators["name"] = new InfoNameValidator();
validators["age"] = new InfoAgeValidator();
validators["gender"] = new InfoGenderValidator();

strTest.forEach((s) => {
    for (let info in validators) {
        console.log(`"${s}" - ${validators[info].isInfoValid(s) ? "matches" : "does not match"} ${info}`);
    }
})

// "king" - matches name
// "king" - does not match age
// "king" - does not match gender
// "king_88" - matches name
// "king_88" - does not match age
// "king_88" - does not match gender
// "he" - does not match name
// "he" - does not match age
// "he" - does not match gender
// "hello_typescript" - does not match name
// "hello_typescript" - does not match age
// "hello_typescript" - does not match gender
// "26" - does not match name
// "26" - matches age
// "26" - does not match gender
// "123" - does not match name
// "123" - does not match age
// "123" - does not match gender
// "male" - does not match name
// "male" - does not match age
// "male" - matches gender