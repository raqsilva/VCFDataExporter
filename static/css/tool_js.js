
function showonlyone(thechosenone) {
      var newboxes = document.getElementsByTagName("div");
            for(var x=0; x<newboxes.length; x++) {
                  name = newboxes[x].getAttribute("class");
                  if (name == 'newboxes') {
                        if (newboxes[x].id == thechosenone) {
                        newboxes[x].style.display = 'block';
                  }
                  else {
                        newboxes[x].style.display = 'none';
                  }
            }
      }
}



function showonlyone2(thechosenone) {
      var boxes = document.getElementsByTagName("div");
            for(var x=0; x<boxes.length; x++) {
                  name = boxes[x].getAttribute("class");
                  if (name == 'boxes') {
                        if (boxes[x].id == thechosenone) {
                        boxes[x].style.display = 'block';
                  }
                  else {
                        boxes[x].style.display = 'none';
                  }
            }
      }
}



function SelectHandler(select){
		if(select.value == 'xlsx'){
				$("#select_xlsx").show()
				$("#select_vcf").show();
                  }
		else if(select.value == 'vcf'){
				$("#select_vcf").show();
				$("#select_xlsx").hide();
				}
		}



$(document).ready(function() {
    $('#id_populations_5_0').click(function(event) {  //on click
        if(this.checked) { // check select status
            $('.checkbox1').each(function() { //loop through each checkbox
                this.checked = true;  //select all checkboxes with class "checkbox1"              
            });
        }else{
            $('.checkbox1').each(function() { //loop through each checkbox
                this.checked = false; //deselect all checkboxes with class "checkbox1"                      
            });        
        }
    });
   
});



$(document).ready(function() {
    $('#id_columns_12').click(function(event) {  //on click
        if(this.checked) { // check select status
            $('.column1').each(function() { 
                this.checked = true;      
            });
        }else{
            $('.column1').each(function() { 
                this.checked = false;                      
            });        
        }
    });
   
});



$(document).ready(function() {
    $('#id_exac_col_44').click(function(event) {  //on click
        if(this.checked) { // check select status
            $('.add_all').each(function() { 
                this.checked = true;         
            });
        }else{
            $('.add_all').each(function() { 
                this.checked = false;             
            });        
        }
    });
   
});



// loading spinner
//$(document).ready(function(){
//    $('#button-upload').click(function() {
//        $('#spinner').show();
//    });
//});



//$(function() {
//    var form = $("#post-form");
//    form.submit(function(e) {
//        $("#sendbutton").attr('disabled', true);
//        $('#spinner').show();
//        $("#ajaxwrapper2").load(
//            form.attr('action') + '#ajaxwrapper2',
//            form.serializeArray(),
//            function(responseText, responseStatus) { 
//                $("#sendbutton").attr('disabled', false);
//                $('#spinner').hide();
//            }
//        );
//        e.preventDefault();
//    });
//});







