//toggle visibility of li in permissions, based on agreements
function onAgreementChange(e)
{
    var selected = e.target.value.endsWith('0000');//yes value
    var selector = '.op_' + e.target.id;
    var permissions = document.getElementById('permissions').querySelectorAll(selector);
    permissions.forEach(function(permission){
        permission.style.display = selected ? 'block' : 'none'; 
    });
}
