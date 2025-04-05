"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var infoNameRegexp = /^[A-Za-z][A-Za-z0-9_]+$/;
var InfoNameValidator = /** @class */ (function () {
    function InfoNameValidator() {
    }
    InfoNameValidator.prototype.isInfoValid = function (info) {
        if (info == "male" || info == "female") {
            return false;
        }
        else {
            return info.length >= 3 && info.length <= 10 && infoNameRegexp.test(info);
        }
    };
    return InfoNameValidator;
}());
exports.default = InfoNameValidator;
