function sortul(ulid)
{
    var ul = document.getElementById(ulid);
    var lis = ul.getElementsByTagName("li");
    var len = lis.length;
    if (len > 0) {
        for (var i=len-1;i>=0;i--)
            ul.appendChild(lis[i]);
    }
    
    var as = ul.parentElement.getElementsByClassName("btnCenterLeft");
    for (var a=0;a<as.length;a++)
    {
        var cname = as[a].className;
        if (cname.match(/btnSortAZ/)) {
            as[a].className = cname.replace("btnSortAZ", "btnSortZA"); 
            continue;
        }
        if (cname.match(/btnSortZA/)) {
            as[a].className = cname.replace("btnSortZA", "btnSortAZ");
            continue;
        }
    }

}
