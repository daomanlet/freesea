var sites = { "油管": "youtube", "P站": "pornhub" }
var progress = 0;
var taskStatus = { "detail": "init", "image": "init" };

function progressBarMove() {
    if (progress == 0) {
        progress = 1;
        taskStatus = { "detail": "init", "image": "init" };
        var elem = document.getElementById("progressbar");
        elem.className = 'progress-bar';
        var width = 10;
        var id = setInterval(frame, 100);

        function frame() {
            if (width >= 100) {
                clearInterval(id);
                progress = 0;
                elem.className = 'hidden';
                elem.innerHTML = '';
                $("#search-text").removeAttr("readonly");
            } else {
                if (width < 80) {
                    width++;
                    elem.style.width = width + "%";
                    elem.innerHTML = '正在提取信息' + width + "%";
                } else {
                    if (taskStatus["image"] == 'done') {
                        if (width >= 80) {
                            width = width + 10;
                            elem.style.width = width + "%";
                            elem.innerHTML = '网页形成截图完成 ' + width + "%";
                            taskStatus["image"] = 'init';
                        }
                    }
                    if (taskStatus["detail"] == 'done') {
                        if (width >= 80) {
                            width = width + 10;
                            elem.style.width = width + "%";
                            elem.innerHTML = '视频信息提取完成 ' + width + "%";
                            taskStatus["detail"] = 'init';
                        }
                    }
                }
            }
        }
    }
}

function showSearchResult(ele) {
    var domain = sites[document.getElementById('domainbutton').innerHTML];
    if (domain == null) {
        domain = 'youtube';
    }
    $.getJSON('/subscribe?keywords=' + ele.value + '&domain=' + domain)
        .done(function(data) {
            var i = 0;
            $("#search_result").empty();
            var some = data.filter(function(value, index, array) { return index < 20; })
            some.forEach(obj => {
                var c1 = $("<div class='col-sm-8'>").append("<span class='mb-1  text-info'>" + obj['title'] + "</span>")
                var c2;
                if (i == 0) {
                    c2 = $("<div class='col-sm-2'>").append("<a href=/download?id=" +
                        obj['id'] +
                        '&domain=' +
                        domain + "><span class='mb-1  text-warning'>点击下载</span></a>");
                } else if (i <= 20) {
                    c2 = $("<div class='col-sm-2'>").append("<a href='/about'><span class='mb-1  text-warning'>点击订阅</span></a>");
                }
                var row = $("<div/>").addClass("row mb-1");
                row.append($("<div class='col-sm-1'/>"));
                row.append(c1);
                row.append(c2);
                row.append($("<div class='col-sm-1/>"));
                $("#search_result").append(row);
                i++;
            });
            taskStatus['detail'] = 'done';

        });

}

function search(ele) {
    if (event.key === 'Enter') {
        $("#search-text").attr("readonly", "readonly");
        var domain = sites[document.getElementById('domainbutton').innerHTML];
        if (domain == null) {
            domain = 'youtube';
        }
        progressBarMove();
        showSearchResult(ele)
        $.ajax({
            url: '/search?keywords=' + ele.value + '&domain=' + domain,
            cache: false,
            xhr: function() { // Seems like the only way to get access to the xhr object
                var xhr = new XMLHttpRequest();
                xhr.responseType = 'blob'
                return xhr;
            },
            success: function(data) {
                var img = document.getElementById('img');
                var url = window.URL || window.webkitURL;
                img.onload = function() {
                    taskStatus["image"] = 'done'
                }
                img.src = url.createObjectURL(data);

            },
            error: function() {

            }
        });
    }
}