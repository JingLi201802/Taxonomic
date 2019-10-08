function sub() {
    var u_name = document.forms["mainForm"]["userName"].value;
    var u_pass = document.forms["mainForm"]["pass"].value;
    if(u_name!=='' && u_pass!==''){
        window.location.href="index.html";
        if(parent !== null){
            getAES(u_name, u_pass);
        }
    }
}

function getAES(name,pass) {
    var key = pass;
    var p_key = name;
    var enc = getAString(pass,key,p_key);
    return enc;
}

function getAString(pass,key,p_key) {

}

function testing() {
    document.getElementById("alert").style.display="none";
    var u_name = document.forms["mainForm"]["userName"].value;
    var u_pass = document.forms["mainForm"]["pass"].value;
    document.getElementById("test").innerHTML=u_name+" "+u_pass;
}