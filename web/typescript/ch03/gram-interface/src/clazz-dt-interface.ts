interface ITimeDate {
  curTime: Date;
  setTime(cur: Date): void;
  getTime(): Date;
}

class CTime implements ITimeDate {
  curTime: Date;
  constructor(cur: Date) {
    this.curTime = cur;
  };
  setTime(cur: Date): void {
    this.curTime = cur;
  };
  getTime(): Date {
    let curTime: Date;
    if (this.curTime) {
      curTime = this.curTime;
    } else {
      curTime = new Date();
    }
    return curTime;
  };
}

let ct: CTime = new CTime(new Date());
console.log("Now is : " + ct.getTime());
let newTime: Date = new Date('2025/03/23 10:00:00');
ct.setTime(newTime);
console.log("New time is : " + ct.getTime());
