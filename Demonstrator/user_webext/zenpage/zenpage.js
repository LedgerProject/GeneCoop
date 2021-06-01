// import {zencode_exec} from './zenroom/dist/module/zenroom';
const { zencode_exec } = require("zenroom");

const hello_script = 'print("Hello World!")';

function zen_generate(seed, questions, answers) {
    const generate_script = `
    rule check version 1.0.0
    Scenario 'ecdh': create keypair from data
    Given I have a 'string dictionary' named 'QandAandSeed'
    Given I have a 'string' named 'Question1' in 'QandAandSeed'
    Given I have a 'string' named 'Answer1' in 'QandAandSeed'
    Given I have a 'string' named 'Question2' in 'QandAandSeed'
    Given I have a 'string' named 'Answer2' in 'QandAandSeed'
    Given I have a 'string' named 'Question3' in 'QandAandSeed'
    Given I have a 'string' named 'Answer3' in 'QandAandSeed'
    Given I have a 'string' named 'Seed' in 'QandAandSeed'
    When I create the hash of 'QandAandSeed'
    and I rename the 'hash' to 'hashedQandAandSeed'
    When I create the keypair with secret key 'hashedQandAandSeed'
    Then print the 'keypair'`;

    var ques_ans_seed = {};

    for (let count = 0; count < questions.length; count++) {
        ques_ans_seed["Question" + (count + 1)] = questions[count];
        ques_ans_seed["Answer" + (count + 1)] = answers[count];
    }
    ques_ans_seed['Seed'] = seed['seed'];

    const data_togen = {
        "QandAandSeed": ques_ans_seed
    };

    console.log("Hash data to generate key: ", JSON.stringify(data_togen));

    return new Promise(function (resolve, reject) {
        zencode_exec(generate_script, { data: JSON.stringify(data_togen), keys: {}, conf: `color=0, debug=0` })
            .then((result) => {
                console.log("Result from zenroom generate: ", result.result);
                const msg_generate = JSON.parse(result.result)["keypair"];
                console.log("Msg generated: ", JSON.stringify(msg_generate));
                resolve(msg_generate);
            }).catch((error) => {
                console.error("Error in zen_generate function: ", JSON.stringify(error));
                reject(error);
            });
    });

}

function zen_hash(questions, answers) {
    const hash_script = `
    rule check version 1.0.0
    Scenario 'ecdh': create hashes of questions and answers
    Given I have a 'string dictionary' named 'QandA'
    Given I have a 'string' named 'Question1' in 'QandA'
    Given I have a 'string' named 'Answer1' in 'QandA'
    Given I have a 'string' named 'Question2' in 'QandA'
    Given I have a 'string' named 'Answer2' in 'QandA'
    Given I have a 'string' named 'Question3' in 'QandA'
    Given I have a 'string' named 'Answer3' in 'QandA'
    When I create the 'base64 dictionary'
    and I rename the 'base64 dictionary' to 'hashedQandA'
    When I create the hash of 'Question1'
    and I rename the 'hash' to 'Question1.hash'
    When I insert 'Question1.hash' in 'hashedQandA'
    When I create the hash of 'Question2'
    and I rename the 'hash' to 'Question2.hash'
    When I insert 'Question2.hash' in 'hashedQandA'
    When I create the hash of 'Question3'
    and I rename the 'hash' to 'Question3.hash'
    When I insert 'Question3.hash' in 'hashedQandA'
    When I create the hash of 'Answer1'
    and I rename the 'hash' to 'Answer1.hash'
    When I insert 'Answer1.hash' in 'hashedQandA'
    When I create the hash of 'Answer2'
    and I rename the 'hash' to 'Answer2.hash'
    When I insert 'Answer2.hash' in 'hashedQandA'
    When I create the hash of 'Answer3'
    and I rename the 'hash' to 'Answer3.hash'
    When I insert 'Answer3.hash' in 'hashedQandA'
    Then print the 'hashedQandA'`;

    var ques_ans = {};

    for (let count = 0; count < questions.length; count++) {
        ques_ans["Question" + (count + 1)] = questions[count];
        ques_ans["Answer" + (count + 1)] = answers[count];
    }
    const data_tohash = {
        "QandA": ques_ans
    };

    console.log("Hash data to zenroom: ", JSON.stringify(data_tohash));

    return new Promise(function (resolve, reject) {
        zencode_exec(hash_script, { data: JSON.stringify(data_tohash), keys: {}, conf: `color=0, debug=0` })
            .then((result) => {
                console.log("Result from zenroom hash: ", result.result);
                const msg_hash = JSON.parse(result.result);
                // console.log("Msg hash: ", JSON.stringify(msg_hash));
                resolve(msg_hash);
            }).catch((error) => {
                console.error("Error in zen_hash function: ", error);
                reject(error);
            });
    });

}

