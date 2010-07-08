$(document).ready(function(){
    $('#progress').ajaxStart(function() {
        $(this).show();
    });

    $('#progress').ajaxComplete(function() {
        $(this).hide();
        $("a").each(function(){
            var url = this.href;
            if (url.match(/javascript/)) return;
            if (url.match(/(board|subject|post)/))
            {
                url = url.replace("board", "iboard").replace("subject","isubject").replace("post","ipost");
                this.href = "javascript:loadSmart('" + url + "')";
            }
        });
     
    });

    $("#main").css("height", $(window).height()-$("#navboard").height());
});

function loadSmart(path) {
    if (path.match(/iboard/)) loadBoard(path);
    if (path.match(/isubject/)) loadSubject(path);
    if (path.match(/ipost/)) loadPost(path);
}


function loadBoard(path)
{
    $('#divThreads').load(path)
}

function loadSubject(path)
{
    $('#divPosts').load(path)
}

function loadPost(path)
{
    $('#divPosts').load(path)
}



