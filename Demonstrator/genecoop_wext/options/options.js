const pubkeyInput = document.querySelector("#public_key");
const prikeyInput = document.querySelector("#private_key");

function saveOptions(e) {
    e.preventDefault();
    browser.storage.local.set({
        authCredentials: {
            public_key: pubkeyInput.value,
            private_key: prikeyInput.value
        }
    });
}

function restoreOptions() {

    function setCurrentChoice(result) {
        if (result.authCredentials !== undefined) {
            pubkeyInput.value = result.authCredentials.public_key || "";
            prikeyInput.value = result.authCredentials.private_key || "";
        }else{
            pubkeyInput.value = "";
            prikeyInput.value = "";
        }
    }

    function onError(error) {
        console.log(`Error: ${error}`);
    }

    let gettingStoredSettings = browser.storage.local.get();
    gettingStoredSettings.then(setCurrentChoice, onError);
}

document.addEventListener("DOMContentLoaded", restoreOptions);
document.querySelector("form").addEventListener("submit", saveOptions);