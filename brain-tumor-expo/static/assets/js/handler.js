//Trigger gambar 1
$('#imageOneDisplay').on('click', function (e) {
  //   alert('called');
  let inputFile = $('#imageOne');
  if (inputFile.val()) {
    // alert('called');
    Swal.fire({
      title: 'Mau ngapain?',
      icon: 'question',
      showDenyButton: true,
      showCancelButton: true,
      confirmButtonColor: '#F96D00',
      confirmButtonText: 'Ganti gambar',
      denyButtonText: `Hapus gambar`,
      cancelButtonText: `Batal`,
    }).then((result) => {
      if (result.isConfirmed) {
        inputFile.val('');
        $('#imageOneDisplay').css('background-image', 'unset');
        $('#signOne').css('opacity', '1');
        $('#signOne').css('visibility', 'visible');
        inputFile.css('opacity', '0');
        inputFile.css('visibility', 'visible');
        inputFile.click();
      } else if (result.isDenied) {
        $('#imageOneDisplay').css('background-image', 'unset');
        inputFile.val('');
        $('#signOne').css('opacity', '1');
        $('#signOne').css('visibility', 'visible');
        inputFile.css('opacity', '0');
        inputFile.css('visibility', 'visible');
        $(this).css('border', 'none');
        $('#signOne').text('Upload or drop your image right here');
        $('#signOne').css('color', '#5A6A85');
      }
    });
  } else {
    // inputFile.click
    // alert('called');
  }
});

$('#imageOneDisplay').on('dragover', function (e) {
  e.preventDefault();
  e.stopPropagation();
  $(this).addClass('dragover');
  $(this).css('border', '#C33BFE dashed');
  $('#signOne').text('Drop here...');
  $('#signOne').css('color', '#C33BFE');
  $('#imageOne').css('opacity', '0');
  $('#imageOne').css('visibility', 'unset');
});
$('#imageOneDisplay').on('dragleave', function (e) {
  e.preventDefault();
  e.stopPropagation();
  $(this).removeClass('dragover');
  $(this).css('border', 'none');
  $('#signOne').text('Upload or drop your image right here');
  $('#signOne').css('color', '#5A6A85');
});
$('#imageOneDisplay').on('drop', function (e) {
  //   e.preventDefault();
  //   e.stopPropagation();
  $(this).removeClass('dragover');
  $(this).css('border', 'none');
  $('#signOne').css('opacity', '0');
  $('#signOne').css('visibility', 'hidden');
  $('#imageOne').css('opacity', '0');
  $('#imageOne').css('visibility', 'hidden');
});

function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      $('#imageOneDisplay').css(
        'background-image',
        'url(' + e.target.result + ')'
      );
      $('#imageOneDisplay').hide();
      $('#imageOneDisplay').fadeIn(650);
    };
    reader.readAsDataURL(input.files[0]);
  }
}

$('#imageOne').on('change', function (params) {
  //   alert('called');
  let fileInput = document.getElementById('imageOne');
  if (fileInput.files.length > 0) {
    const fileSize = fileInput.files.item(0).size;
    const fileMb = fileSize / 1024 ** 2;
    if (fileMb >= 2) {
      fileInput.value = '';
      swal.fire({
        icon: 'warning',
        title: 'Ukuran file terlalu besar',
        text: 'Pastikan ukuran gambar yang kamu upload tidak lebih dari 2MB',
      });
    } else {
      readURL(this);
      $('#signOne').css('opacity', '0');
      $('#signOne').css('visibility', 'hidden');
      $('#imageOne').css('opacity', '0');
      $('#imageOne').css('visibility', 'hidden');
    }
  }
});

$('#btn-predict').click(function (e) {
  let desc = $('#desc').val();
  let image = $('#imageOne').val();

  if (desc != '' || image != '') {
    e.preventDefault();
    //   $(this).hide();
    // Make prediction by calling api /predict
    var form_data = new FormData($('#contact-form')[0]);
    $.ajax({
      type: 'POST',
      url: '/predict',

      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      // async: true,
      success: function (data) {
        // Get and display the result
        $('#result-container').removeClass('d-none');
        $('#result-container').addClass('d-grid');

        $('#resultImage').fadeIn(600);
        $('#resultImage').text(data[0]);
        $('#readMoreImage').fadeIn(600);
        $('#readMoreImage').text(data[1]);
        $('#linkImage').attr('href', data[2]);

        $('#resultText').fadeIn(600);
        $('#resultText').text(data[3]);
        $('#readMoreText').fadeIn(600);
        $('#readMoreText').text(data[4]);
        $('#linkText').attr('href', data[5]);

        window.location.hash = '#btn-predict';
      },
    });
  } else {
    swal.fire({
      icon: 'warning',
      title: 'Incomplete Data',
      text: 'Please fill in the form completly',
    });
  }
});
