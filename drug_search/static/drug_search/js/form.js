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