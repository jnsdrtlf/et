'use strict';

var form = $('.form-auth');
var url = form.attr('action');
var password = $('[name=form]').val() === 'password';

form.submit(function (ev) {
    ev.preventDefault();
    ev.stopPropagation();

    $('.is-invalid').removeClass('is-invalid');
    $('#feedback').hide();
    form.removeClass('was-validated');

    if (!form[0].checkValidity()) {
        form.addClass('was-validated');
        return;
    }

    if (password && $('#inputPassword').val() !== $('#inputPasswordRpt').val()) {
        $('#inputPasswordRpt').addClass('is-invalid');
        return;
    }

    if (password && $('#inputPassword').val().length < 8) {
        $('#inputPassword').addClass('is-invalid').focus();
        $('#feedback-password').show();
        return;
    }

    let data = form.serialize();
    $('#buttonSubmit').button('loading');
    $.post(url, data)
        .done(function (res) {
            window.location = res.redirect;
        })
        .fail(function (res) {
            switch (res.responseJSON.reason) {
                case 'email':
                    $('#inputEmail').addClass('is-invalid').focus();
                    $('#feedback-email').show();
                    break;
                case 'password':
                    $('#inputPassword').addClass('is-invalid').focus();
                    $('#feedback-password').show();
                    break;
                case 'token not found':
                case 'token expired':
                    $('#feedback-token').show();
                    break;
            }
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