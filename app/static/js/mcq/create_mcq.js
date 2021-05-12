import { Question, Option } from './mcq_models.js';

$(document).ready(function(){


    // Click listeners for various functions

    $("#btn-add-question").on('click', add_question);

    $(".container").on('click', '.btn-add-option', function() {
        add_option($(this).closest('.question'));
    });

    $(".container").on('click', '.btn-remove-question', function(){
        
        $(this).closest(".question").remove();

    });

    $(".container").on('click', '.btn-remove-option', function(){
        $(this).closest(".option").remove();
    });


    $("#btn-submit-quiz").on('click', submit_quiz)

});


// Adds a question form to the page
function add_question() {

    let $clone = $("#mcq-question-template").html();

    let $row = $("#btn-add-question").closest(".row");
    $($clone).insertBefore($row);
     

}

// Adds an option to the question 
// question object must be passed 

function add_option($question) {

   
    let $clone = $("#mcq-option-template").html();
    let $row = $question.find(".btn-add-option").closest(".row");
    $($clone).insertBefore($row);


}

// Sends a request to submit the quiz
function submit_quiz() {
   

 

    var request = $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/mcq/create",
        data: fetch_questions(),
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

// Returns a JSON representation of all of the current questions and their options
function fetch_questions() {

    let title = $('#quiz-title').val();
    let description = $('#quiz-description').val();
    
    

    let  json = {title: title, description:description, questions: []};

   $(".container").find(".question").each(function(){

        let title = $(this).find('.question-title').val();
        let category = $(this).find('.question-category').val();
        let content = $(this).find('.question-content').val();
      
        let options = [];
        
        $(this).find(".option").each(function(){

            let content = $(this).find('.option-content').val();
            let isChecked = $(this).find('.option-is-correct').is(":checked");
            
            options.push(new Option(content, isChecked));

        });


        json.questions.push(new Question(title, category, content, options));



   })
   
   return JSON.stringify(json);
}






 