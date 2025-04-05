import { IInfoValidation } from "./info-module";

const infoGenderRegexp = /^male|female$/;

export default class InfoGenderValidator implements IInfoValidation {
    isInfoValid(info: string): boolean {
        return infoGenderRegexp.test(info);
    }
}