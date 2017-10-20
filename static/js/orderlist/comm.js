/**
 * Created by zhaoyoucai on 17/9/29.
 */

    //倒计时
    var addTimer = function () {
        var list = [],interval;

        return function (id, updateDateStr,timeoutLeftTime) {
            if (!interval)
                interval = setInterval(go, 1000);

            updateDateStr = updateDateStr.replace(/-/g,"/");
            updateDateStr = updateDateStr.split('.')[0];

            var endDate = new Date(updateDateStr);
            var now = new Date();

            var leftTime = (parseInt(timeoutLeftTime)+endDate.getTime()-now.getTime())/1000;

            list.push({ ele: document.getElementById(id), time: leftTime });
        }

        function go() {
            for (var i = 0; i < list.length; i++) {
                list[i].ele.innerHTML = getTimerString(list[i].time ? list[i].time -= 1 : 0);
                if (!list[i].time)
                    list.splice(i--, 1);
            }
        }

        function getTimerString(time) {
            d = Math.floor(time / 86400),
            h = Math.floor((time % 86400) / 3600),
            m = Math.floor(((time % 86400) % 3600) / 60),
            s = Math.floor(((time % 86400) % 3600) % 60);
            if (time>0)
                if (d>0)
                    //return d + "天" + h + "小时" + m + "分" + s + "秒";
                    return d + "天" + h + "小时" + m + "分";
                else
                    return h + "小时" + m + "分" + s + "秒";

            else return "已到期";
        }
    } ();

