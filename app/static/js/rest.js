function search(ele){
    if(event.key === 'Enter') {
        //alert(ele.value);
        // $.get({
        //     url:'/search?keywords='+ele.value,
        //     data:null,
        //     success: success,
        //     dataType: 'image/jpg',
        //     async:false
        // }).success(function(data){
        //     var event = new Event('data-submitted');
        //     event.data = data; 
        //     formEl.dispatchEvent(event);
        // });
        $.ajax({
            url:'/search?keywords='+ele.value,
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