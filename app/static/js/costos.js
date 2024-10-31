function openUploadModal() {
    $('#uploadModal').modal('show');
}

function closeUploadModal() {
    $('#uploadModal').modal('hide');
}

function openVentasMeliModal() {
    $('#ventasMeliModal').modal('show');
}

function closeVentasMeliModal() {
    $('#ventasMeliModal').modal('hide');
}

// AJAX for file upload
$('#uploadButton').on('click', function() {
    var formData = new FormData($('#formVentasMeli')[0]);

    // Hide input and button, show spinner
    $('#fileToUploadMeli').hide();
    $('#uploadButton').hide();
    $('#loadingSpinner').show();

    $.ajax({
        url: 'models/CargaVentasMeli.php',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            try {
                var result = JSON.parse(response);
                if (result.status === 'success') {
                    $('#uploadResult').html('<p style="color:green;">El archivo se cargó correctamente.</p>');
                } else {
                    $('#uploadResult').html('<p style="color:red;">Hubo un error al cargar el archivo: ' + result.message + '</p>');
                }
            } catch (e) {
                console.error("Error parsing JSON:", e, response);
                $('#uploadResult').html('<p style="color:red;">Hubo un error inesperado.</p>');
            }

            $('#uploadResult').show();
            setTimeout(function() {
                $('#uploadResult').hide();
                $('#ventasMeliModal').modal('hide');
                location.reload();
            }, 3000);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Error en la solicitud AJAX:", textStatus, errorThrown);
            $('#uploadResult').html('<p style="color:red;">Error en la solicitud AJAX: ' + textStatus + '</p>');
        },
        complete: function() {
            $('#fileToUploadMeli').show();
            $('#uploadButton').show();
            $('#loadingSpinner').hide();
        }
    });
});

// Utility function
function formatearNumero(campo) {
    let valor = campo.value;
    valor = valor.replace(/,/g, '.');
    if ((valor.match(/\./g) || []).length > 1) {
        valor = valor.replace(/\.(?=.*\.)/g, '');
    }
    campo.value = valor;
}
