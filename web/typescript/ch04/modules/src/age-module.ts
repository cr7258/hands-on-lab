import { IInfoValidation } from "./info-module";

const infoAgeRegexp = /^[0-9][0-9]?$/;

export default class InfoAgeValidator implements IInfoValidation {
    isInfoValid(info: string): boolean {
        return infoAgeRegexp.test(info);
    }
}

