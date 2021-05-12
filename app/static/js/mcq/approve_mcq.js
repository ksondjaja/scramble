$(document).ready(function(){

    
    $(".container").on("click", ".btn-approve-quiz", function(evt){

        let $card = $(this).closest(".card");
        let $id = $card.attr("data-id");
        
        var request = $.ajax({
            type: "POST",
            url: $SCRIPT_ROOT + "/mcq/approve-quiz/" + $id,
            contentType: "application/json; charset=utf-8"
        });
    
        request.done(function(result){
            
            $("#approved-quizzes").prepend(result['html']);
            $card.closest(".card-container").fadeOut(300, function(){
                $(this).remove();
            });

        });
    
        request.fail(function(jqXHR, textStatus){
    
            console.log(jqXHR)
    
        });


        evt.stopPropagation();
        evt.preventDefault();

    });



});


 