function zen_sign(public_key, private_key, tosign) {
    const sign_script = `
    rule check version 1.0.0
    Scenario 'ecdh': create the signature of a request
    Given I am 'Signer'
    Given I have my 'keypair'
    Given that I have a 'string' named 'message'
    When I create the signature of 'message'
    When I rename the 'signature' to 'message.signature'
    Then print the 'message.signature'`;

    const data = {
        "message": tosign,
        "Signer": {
            "keypair": {
                "private_key": private_key,
                "public_key": public_key
            }
        }
    };
    console.log("Data: ", data);
    return new Promise(function (resolve, reject) {

        zencode_exec(sign_script, { data: JSON.stringify(data), keys: {}, conf: `color=0, debug=0` })
            .then((result) => {
                console.log(result);
                const msg_sign = JSON.parse(result.result)["message.signature"];
                console.log("Msg signature: ", msg_sign);
                resolve(msg_sign);
            }).catch((error) => {
                console.error("Error in zenroom sign function: ", error);
                reject(error);
            });
    });

}

function zen_vc_sign(public_key, private_key, vc_text, user_id) {
    const sign_vc_script = `
    rule check version 1.0.0
    Scenario 'w3c' : sign
    Scenario 'ecdh' : keypair
    Given that I am 'Issuer'
    Given I have my 'keypair'
    Given I have a 'verifiable credential' named 'my-vc'
    Given I have a 'string' named 'PublicKeyUrl' inside 'Issuer'
    When I sign the verifiable credential named 'my-vc'
    When I set the verification method in 'my-vc' to 'PublicKeyUrl'
    Then print 'my-vc' as 'string'`;


    const data = {
        "my-vc": vc_text
    };
    const keys = {
        "Issuer": {
            "keypair": {
                "private_key": private_key,
                "public_key": public_key
            },
            "PublicKeyUrl": user_id
        }
    };
    console.log("Data: ", JSON.stringify(data));
    console.log("Keys: ", JSON.stringify(keys));
    return new Promise(function (resolve, reject) {

        zencode_exec(sign_vc_script, { data: JSON.stringify(data), keys: JSON.stringify(keys), conf: `color=0, debug=0` })
            .then((result) => {
                console.log("Result", JSON.stringify(result));
                const signed_vc_str = JSON.stringify(JSON.parse(result.result)['my-vc']);
                console.log("Signed vc: ", signed_vc_str);
                resolve(signed_vc_str);
            }).catch((error) => {
                console.error("Error in zenroom sign function: ", JSON.stringify(error));
                reject(error);
            });
    });

}

