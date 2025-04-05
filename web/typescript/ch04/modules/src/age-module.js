"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var infoAgeRegexp = /^[0-9][0-9]?$/;
var InfoAgeValidator = /** @class */ (function () {
    function InfoAgeValidator() {
    }
    InfoAgeValidator.prototype.isInfoValid = function (info) {
        return infoAgeRegexp.test(info);
    };
    return InfoAgeValidator;
}());
exports.default = InfoAgeValidator;
