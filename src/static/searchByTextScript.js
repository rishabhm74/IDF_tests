$(document).ready(function(){
  console.log("ready");

  $('.submitButton').on('click', function(){
    let mainText = $(this).parent().parent().parent().find("div:eq(0)").next();
    let mainHeading = mainText.find("div:eq(0)");
    let mainForm = mainHeading.find("form:eq(0)");
    let mainTitle = mainForm.find("button:eq(0)").val();
    //console.log(mainTitle);
    let mainInput = $(this).parent().find("input:eq(0)").val(mainTitle);
    let mainInputVal = mainInput.val();
    console.log(mainInputVal);

    req = $.ajax({
      url : '/acceptTitle',
      type : 'POST',
      data : {mainInputVal : mainInputVal}
    });

    req.done(function(data){
      console.log("done");
    });

  });

});





















/*$(document).ready(function(){

  $('.show_similar_button').on('click', function(e){
    e.preventDefault();
    let mainParent = $(this).parent().parent().parent(); //output
    let mainText = mainParent.find("div:eq(2)");
    let mainHeading = mainText.find("div:eq(0)");
    let mainForm = mainHeading.find("form:eq(0)");
    let mainClassButton = mainForm.find("button:eq(0)");
    let mainTitle = mainClassButton.val();
    let mainInput = mainForm.find("#the_similar_input");
    console.log(mainInput);
    //mainInput.val("this");
    mainInput.val(mainTitle);
    console.log(mainInput.val());
    console.log(mainTitle);
    
    req = $.ajax({
      url : '/theTest',
      type : 'POST',

    });

    req.done(function(){
      console.log("done");
    });

  });

  console.log("it works");

  $('.testButton').on('click', function(){

    theTitle = $('.myclassname').val();
    console.log(theTitle);
    req = $.ajax({
      url : '/theTest',
      type : 'POST'

    });

    req.done(function(data){
      console.log("its done!!")
      //console.log(data.theList);
      $('#thetestDiv').text(data.theList);
    });

  });

*/
