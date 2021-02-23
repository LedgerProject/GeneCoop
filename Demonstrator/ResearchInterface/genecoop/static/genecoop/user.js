//on agreement-change toggle the selected permissions, 
//and enable submit button when allowed by optionality 
function onAgreementChange(e)
{
    togglePermissions(e);
    checkOptionality();
}

//enable button only when all mandatory fields are yes
function checkOptionality()
{
    let button = document.getElementById("submitButton");
    var mandatory_options = document.querySelectorAll('.mandatory');
    let checked = Array.from(mandatory_options).map(item =>{
        //the yes options is the one of which the value ends with _000, there is only one.
        let yes = Array.from(item.getElementsByTagName('input'))
            .filter(el => el.value.endsWith("_000"))[0];
        return yes.checked;
    });

    let allowed = checked.reduce((res,cur) => res && cur, true);
    button.disabled = !allowed;
}

//toggle visibility of li in permissions, based on agreements
function togglePermissions(e)
{
    var selected = e.target.value.endsWith('_000');//yes value
    var selector = '.op_' + e.target.id;
    var permissions = document.getElementById('permissions').querySelectorAll(selector);
    permissions.forEach(function(permission){
        permission.style.display = selected ? 'block' : 'none'; 
    });
}
