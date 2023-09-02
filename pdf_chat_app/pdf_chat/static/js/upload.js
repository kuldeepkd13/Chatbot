    // Display the modal when pdf_name is available
    var pdf_name = "{{ pdf_name }}";  // Use Django template tag to get the value
    
    if (pdf_name) {
        var modal = document.getElementById('myModal');
        modal.style.display = "block";
        
        var pdfUploaded = document.getElementById('pdfUploaded');
        var startChatLink = document.getElementById('startChatLink');
        
        pdfUploaded.style.display = "block";
        startChatLink.style.display = "block";
    }