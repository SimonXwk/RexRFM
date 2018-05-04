$('#browseFile1').on('change',function(){
    //get the file name
    var fileName = $(this).val();
    //replace the "Choose a file" label
    $(this).next('.custom-file-label').find('small').html(fileName.substr(fileName.lastIndexOf("\\")+1));
})