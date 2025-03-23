var CTime = /** @class */ (function () {
    function CTime(cur) {
        this.curTime = cur;
    }
    ;
    CTime.prototype.setTime = function (cur) {
        this.curTime = cur;
    };
    ;
    CTime.prototype.getTime = function () {
        var curTime;
        if (this.curTime) {
            curTime = this.curTime;
        }
        else {
            curTime = new Date();
        }
        return curTime;
    };
    ;
    return CTime;
}());
var ct = new CTime(new Date());
console.log("Now is : " + ct.getTime());
var newTime = new Date('2025/03/23 10:00:00');
ct.setTime(newTime);
console.log("New time is : " + ct.getTime());
