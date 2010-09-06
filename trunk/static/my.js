function sortul(ulid)
{
    var ul = document.getElementById(ulid);
    if (ul == null) return;
    var lis = ul.getElementsByTagName("li");
    var len = lis.length;
    if (len > 0) {
        for (var i=len-1;i>=0;i--)
            ul.appendChild(lis[i]);
    }
    
    var as = ul.parentElement.getElementsByClassName("btnCenter0 fleft");
    for (var a=0;a<as.length;a++)
    {
        var cname = as[a].className;
        if (cname.match(/btnSortAZ/)) {
            as[a].className = cname.replace("btnSortAZ", "btnSortZA"); 
            as[a].innerText = "∵";
            continue;
        }
        if (cname.match(/btnSortZA/)) {
            as[a].className = cname.replace("btnSortZA", "btnSortAZ");
            as[a].innerText = "∴";
            continue;
        }
    }
}

function toggleComment() {
    if ($(".expandall")[0].innerText == "≡") {
        $(".hidecomments").show();
        $(".expandall").text("－");
        $("a.excomments").text("-");
    } else {
        $(".hidecomments").hide();
        $(".expandall").text("≡");
        $("a.excomments").text("+");
    }
}

function toggleCommentSingle(id) {
    var ap = $("a#"+id);
    if (ap.text() == "+")
        ap.text("-");
    else ap.text("+");
    ap.next().toggle();
}
