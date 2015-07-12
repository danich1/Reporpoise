/* This adds functionality towards the text box when entering data*/
function onBlur(el)
{
    if(el.value == '')
    {
    el.value=el.defaultValue;
    }
}
function onFocus(el)
{
    if(el.value==el.defaultValue)
    {
    el.value='';
    }
}
function init()
{
//lol I don't know JQuery
$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
    $('.alert').hide();
    $('#genes').submit(function(e)
    {
        if (document.getElementById("gene_text").value == document.getElementById("gene_text").defaultValue && document.getElementById("fileToUpload").value=="")
        {
            document.getElementById("message").innerHTML = "You did not insert a file nor input any gene names!!";
            $('.alert').show();
            e.preventDefault();
        }
        else if ($(".sourcecheck:checked").length==0)
        {
            document.getElementById("message").innerHTML = "You did not select an interaction source!!";
            $('.alert').show();
            e.preventDefault();
        }
    })
});
}