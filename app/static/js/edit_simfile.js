$(document).ready(function(){

    var data = $('#fileData').text();
    data = JSON.parse(data);
    console.log(data);
    
    var editor = CodeMirror.fromTextArea(document.getElementById("codeEditor"), {
        lineNumbers: true,
        mode: "text/x-c++src",
        viewportMargin: Infinity,
        height: "auto"
    });
    
    var initData = data.fdata;
    editor.setSize(null, "650px");
    editor.setValue(initData);
    var contentEdited = false;

    editor.on("change", function(instance, changeObj) {
        contentEdited = true;
        if (contentEdited) {
            $('.button-wrapper').css('display', 'flex');
        }
    });

    $('#discardButton').click(function() {
        editor.setValue(initData);
        contentEdited = false;
        $('.button-wrapper').css('display', 'none');
    });

    $('#updateButton').click(function() {
        // Get commit comment from the user
        var comment = prompt("Please enter your commit comment:", "Updated");
        if (comment === null) {
            // User pressed 'Cancel' on the prompt
            return;
        }

        // Confirm submission
        if (!confirm('Are you sure you want to submit?')) {
            return;
        }

        var updatedContent = editor.getValue();
        var dataToSend = {
            fdata: updatedContent, 
            simfile_id: data.simfile_id,
            comment: comment // use the comment from the prompt
        };

        $.ajax({
            type: "POST",
            url: "/update_simfile",
            data: JSON.stringify(dataToSend),
            contentType: "application/json;charset=utf-8",
            success: function(response){
                console.log(response);
            },
            error: function(error){
                alert("Error: " + error);
            }  
        });

        contentEdited = false;
        initData = updatedContent;
        $('.button-wrapper').css('display', 'none');
    });
});

