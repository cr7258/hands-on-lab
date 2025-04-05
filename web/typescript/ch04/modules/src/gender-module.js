"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var infoGenderRegexp = /^male|female$/;
var InfoGenderValidator = /** @class */ (function () {
    function InfoGenderValidator() {
    }
    InfoGenderValidator.prototype.isInfoValid = function (info) {
        return infoGenderRegexp.test(info);
    };
    return InfoGenderValidator;
}());
exports.default = InfoGenderValidator;
