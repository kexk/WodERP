
$(function () {
    var clipboard = new Clipboard('.CpU');
    var cent = $(".limingcentUrlpic");
    var obj = $("<button class='CpU' data-clipboard-action='copy' data-clipboard-text='' style='position:absolute;width:43px;height:23px;z-index: 1000;top: 0px;right: 0px;background: -webkit-gradient(linear, left top, left bottom, from(#fff), to(#ededed));''>" +
        "<span style='font:200 12px Arial;color:#676269;padding: 1px;'> 复制 </span></button>");
    var btns = $("<div class='btnsss' style='position:absolute;right:0px;top:12px;width:45px;z-index: 100;height:25px;text-align: center;clear: both;border: 1px solid #ccc;border-radius:4px '></div>");
    obj.css({ "cursor": "pointer",border:'0px',boxShadow:'0 0 4px black rgba(0,1px,1px,.3)',borderRadius:'2px'});
    var wrap=$("<div class='limingWarp' style='position:relative;display: inline'></div>");
    var wraptwo=$("<div class='limingWarpson'  style='position:relative;display:inline-block;'></div>");
    $('.limingcentUrlpic').css('display','inline-block');
    clipboard.on('success', function(e) {
        e.clearSelection();
        $.Notification.autoHideNotify('success', 'top right', '','复制成功！','1000');
    });
    clipboard.on('error', function(e) {
    });
    $(document).on('mouseover', '.limingcentUrlpic', function () {
        btns.append(obj);
        if($(this).closest($(".limingWarp")).length<1){
            $(this).wrap(wrap);
        }
        $(this).closest($(".limingWarp")).append(btns);
        var cc=$.trim($(this).text());
        $(".CpU").attr({"data-clipboard-text": cc});
        $(this).next(btns).show();
    });
    $(document).on('mouseover', '.limingcentUrlpicson', function () {
        btns.append(obj);
        if ($(this).find($(".limingWarpson")).length<1?true:false){
            $(this).find("a").wrap(wraptwo);
        }
        $(this).find($('.limingWarpson')).append(btns);
        var cc=$.trim($(this).find("a").text());
        $(".CpU").attr({"data-clipboard-text": cc});
        $(this).find(btns).show();
    });
    $(document).on('mouseout', '.limingcentUrlpicson', function () {
        $(this).find($('.btnsss')).hide();
    });
    $(document).on('mouseover', '.btnsss', function () {
        $(this).show();
    });
    $(document).on('mouseout', '.btnsss', function () {
        $(this).hide();
    });
    $(document).on('mouseout', '.limingcentUrlpic', function () {
        $(this).next(btns).hide();
    });
});
$(document).on('click','.CpU',function(e){
    return false;

});
