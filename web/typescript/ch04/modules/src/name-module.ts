import { IInfoValidation } from "./info-module";

const infoNameRegexp = /^[A-Za-z][A-Za-z0-9_]+$/;

export default class InfoNameValidator implements IInfoValidation {
    isInfoValid(info: string): boolean {
        if( info == "male" || info == "female") {
            return false;
        } else {
            return info.length >= 3 && info.length <= 10 && infoNameRegexp.test(info);
        }
    }
}