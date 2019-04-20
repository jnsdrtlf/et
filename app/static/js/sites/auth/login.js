'use strict';

var form = $('.form-auth');
var url = form.attr('action');

form.submit(function (ev) {
    ev.preventDefault();
    ev.stopPropagation();

    $('.is-invalid').removeClass('is-invalid');
    form.removeClass('was-validated');

    if (!form[0].checkValidity()) {
        form.addClass('was-validated');
        return;
    }

    let data = form.serialize();
    $('#buttonSubmit').button('loading');
    $.post(url, data)
        .done(function (res) {
            window.location = res.redirect;
        })
        .fail(function () {
            $('#feedback').show();
        })
        .always(function () {
            $('#buttonSubmit').button('reset');
        })

});

$('input').on('change', function () {
    $(this).removeClass('is-invalid');
});

$('#inputEmail, #inputPassword').on('change', function () {
    $('#feedback').hide();
});