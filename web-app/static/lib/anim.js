
var t1=$("#title").offset().top;
var t2=$("#anim7").offset().top;
var t3=$("#manu").offset().top;
var t4=$("#anim20").offset().top;
var t5=$("#gmap").offset().top;
var t6=$("#oc").offset().top;

$(window).scroll(function(){
    "use strict";
var top=$(window).scrollTop();
if(top>t1&&top<t2){
    $("#title").addClass("anim1");
    $("#anim1").addClass("anim1");
    $("#anim2").addClass("anim2");
    $("#anim3").addClass("anim3");
    $("#anim4").addClass("anim4");
    $("#anim5").addClass("anim5");
    $("#anim6").addClass("anim6");
}
if(top>t2&&top<t3){
    $("#anim7").addClass("anim1");
    $("#anim8").addClass("anim2");
    $("#anim9").addClass("anim3");
    $("#anim10").addClass("anim4");
    $("#anim11").addClass("anim5");
    $("#anim12").addClass("anim6");
}
if(top>t3&&top<t4){
    $("#anim13").addClass("anim1");
    $("#anim14").addClass("anim2");
    $("#anim15").addClass("anim3");
    $("#anim16").addClass("anim4");
    $("#anim17").addClass("anim5");
    $("#anim18").addClass("anim6");
}
if(top>t4&&top<t5){
    $("#anim19").addClass("anim1");
    $("#anim20").addClass("anim2");
    $("#anim21").addClass("anim3");
    $("#gmap").addClass("anim4");
}
if(top>t5&&top<t6){
    $("#oc").addClass("anim1");

}
});// JavaScript Document