$(document).ready(function(){


    // Initially display the top-all table
    $("#table-top-all").show().css('display','table');


    $("#nav-top-all").click(function(){

        $(this).addClass('active')
        $("#nav-top-user").removeClass("active");

        $("#table-top-user").fadeOut(100, function(){
            
            $("#table-top-all").fadeIn(100).css('display','table');

        });

    });




    $("#nav-top-user").click(function(){

        $(this).addClass('active')
        $("#nav-top-all").removeClass("active");
        

        $("#table-top-all").fadeOut(100, function(){

            $("#table-top-user").fadeIn(100).css('display','table');

        });

    });

});