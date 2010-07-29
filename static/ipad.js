$(document).ready(function(){

    $(window).hashchange(function () {
        //alert(location.hash);
        loadSmart(location.hash.substr(1));
    });

    $(window).hashchange();
 
    bind_a();

    $('#progress').ajaxStart(function() {
        $(this).show();
    });

    $('#progress').ajaxComplete(function() {
        $(this).hide();

        $("#divPosts h1.nav a.btnCenter0").remove();
        $("#boardh1").remove();

        bind_a();

        if ($('#snavbottom').length > 0) {
            if ($('#snavbottom').position().top < $('#divPosts').height() || $("#snavtop:first-child").length == 0) {
                $('#snavbottom').remove();
                $('#snavtop').remove();
            }            
        }
    
    });

    $(window).resize(function() {
        setLayout();
    })
    
    setLayout();
    if (navigator.userAgent.match(/Chrome/i)) return;
    $("#divThreads").jScrollTouch();
    $("#divPosts").jScrollTouch();
});

function setLayout() {
    $("#navcon").css("width", $(window).width() - 90);
    $("#main").css("height", $(window).height()-$("#navboard").height());
}

function hlBoard(bd) {
    $(bd).siblings().css({"background": "", "color": "","text-shadow":""});
    $(bd).css({"background": "#0099FF", "color": "white","text-shadow":"gray 0px 1px 1px;"});
    while ($(bd).position().left > $(window).width()-60) nav2right();
    while ($(bd).position().left < 30) nav2left();
}

function bind_a() {
    $("a").each(function(){
        var url = this.href;
        if (this.pathname == "/") $(this).remove();
        if (url.match(/history.go/)) $(this).remove();
        if (url.match(/javascript/)) return;
        if (url.match(/#/)) return;
        if (url.match(/(board|subject|post)/))
        {
            url = url.replace("board", "iboard").replace("subject","isubject").replace("post","ipost");
            this.href = "#" + url;
   
            $(this).bind('click', function () {
                if ($(this).hasClass("hBoard")) {
                    hlBoard("#"+this.id);
                    //$(this).siblings().css({"background": "", "color": "","text-shadow":""});
                    //$(this).css({"background": "#0099FF", "color": "white","text-shadow":"gray 0px 1px 1px;"});
                }

                if (location.hash == this.hash)
                    $(window).hashchange();

                if (_gaq) {
                    _gaq._getAsyncTracker()._trackPageview(url);
                }
            });
        }
    });
}

function loadSmart(path) {
    var m = path.match(/(iboard|isubject)\/(.*?)\//);
    if (m) hlBoard("#hb"+m[2]);
    if (path.match(/iboard/)) loadBoard(path);
    if (path.match(/isubject/)) loadSubject(path);
    if (path.match(/ipost/)) loadPost(path);
}


function loadBoard(path)
{
    $('#divThreads').load(path);
}

function loadSubject(path)
{
    $('#divPosts').load(path);
}

function loadPost(path)
{
    $('#divPosts').load(path);
}

function nav2left()
{
    $('#navcon').scrollLeft($('#navcon').scrollLeft() - $('#navcon').width());
}

function nav2right()
{
    $('#navcon').scrollLeft($('#navcon').width() + $('#navcon').scrollLeft());
}

