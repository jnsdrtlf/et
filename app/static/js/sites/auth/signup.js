'use strict';

var form = $('.form-auth');
var url = form.attr('action');
var nextURL = $('[name="login-url"]').val();

form.submit(function (ev) {
    ev.preventDefault();
    ev.stopPropagation();

    $('.is-invalid').removeClass('is-invalid');
    form.removeClass('was-validated');

    if (!form[0].checkValidity()) {
        form.addClass('was-validated');
        return;
    }
    if ($('#inputPassword').val() !== $('#inputPasswordRpt').val()) {
        $('#inputPasswordRpt').addClass('is-invalid').focus();
        return;
    }
    if ($('#inputPassword').val().length < 8) {
        $('#inputPassword').addClass('is-invalid').focus();
        $('#feedback-password').show();
        return;
    }

    var data = form.serialize();
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
                case 'password length':
                    $('#inputPassword').addClass('is-invalid').focus();
                    $('#feedback-password').show();
                    break;
                default:
                    $('#feedback-other').show();
            }
        })
        .always(function () {
            $('#buttonSubmit').button('reset');
        })

});

$('input').on('change', function () {
    $(this).removeClass('is-invalid');
});

$('#inputEmail').on('change', function () {
    $('#feedback-email').hide();
});

$('#inputPassword').on('change', function () {
    $('#feedback-password').hide();
});