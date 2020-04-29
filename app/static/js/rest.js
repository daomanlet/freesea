var sites = { "油管": "youtube", "P站":"pornhub"}


function search(ele){
    if(event.key === 'Enter') {
        var domain = sites[document.getElementById('domainbutton').innerHTML];
        if (domain == null){
            domain = 'youtube';
        }
        $.ajax({
            url:'/search?keywords='+ele.value+'&domain='+domain,
            cache:false,
            xhr:function(){// Seems like the only way to get access to the xhr object
                var xhr = new XMLHttpRequest();
                xhr.responseType= 'blob'
                return xhr;
            },
            success: function(data){
                var img = document.getElementById('img');
                var url = window.URL || window.webkitURL;
                img.src = url.createObjectURL(data);
            },
            error:function(){
                
            }
        });                
    }
}