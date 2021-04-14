

const nr_questions = 3;
const questionTexts = ["Where did your parents meet?", "What is the name of your first pet?", "What is your hometown?",
    "What is the name of your first (immaginary) partner?", "What is your favorite color?", "What is your favorite profession?"];

function createOptions(question_nr, option_nr=-1){
    
    var questionSelect = document.querySelector("#question" + question_nr);
    if (option_nr == -1){
        var count = 0;
        for (questionText of questionTexts) {
            var opt = document.createElement('option');
            opt.value = count;
            opt.text = questionText;
            questionSelect.options.add(opt);
            count++;
        }
    }else{
        var opt = document.createElement('option');
        opt.value = option_nr;
        opt.text = questionTexts[option_nr];
        questionSelect.options.add(opt);
    }
    
}
function saveOptions(e) {
    e.preventDefault();
    var questions = [];
    var answers = [];
    var selectedQuestionTexts = [];
    for (var question_nr = 1; question_nr <= nr_questions; question_nr++) {
        var questionSelect = document.querySelector("#question" + question_nr);
        var answerInput = document.querySelector("#answer" + question_nr);
        questions[question_nr-1] = questionSelect.value;
        answers[question_nr-1] = answerInput.value;
        selectedQuestionTexts[question_nr-1] = questionTexts[questionSelect.value];
        console.log(questions[question_nr-1], " has answer ", answers[question_nr-1]);
    }
    browser.storage.local.set({
        keypair_recovery: {
            questions: questions,
            answers: answers,
            selectedQuestionTexts
        }
    }
    );
}

function restoreOptions() {


    function setCurrentChoice(result) {

        if (result.keypair_recovery === undefined) {
            for (var question_nr = 1; question_nr <= nr_questions; question_nr++) {
                createOptions(question_nr);
            }

        } else {
            for (var question_nr = 1; question_nr <= nr_questions; question_nr++) {
                createOptions(question_nr, result.keypair_recovery.questions[question_nr-1])
                var answerInput = document.querySelector("#answer" + question_nr);
                answerInput.value = result.keypair_recovery.answers[question_nr-1];
                answerInput.disabled = true; 
            }
            html = document.querySelector("[id='submitButton']");
            html.disabled = true;
        }
    }

    function onError(error) {
        console.log(`Error: ${error}`);
    }

    if (typeof(browser) === "undefined"){
        setCurrentChoice({});
    }else{
        let gettingStoredSettings = browser.storage.local.get();
        gettingStoredSettings.then(setCurrentChoice, onError);
    }
    
}

document.addEventListener("DOMContentLoaded", restoreOptions);
document.querySelector("form").addEventListener("submit", saveOptions);