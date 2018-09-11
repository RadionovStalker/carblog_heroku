//Использование POST запроса в AJAX и DJANGO
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


$("#subscribe_control").click(function (){
    console.log("subscribe clicked in js");
    $.ajax({
        type: "GET",
        url: "",
        data: {
            'action': $("input[name$='action']").val(),
        },
        dataType: "json",
        cache: false,
        success: function(data) {
            console.log(data);
            if(data['subscribed']==1){
                $("#subscribe_control").text("Подписаться");
            }
            else if(data['subscribed']==2){
                $("#subscribe_control").text("Отменить подписку");
            }
             $("#subs_rat").text("Всего подписчиков: ".concat(data['count_subs']));
        }
    });
});

$("#like_control").click(function (){
    console.log("like clicked in js!");
   $.ajax({
       type: "GET",
       url: "",
        data: {
           'type': $( "input[name$='type']" ).val(),
        },
        dataType: "json",
        cache: false,
        success: function(data) {
           console.log(data);
           if(data['liked']==1){
              $("#like_control").text("Like");
           }
           else if(data['liked']==2){
              $("#like_control").text("Unlike");
           }
            $("#rating").text("Рейтинг: ".concat(data['count_like']));
        }
    });
});

$(".btn_ans").click(function() {
    console.log("Была нажата кнопка комментария № ".concat($(this).val()));
    var com_id = $(this).val();
    //var com_text = $("p.com_text");
    var com_text = $(this).closest("p");
    var com_author = $(this).closest(".com_author").text();
    console.log(com_text);
    console.log(com_author);
});

function answer(com_id, answer_to, elem){

    if($(elem).val() == 1){
        $(elem).val(2);
        $(elem).text("Отменить");
        $("#answer"+com_id.toString()).empty();
        $("#answer"+com_id.toString()).append(
        '<form method="post">'+
            '<input type="hidden" name="csrfmiddlewaretoken" value="'+csrftoken+'">'+
            '<p>Ответить :'+answer_to+'</p>'+
            '<textarea name="ans_text" placeholder="Введите Ваш ответ тут..."></textarea>'+
            '<input type="hidden" name="coment_id" value='+com_id+' />'+
            '<button type="submit" name="answer" >Подтвердить</button>'+
        '</form>'
        );
    }
    else{
        $(elem).val(1);
        $(elem).text("Ответить");
        $("#answer"+com_id.toString()).empty();
    }
}

function update_comment(com_id, text, elem){
    if($(elem).val() == 1){
        $(elem).val(2);
        $(elem).text("Отменить");
        $("#answer"+com_id.toString()).empty();
        $("#answer"+com_id.toString()).append(
        '<form method="post">'+
            '<input type="hidden" name="csrfmiddlewaretoken" value="'+csrftoken+'">'+
            '<textarea name="upd_com_text">'+text+'</textarea>'+
            '<input type="hidden" name="coment_id" value='+com_id+' />'+
            '<button type="submit" name="update_com" >Подтвердить</button>'+
        '</form>'
        );
    }
    else{
        $(elem).val(1);
        $(elem).text("Редактировать");
        $("#answer"+com_id.toString()).empty();
    }
}

function delete_comment(com_id, elem){
    if($(elem).val() == 1){
        $(elem).val(2);
        $(elem).text("Отменить");
        $("#answer"+com_id.toString()).empty();
        $("#answer"+com_id.toString()).append(
        '<form method="post">'+
            '<input type="hidden" name="csrfmiddlewaretoken" value="'+csrftoken+'">'+
            '<p>Вы уверены, что хотите удалить данный комментарий?</p>'+
            '<p>Для подтверждения удаления, нажмите "Подтвердить"</p>'+
            '<p>Иначе, нажмите "Отменить"</p>'+
            '<input type="hidden" name="coment_id" value='+com_id+' />'+
            '<button type="submit" name="delete_com" >Подтвердить</button>'+
        '</form>'
        );
    }
    else{
        $(elem).val(1);
        $(elem).text("Удалить");
        $("#answer"+com_id.toString()).empty();
    }
}