(function () {

    /**
     * Check and set a global guard variable.
     * If this content script is injected into the same page again,
     * it will do nothing next time.
     */
    if (window.hasRun) {
        console.log("zenpage already started")
        return;
    }
    window.hasRun = true;


    function onError(e) {
        console.error(e);
    }

    // function extractContent(s) {
    //     // var span = document.createElement('span');
    //     // span.innerHTML = s;
    //     // return span.textContent || span.innerText;
    //     return JSON.parse(s.textContent);
    // };

    // function processContent(s) {
    //     s = s.replace(/\n+/g, ' ')
    //     s = s.replace(/\t+/g, ' ')
    //     s = s.replace(/\s+/g, ' ')
    //     return s;
    // }
    // function hash_contract(contract) {
    //     // no hashing for the moment
    //     return contract;
    // };

    function prepare_vc(vc_text, username) {

        vc_text = vc_text.replaceAll('__DATE__', new Date().toISOString());
        vc_text = vc_text.replaceAll('__DNA_DONOR_ID__', username);

        console.log("Textual VC: ", vc_text);

        const vc_json = JSON.parse(vc_text);

        console.log("Parsed VC: ", JSON.stringify(vc_json));
        return vc_json;
    };

    function toggle_instructions() {
        let div = document.querySelector("[id='action-required-genecoop-plugin']");
        if (div !== null) {
            div.style = 'display: none;visibility: hidden;';
        }

        div = document.querySelector("[id='action-done-genecoop-plugin']");
        if (div !== null) {
            div.style = 'display: block;visibility:visible;';
        }

    }
    /**
    */
    async function get_serverseed(msg_hash, username) {
        let url = username + '/seed/';
        let data = { 'message': msg_hash };
        console.log('get_serverseed url to call: ', url);
        console.log('get_serverseed message: ', data);

        const response = await fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            // mode: 'cors', // no-cors, *cors, same-origin
            // cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            // credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json'
            },
            // redirect: 'follow', // manual, *follow, error
            // referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
            body: JSON.stringify(data) // body data type must match "Content-Type" header
        });
        resp = response.json();
        console.log('get_serverseed returned ', resp);
        return resp;
    }
    /**
    */
    function wrapper_action(action, storedSettings) {
        // This function takes care before performing the action the credentials are available,
        // getting them if necessary
        if (storedSettings.authCredentials === undefined && storedSettings.keypair_recovery === undefined) {
            onError("Please select and answer the questions in the add-on settings");
            return;
        }
        if (storedSettings.authCredentials === undefined) {
            console.log('No credentials yet');
            // generate an hash from the questions/answers to be used as secret for the credentials, together with a server seed.
            zen_hash(storedSettings.keypair_recovery.selectedQuestionTexts, storedSettings.keypair_recovery.answers)
                .then((msg_hash) => {
                    // get the server seed
                    get_serverseed(msg_hash, storedSettings.keypair_recovery.username)
                        .then((seed) => {
                            // generate credentials using the questions/answers and the seed
                            zen_generate(seed, storedSettings.keypair_recovery.selectedQuestionTexts, storedSettings.keypair_recovery.answers)
                                .then((key_pair) => {
                                    browser.storage.local.set({
                                        authCredentials: {
                                            public_key: key_pair.public_key,
                                            private_key: key_pair.private_key
                                        }
                                    }).then(() => {
                                        // now that we have the credentials we can call the action
                                        let gettingStoredSettings = browser.storage.local.get();
                                        gettingStoredSettings.then((x) => { perform_action(action, x) }, onError);
                                    });
                                })
                        });
                })
                .catch((error) => {
                    console.error("Error in wrapper_action function: ", error);
                    throw new Error(error);
                });
        } else {
            // credentials available, proceed to action
            console.log('Credentials available');
            perform_action(action, storedSettings);
        }
    }

    /**
     */
    function perform_action(action, storedSettings) {

        console.log(`${action} called`);

        if (storedSettings.authCredentials === undefined) {
            onError("Auth credentials are undefined");
            return;
        }

        if (action == 'login') {

            const challenge = document.querySelector("[id='challenge']").value;
            console.log("Challenge: ", challenge);

            zen_sign(storedSettings.authCredentials.public_key, storedSettings.authCredentials.private_key, challenge)
                .then((msg_sign) => {
                    console.log("Signature: ", msg_sign);

                    var html = document.querySelector("[id='response']");
                    html.value = JSON.stringify(msg_sign);

                    html = document.querySelector("[id='user_id']");
                    html.value = storedSettings.keypair_recovery.username;

                    toggle_instructions();

                    var button = document.querySelector("[id='proceedButton']");
                    button.style = 'visibility:visible;';
                })
                .catch((error) => {
                    console.error("Error in perform_action function: ", error);
                    throw new Error(error);
                });

        } else if (action == 'sign') {

            const vc = document.querySelector("[id='vc']");

            const vc_json = prepare_vc(vc.textContent, storedSettings.keypair_recovery.username);

            zen_vc_sign(storedSettings.authCredentials.public_key, storedSettings.authCredentials.private_key, vc_json, storedSettings.authCredentials.public_key)
                .then((signed_vc_str) => {

                    var html = document.querySelector("[id='signed_vc']");
                    html.value = signed_vc_str;

                    html = document.querySelector("[id='public_key']");
                    html.value = storedSettings.authCredentials.public_key;

                    html = document.querySelector("[id='username']");
                    html.value = storedSettings.keypair_recovery.username;

                    toggle_instructions();

                    html = document.querySelector("[id='submitButton']");
                    html.disabled = false;
                })
                .catch((error) => {
                    console.error("Error in perform_action function: ", error);
                    throw new Error(error);
                });
        }
    }
    // /**
    //  */
    function reset() {
        console.log("Reset called")
        let existingSignatures = document.querySelectorAll(".signature");
        for (let sig of existingSignatures) {
            sig.remove();
        }
    }

    // /**
    //  * Listen for messages from the browserAction script.
    // */
    browser.runtime.onMessage.addListener((message) => {
        let gettingStoredSettings = browser.storage.local.get();
        if (message.command === "login") {
            gettingStoredSettings.then((x) => { wrapper_action('login', x) }, onError);
        } else if (message.command === "sign") {
            gettingStoredSettings.then((x) => { wrapper_action('sign', x) }, onError);
        } else if (message.command === "getcredentials") {
            gettingStoredSettings.then((x) => { get_credentials(x.keypair_recovery) }, onError);
        } else if (message.command === "reset") {
            reset();
        }
    });

    console.log("zenpage start");
})();

