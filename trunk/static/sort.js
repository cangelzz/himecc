function sort(ulid)
{
    var ul = document.getElementById(ulid);
    var lis = ul.getElementsByTagName("li");
    var len = lis.length;
    if (len > 0) {
        for (var i=len-1;i>=0;i--)
            ul.appendChild(lis[i]);
    }
}
