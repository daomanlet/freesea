var sites = { "油管": "youtube", "P站": "pornhub" }
var progress = 0;
var taskStatus = 'init';

function move() {
    if (progress == 0) {
        progress = 1;
        taskStatus = 'init';
        var elem = document.getElementById("progressbar");
        elem.className = 'progress-bar';
        var width = 10;
        var id = setInterval(frame, 10);

        function frame() {
            if (width >= 100) {
                clearInterval(id);
                progress = 0;
                elem.className = 'hidden';
                elem.innerHTML = '';
            } else {
                if (width < 90) {
                    width++;
                    elem.style.width = width + "%";
                    elem.innerHTML = width + "%";
                } else {
                    if (taskStatus == 'done') {
                        width = 100;
                    }
                }
            }
        }
    }
}

function search(ele) {
    if (event.key === 'Enter') {
        var domain = sites[document.getElementById('domainbutton').innerHTML];
        if (domain == null) {
            domain = 'youtube';
        }
        move();
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
                    taskStatus = 'done'
                }
                img.src = url.createObjectURL(data);

            },
            error: function() {

            }
        });
    }
}