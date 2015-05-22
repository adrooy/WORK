$(document).ready(function(){ 
//    $("p:odd").css("background-color", "#bbf"); 
//    $("p:even").css("background-color","#ffc"); 
//
    $("tr").click(function () { 
        $("tr").each(function(){ 
        if($(this).hasClass("highlight")){ 
            $(this).removeClass("highlight"); 
            }}); 
        if($(this).attr('id')){
            $(this).addClass("highlight"); 
        }
    }); 
    $("tr#batch").click(function () { 
        $("tr#batch").each(function(){ 
        if($(this).hasClass("highlight")){ 
            $(this).removeClass("highlight"); 
            }}); 
        if($(this).attr('id')){
            $(this).addClass("highlight"); 
        }
    }); 
    var html = $("#html").val();
/*
    /gg_mgmt/feedback/

    /gg_mgmt/game/
    /gg_mgmt/game/plugin/

    /gg_mgmt/developer/index/
    /gg_mgmt/developer/operation/
    /gg_mgmt/developer/imei/

    /gg_mgmt/market/recommend/
    /gg_mgmt/market/topic/
    /gg_mgmt/market/category/
    /gg_mgmt/market/hotsearch/
    
    /gg_mgmt/release/release/
    /gg_mgmt/release/releaseList/
    /gg_mgmt/release/check/

    /gg_mgmt/uploadGame/otherGame/
    /gg_mgmt/uploadGame/forumGame/
    /gg_mgmt/uploadGame/googleGame/
    /gg_mgmt/uploadGame/uploadGame/
    /gg_mgmt/uploadGame/googlePlugin/
*/
    $("#"+html).removeClass().addClass("panel-collapse collapse in");
});
$("#topic_type").change(function(){
    var topic_type = $("#topic_type").val();
    window.location.href = '/gg_mgmt/market/topic/?source='+topic_type;
});
$("#topic_add").click(function(){
    var topic_id = $(".highlight#topic").attr("value");
    var topic_type = $("#topic_type").val();
    window.location.href = '/gg_mgmt/market/topic_add/?topic_id='+topic_id+'&topic_type='+topic_type;
});
function topic_alter(topic_id) {
    var topic_type = $("#topic_type").val();
    if(topic_id){
        window.location.href = '/gg_mgmt/market/topic_add/?topic_id='+topic_id+'&topic_type='+topic_type;
    }else{
        alert("请选择专题！！！");
    }
};
function topic_isenabled(topic_id) {
    var topic_type = $("#topic_type").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['topic_type'] = topic_type;
    if(topic_id){
        $.post('/gg_mgmt/market/topic_isenabled/', descJson, function(result){
//            alert(result);
            window.location.href = '/gg_mgmt/market/topic/?source='+topic_type;
        });
    }else{
        alert("请选择专题！！！");
    }
};
function topic_notenabled(topic_id) {
    var topic_type = $("#topic_type").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['topic_type'] = topic_type;
    if(topic_id){
        $.post('/gg_mgmt/market/topic_notenabled/', descJson, function(result){
//            alert(result);
            window.location.href = '/gg_mgmt/market/topic/?source='+topic_type;
        });
    }else{
        alert("请选择专题！！！");
    }
};
function topic_up(topic_id) {
    var topic_type = $("#topic_type").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['topic_type'] = topic_type;
    if(topic_id){
        $.post('/gg_mgmt/market/topic_up/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/topic/?source='+topic_type;
            }else{
                alert('已经是第一个专题！！！');
            }
        });
    }else{
        alert("请选择专题！！！");
    }
};
function topic_down(topic_id) {
    var topic_type = $("#topic_type").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['topic_type'] = topic_type;
    if(topic_id){
        $.post('/gg_mgmt/market/topic_down/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/topic/?source='+topic_type;
            }else{
                alert('已经是最后一个专题！！！');
            }
        });
    }else{
        alert("请选择专题！！！");
    }
};
$("#topic_edit").click(function(){
    var not_test = "";
    $('input[type="radio"][name="not_test"]:checked').each(function(){
        not_test = $(this).val();
               //alert($(this).val());
    });
    var id = $("#topic_id").val();
    var name = $("#topic_name").val();
    var short_desc = $("#topic_short_desc").val();
    var detail_desc = $("#topic_detail_desc").val();
    var pic_url = $("#topic_pic_url").val();
    var topic_date = $("#topic_date").val();
    var unrelease_date = $("#unrelease_date").val();
    var order_num = $("#topic_order_num").val();
    var descJson = {}
    var release_time = (new Date(topic_date.replace(new RegExp('-','gm'),'/'))).getTime();
    var unrelease_time = (new Date(unrelease_date.replace(new RegExp('-','gm'),'/'))).getTime();
    descJson['not_test'] = not_test;
    descJson['id'] = id;
    descJson['name'] = name;
    descJson['short_desc'] = short_desc;
    descJson['detail_desc'] = detail_desc;
    descJson['pic_url'] = pic_url;
    descJson['order_num'] = order_num;
    descJson['topic_date'] = topic_date;
    descJson['unrelease_date'] = unrelease_date;
    if (!unrelease_date || unrelease_time > release_time){ 
        $.post('/gg_mgmt/market/topic_edit/', descJson, function(topic_id){
    //        window.location.href = '/gg_mgmt/market/topic_alter/?topic_id='+topic_id;
            alert(topic_id);
        });
    }else{
        alert('请确认发布和上线时间！！！');
    }
});
function topic_delete(topic_id) {
    var topic_type = $("#topic_type").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['topic_type'] = topic_type;
    if(topic_id){
        if(confirm('确认删除吗？')){
            $.post('/gg_mgmt/market/topic_delete/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/topic/?source='+topic_type;
            });
        }else{
            alert('取消删除！');
        }
    }else{
        alert("请选择专题！！！");
    }
};
$("#game_add").click(function(){
    var topic_id = $("#topic_id").val();
    if(topic_id){
        var game_id = prompt('请输入添加的游戏ID');
        var game_id_index = $(".highlight#game").attr("value");
        var descJson = {}
        descJson['topic_id'] = topic_id;
        descJson['game_id'] = game_id;
        descJson['game_id_index'] = game_id_index;
        $.post('/gg_mgmt/market/topic_addGame/', descJson, function(result){
            alert(result);
            window.location.href = '/gg_mgmt/market/topic_alter/?topic_id='+topic_id;
        });
    }
});
$("#game_delete").click(function(){
    var game_id = $(".highlight#game").attr("value");
    var topic_id = $("#topic_id").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['game_id'] = game_id;
    if(game_id){
        if(confirm('确认删除吗？')){
            $.post('/gg_mgmt/market/topic_delGame/', descJson, function(result){
                window.location.href = '/gg_mgmt/market/topic_alter/?topic_id='+topic_id;
            });
        }else{
            alert('取消删除！');
        }
    }else{
        alert("请选择游戏！！！");
    }
});
$("#game_move").click(function(){
    var game_id = $(".highlight#game").attr("value");
    var topic_id = $("#topic_id").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['game_id'] = game_id;
    if(game_id){
        var index = prompt('请输入要移动到的位置');
        descJson['index'] = index;
        $.post('/gg_mgmt/market/topic_moveGame/', descJson, function(result){
                window.location.href = '/gg_mgmt/market/topic_alter/?topic_id='+topic_id+'&game_id='+game_id;
        });
    }else{
        alert("请选择游戏！！！");
    }
});
$("#game_up").click(function(){
    var game_id = $(".highlight#game").attr("value");
    var topic_id = $("#topic_id").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['game_id'] = game_id;
    if(game_id){
        $.post('/gg_mgmt/market/topic_upGame/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/topic_alter/?topic_id='+topic_id+'&game_id='+game_id;
            }else{
                alert('已经是第一个游戏');
            }
        });
    }else{
        alert("请选择游戏！！！");
    }
});
$("#game_down").click(function(){
    var game_id = $(".highlight#game").attr("value");
    var topic_id = $("#topic_id").val();
    var descJson = {}
    descJson['topic_id'] = topic_id;
    descJson['game_id'] = game_id;
    if(game_id){
        $.post('/gg_mgmt/market/topic_downGame/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/topic_alter/?topic_id='+topic_id+'&game_id='+game_id;
            }else{
                alert('已经是最后一个游戏');
            }
        });
    }else{
        alert("请选择游戏！！！");
    }
});
$("#recgame_add").click(function(){
    var game_id = $(".highlight#game").attr("value");
    window.location.href = '/gg_mgmt/market/recommend_addGame/?game_id='+game_id;
});
function recgame_alter(game_id) {
    if(game_id){
        window.location.href = '/gg_mgmt/market/recommend_altGame/?game_id='+game_id;
    }else{
        alert("请选择游戏！！！");
    }
};
function recgame_delete(game_id) {
    var descJson = {}
    descJson['game_id'] = game_id;
    if(game_id){
        if(confirm('确认删除吗？')){
            $.post('/gg_mgmt/market/recommend_delGame/', descJson, function(result){
                window.location.href = '/gg_mgmt/market/recommend/';
            });
        }else{
            alert('取消删除！');
        }
    }else{
        alert("请选择游戏！！！");
    }
};
function recgame_isenabled(game_id) {
    var descJson = {}
    descJson['game_id'] = game_id;
    if(game_id){
        $.post('/gg_mgmt/market/recommend_isenabledGame/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/recommend/';
        });
    }else{
        alert("请选择游戏！！！");
    }
};
function recgame_notenabled(game_id) {
    var descJson = {}
    descJson['game_id'] = game_id;
    if(game_id){
        $.post('/gg_mgmt/market/recommend_notenabledGame/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/recommend/';
        });
    }else{
        alert("请选择游戏！！！");
    }
};
$("#recgame_edit").click(function(){
    var game_id = $("#game_id").val();
    var manual_num = $("#manual_num").val();
    var release_date = $("#release_date").val();
    var unrelease_date = $("#unrelease_date").val();
    var descJson = {}
    descJson['game_id'] = game_id;
    descJson['manual_num'] = manual_num;
    descJson['release_date'] = release_date;
    descJson['unrelease_date'] = unrelease_date;
    var release_time = (new Date(release_date.replace(new RegExp('-','gm'),'/'))).getTime();
    var uneelease_time = (new Date(unrelease_date.replace(new RegExp('-','gm'),'/'))).getTime();
    if (!unrelease_date || unrelease_time > release_time){
        $.post('/gg_mgmt/market/recommend_editGame/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/recommend/';
        });
    }else{
        alert("请确认发布时间和下线时间！！！");
    }
});
function recgame_up(game_id) {
    var descJson = {}
    descJson['game_id'] = game_id;
    if(game_id){
        $.post('/gg_mgmt/market/recommend_upGame/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/recommend/?game_id='+game_id;
            }else{
                alert('已经是第一个游戏');
            }
        });
    }else{
        alert("请选择游戏！！！");
    }
};
function recgame_down(game_id) {
    var descJson = {}
    descJson['game_id'] = game_id;
    if(game_id){
        $.post('/gg_mgmt/market/recommend_downGame/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/recommend/?game_id='+game_id;
            }else{
                alert('已经是最后一个游戏');
            }
        });
    }else{
        alert("请选择游戏！！！");
    }
};
$("#banner_add").click(function(){
    window.location.href = '/gg_mgmt/market/recommend_addBanner/';
});
function banner_alter(banner_id) {
    if(banner_id){
        window.location.href = '/gg_mgmt/market/recommend_addBanner/?banner_id='+banner_id;
    }else{
        alert("请选择专题！！！");
    }
};
$("#banner_edit").click(function(){
    var banner_id = $("#banner_id").val();
    var name = $("#banner_name").val();
    var order_num = $("#order_num").val();
    var game_id = $("#banner_game_id").val();
    var topic_id = $("#banner_topic_id").val();
    var pic_url = $("#banner_pic_url").val();
    var release_date = $("#release_date").val();
    var unrelease_date = $("#unrelease_date").val();
    var descJson = {}
    descJson['banner_id'] = banner_id;
    descJson['name'] = name;
    descJson['order_num'] = order_num;
    descJson['game_id'] = game_id;
    descJson['topic_id'] = topic_id;
    descJson['pic_url'] = pic_url;
    descJson['release_date'] = release_date;
    descJson['unrelease_date'] = unrelease_date;
    //alert(JSON.stringify(descJson));
    var release_time = (new Date(release_date.replace(new RegExp('-','gm'),'/'))).getTime();
    var unrelease_time = (new Date(unrelease_date.replace(new RegExp('-','gm'),'/'))).getTime();
    if (!unrelease_date || unrelease_time > release_time){ 
        $.post('/gg_mgmt/market/recommend_editBanner/', descJson, function(result){
            if(result=='No'){
                alert('请输入正确的游戏或者专题ID！！！');
            }else{
                alert(result);
                window.location.href = '/gg_mgmt/market/recommend/';
            }
        });
     }else{
         alert('请确认发布时间和下线时间！！！');
     }
});
function banner_up(banner_id) {
    var descJson = {}
    descJson['banner_id'] = banner_id;
    if(banner_id){
        $.post('/gg_mgmt/market/recommend_upBanner/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/recommend/?banner_id='+banner_id;
            }else{
                alert('已经是第一个banner');
            }
        });
    }else{
        alert("请选择游戏！！！");
    }
};
function banner_delete(banner_id) {
    var descJson = {}
    descJson['banner_id'] = banner_id;
    if(banner_id){
        if(confirm('确认删除吗？')){
            $.post('/gg_mgmt/market/recommend_delBanner/', descJson, function(result){
                 window.location.href = '/gg_mgmt/market/recommend/';
            });
        }else{
            alert('取消删除！');
        }
    }else{
        alert("请选择banner！！！");
    }
};
function banner_down(banner_id) {
    var descJson = {}
    descJson['banner_id'] = banner_id;
    if(banner_id){
        $.post('/gg_mgmt/market/recommend_downBanner/', descJson, function(result){
            if(result=='Yes'){
                window.location.href = '/gg_mgmt/market/recommend/?banner_id='+banner_id;
            }else{
                alert('已经是最后一个banner');
            }
        });
    }else{
        alert("请选择游戏！！！");
    }
};
function banner_isenabled(banner_id) {
    var descJson = {}
    descJson['banner_id'] = banner_id;
    if(banner_id){
        $.post('/gg_mgmt/market/recommend_isenabledBanner/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/recommend/';
        });
    }else{
        alert("请选择专题！！！");
    }
};
function banner_notenabled(banner_id) {
    var descJson = {}
    descJson['banner_id'] = banner_id;
    if(banner_id){
        $.post('/gg_mgmt/market/recommend_notenabledBanner/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/recommend/';
        });
    }else{
        alert("请选择专题！！！");
    }
};
$("#game_detail").click(function(){
    var game_id = $(".highlight#game").attr("value");
    if(game_id){
    	window.location.href = '/gg_mgmt/game/detail/?game_id='+game_id;
    }else{
        alert("请选择游戏！！！");
    }
});
//_____________________________________________________
//同步论坛数据，发布分类，推荐，专题等
$("#release").click(function(){
    var descJson = {};
    if(confirm('确认发布数据吗？')){
        $.post('/gg_mgmt/market/release/', descJson, function(result){
            alert('发布已完成！');
            window.location.reload();       
        });
    }else{
        alert('取消发步！');
    }
});
$("#update").click(function(){
    var code = ""; //在全局 定义验证码   
    var codeLength = 4;//验证码的长度   
    var checkCode = document.getElementById("checkCode");   
    var selectChar = new Array(0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','wW','x','y','z');//所有候选组成验证码的字符，当然也可以用中文的   
    for(var i=0;i<codeLength;i++)   
    {   
        var charIndex = Math.floor(Math.random()*36);   
        code +=selectChar[charIndex];   
    }   
    var descJson = {};
    var inputCode = prompt("请输入验证码: "+code, "");
    if (inputCode == code){
        $.post('/gg_mgmt/market/update/', descJson, function(result){
            alert(result);
            window.location.reload();       
        });
    }else{
        alert('验证码错误！！！');
    }
});
$("#check").click(function(){
    var descJson = {};
    if(confirm('确认检查失效的游戏和专题吗？')){
        window.location.href = '/gg_mgmt/market/check/';
    }else{
        alert('取消检查！');
    }
});
//________________________________________________________
//分类
$("#category_id").change(function(){
    var category_id = $("#category_id").val();
    window.location.href = '/gg_mgmt/market/category/?category_id='+category_id;
});
$("#cat_game_add").click(function(){
    var category_id = $("#category_id").val();
    window.location.href = '/gg_mgmt/market/category_addGame/?category_id='+category_id;
});
function cat_game_alter(game_id) {
    var category_id = $("#category_id").val();
    if(game_id){
        window.location.href = '/gg_mgmt/market/category_alterGame/?category_id='+category_id+'&game_id='+game_id;
    }else{
        alert("请选择游戏！！！");
    }
};
function cat_game_up(game_id) {
    var category_id = $("#category_id").val();
    if(game_id){
        window.location.href = '/gg_mgmt/market/category/game/up/?category_id='+category_id+'&game_id='+game_id;
    }else{
        alert("请选择游戏！！！");
    }
};
function cat_game_down(game_id) {
    var category_id = $("#category_id").val();
    if(game_id){
        window.location.href = '/gg_mgmt/market/category/game/down/?category_id='+category_id+'&game_id='+game_id;
    }else{
        alert("请选择游戏！！！");
    }
};
$("#cat_game_edit").click(function(){
    var game_id = $("#game_id").val();
    var manual_num = $("#manual_num").val();
    var release_date = $("#release_date").val();
    var unrelease_date = $("#unrelease_date").val();
    var category_id = $("#category_id").val();
    var descJson = {}
    descJson['game_id'] = game_id;
    descJson['manual_num'] = manual_num;
    descJson['release_date'] = release_date;
    descJson['unrelease_date'] = unrelease_date;
    descJson['category_id'] = category_id;
    var release_time = (new Date(release_date.replace(new RegExp('-','gm'),'/'))).getTime();
    var unrelease_time = (new Date(unrelease_date.replace(new RegExp('-','gm'),'/'))).getTime();
    if (!unrelease_date || unrelease_time > release_time){ 
        $.post('/gg_mgmt/market/category_editGame/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/category/?category_id='+category_id;
        });
    }else{
        alert('请确认发布时间和下线时间！！！');
    }
});
function cat_game_delete(game_id) {
    var category_id = $("#category_id").val();
    var descJson = {}
    descJson['game_id'] = game_id;
    descJson['category_id'] = category_id;
    if(game_id){
        if(confirm('确认删除吗？')){
            $.post('/gg_mgmt/market/category_delGame/', descJson, function(result){
                window.location.href = '/gg_mgmt/market/category/?category_id='+category_id;
            });
        }else{
            alert('取消删除！');
        }
    }else{
        alert("请选择游戏！！！");
    }
};
function cat_game_isenabled(game_id) {
    var category_id = $("#category_id").val();
    var descJson = {}
    descJson['game_id'] = game_id;
    descJson['category_id'] = category_id;
    if(game_id){
        $.post('/gg_mgmt/market/category_isenabledGame/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/category/?category_id='+category_id;
        });
    }else{
        alert("请选择游戏！！！");
    }
};
function cat_game_notenabled(game_id) {
    var category_id = $("#category_id").val();
    var descJson = {}
    descJson['game_id'] = game_id;
    descJson['category_id'] = category_id;
    if(game_id){
        $.post('/gg_mgmt/market/category_notenabledGame/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/category/?category_id='+category_id;
        });
    }else{
        alert("请选择游戏！！！");
    }
};
//_____________________________________________________________
//
//热门词
$("#hotsearch").change(function(){
    var word = $("#hotsearch").val();
    window.location.href = '/gg_mgmt/market/hotsearch/?word='+word;
});
$("#hotsearch_add").click(function(){
    var word = prompt('请输入要新增的热门词');
    var order_num = prompt('请输入要新增的热门词序号');
    var descJson = {}
    descJson['word'] = word;
    descJson['order_num'] = order_num;
    $.post('/gg_mgmt/market/hotsearch_add/', descJson, function(result){
        window.location.href = '/gg_mgmt/market/hotsearch/';
    });
});
$("#hotsearch_del").click(function(){
    var word = $(".highlight#word").attr("value");
    var descJson = {}
    descJson['word'] = word;
    if(word){
        if(confirm('确认删除吗？')){
            $.post('/gg_mgmt/market/hotsearch_del/', descJson, function(result){
                window.location.href = '/gg_mgmt/market/hotsearch/';
            });
        }else{
            alert('取消删除');
        }
    }else{
        alert('请选择热门词');
    }
});
function hotsearch_edit(order_num) {
    if(order_num){
        var word= prompt('请输入要编辑的热门词');
        var descJson = {}
        descJson['word'] = word;
        descJson['order_num'] = order_num;
        $.post('/gg_mgmt/market/hotsearch_edit/', descJson, function(result){
            window.location.href = '/gg_mgmt/market/hotsearch/';
        });
    }else{
        alert('请选择热门词');
    }
};
$("#hotsearch_search").click(function(){
    var word = $(".highlight#word").attr("value");
    if(word){
        window.location.href = '/gg_mgmt/market/hotsearch_search/?word='+word;
    }else{
        alert('请选择热门词');
    }
});

//新增游戏浮层____________________________________________________
$(".showgame").click(function(){
    var localid = $(this).attr("localid");
    var id = localid.replace(/[^0-9]/ig,"");
    $("input[name=type]").val(id);
    var box =500;
    var th= $(window).scrollTop()+$(window).height()/1.6-box;
    var h =document.body.clientHeight;
    var rw =$(window).width()/2-box;
    $(".showbox").animate({top:40,opacity:'show',width:800,height:600,right:rw},500);
    $("#zhezhao").css({
        display:"block",height:$(document).height()
    });
    return false;
});
$(".showbox .close").click(function(){
    $(this).parents(".showbox").animate({top:0,opacity: 'hide',width:0,height:0,right:0},500);
    $("#zhezhao").css("display","none");
});
//__________________________________________________________________
