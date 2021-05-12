 /*
Primary scripts for the mcq_quiz file. 
*/


$(document).ready(function(){


    // Display the first question
    let questions = $(".mcq-question");
    
    questions.first().attr("active", '');

    // Start the timer
    var timer = new easytimer.Timer();
    timer.start();
    timer.addEventListener('secondsUpdated', function (e) {
        $('#time-passed').html(timer.getTimeValues().toString());
    });
 
    // Option clicks
    $(".mcq-question").on('click', '.mcq-option', function(){
        
        // Remove currently selected option, if any
        $(this).closest(".mcq-question-options").find(".mcq-option[selected]").removeAttr("selected");
        
        // Set this option as the selected answer
        $(this).attr("selected",""); 
        
        // Move on to the next question
        next_question();

    });

    // Link clicks
    $(".mcq-question-links").on('click', 'li', function(){

        display_question($(this).index());

    });


    // Submission click
    $("#btn-submit-quiz").on('click', function(){
        submit_quiz(timer)
    });


});


function next_question() {

    let index = $('.mcq-question[active]').index();
    display_question(index + 1);

}

function prev_question() {

    let index = $('.mcq-question[active]').index();
    display_question(index - 1);

}

function display_question(index) {



    // If invalid index, don't do anything
    if(index < 0 || index >= $(".mcq-question").length)
        return;


    // Update links
    $(".mcq-question-links").find('.active').removeClass('active');
    $(".mcq-question-links").find("li:eq(" + index + ")").addClass('active');
    


    // Display Question
    let curr_question = $(".mcq-question[active]");
    let question = $('.mcq-question:eq(' + index + ')');
    
    curr_question.fadeOut(300, function(){
        
        curr_question.removeAttr('active');
        
        question.fadeIn(300, function(){
            $(this).attr('active', '');
        });

    });



}
// Returns the answers to each question
function fetch_answers() {

    

    let answers = [];

    $(".mcq-question").each(function(){


        let option_id = $(this).find('.mcq-option[selected]').attr('data-id');
        
        if (option_id)
            answers.push(option_id)

    });


    return answers;

}


// Submits the quiz
function submit_quiz(timer) {


    let data = {time_taken: timer.getTotalTimeValues().seconds, answers: fetch_answers() }

    var request = $.ajax({
        type: "POST",
        data: JSON.stringify(data),
        dataType: "json",
        contentType: "application/json; charset=utf-8"
    });

    request.done(function(result){

        if(result.redirect) {
            window.location.href = result.redirect;
        }
   
    });

    request.fail(function(jqXHR, textStatus){

    console.log(jqXHR)

    });
    

}

