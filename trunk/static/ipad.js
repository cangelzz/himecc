$(document).ready(function(){
    $('#progress').ajaxStart(function() {
        $(this).show();
    });

    $('#progress').ajaxComplete(function() {
        $(this).hide();

        $("div#divPosts h1 a.btnCenter").remove();

        $("a").each(function(){
            var url = this.href;
            if (this.pathname == "/") $(this).remove();
            if (url.match(/history.go/)) $(this).remove();
            if (url.match(/javascript/)) return;
            if (url.match(/(board|subject|post)/))
            {
                url = url.replace("board", "iboard").replace("subject","isubject").replace("post","ipost");
                this.href = "javascript:loadSmart('" + url + "')";
            }
        });

        if ($('#snavbottom').length > 0) {
            if ($('#snavbottom').position().top < $('#divPosts').height() || $("#snavtop:first-child").length == 0) {
                $('#snavbottom').remove();
                $('#snavtop').remove();
            }            
        }
    
    });

    $("#main").css("height", $(window).height()-$("#navboard").height()-1);
    if (navigator.userAgent.match(/Chrome/i)) return;
    $("#divThreads").jScrollTouch();
    $("#divPosts").jScrollTouch();
});

function loadSmart(path) {
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



