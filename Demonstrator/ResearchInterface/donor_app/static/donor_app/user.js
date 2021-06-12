//on agreement-change toggle the selected procedures, 
//and enable submit button when allowed by optionality 
const YES = 'gc_schema:Yes';

function onAgreementChange(e) {
    togglePermissions(e);
    checkOptionality();
}

//enable button only when all mandatory fields are yes
function checkOptionality() {
    let button = document.getElementById("submitButton");
    var mandatory_options = document.querySelectorAll('.mandatory');
    var allowed = true;
    mandatory_options.forEach(function (item) {
        var selector = 'input[value=' + CSS.escape(YES) + ']';
        if (!item.querySelector(selector).checked) {
            allowed = false;
        }
    });
    button.disabled = !allowed;
}

//toggle visibility of li in procedures, based on agreements
function togglePermissions(e) {
    var selected = e.target.value == YES;//yes value
    var selector = 'li[class=' + CSS.escape(e.target.id) + ']';
    var procedures = document.getElementById('procedures').querySelectorAll(selector);
    procedures.forEach(function (permission) {
        permission.style.display = selected ? 'list-item' : 'none';
    });
}
