'use strict';

$('#form-email').submit(function (e) {
    let form = $(this);
    e.preventDefault();

    $('#form-email > #feedback-other').hide();
    $('#form-email > #feedback-email').hide();
    $('.is-invalid').removeClass('is-invalid');
    form.removeClass('was-validated');

    if (!form[0].checkValidity()) {
        form.addClass('was-validated');
        return;
    }
    
    let url = form.attr('action');
    let data = arrayToJson(form.serializeArray());
    $.ajax({
        url: url,
        type: data._method.toUpperCase(),
        data: data,
        dataType: "json",
        cache: false
    }).done(function() {
        $('#emailModal').modal('hide');
        location.reload();
    }).fail(function(res) {
        if (res.responseJSON.hasOwnProperty('reason')) {
            switch(res.responseJSON.reason) {
                case 'email':
                    $('#form-email > #feedback-email').show();
                    $('#inputEmail').addClass('is-invalid').focus();
                    break;
                default:
                    $('#form-email > #feedback-other').show();
                    break;
            }
        } else {
            $('#form-email > #feedback-other').show();
        }
    });
});

$('#submitEmail').on('click', function () {
    $('#form-email').submit();
});

$('#form-name').submit(function (e) {
    let form = $(this);
    e.preventDefault();
    $('#form-name > #feedback-other').hide();

    form.removeClass('was-validated');

    if (!form[0].checkValidity()) {
        form.addClass('was-validated');
        return;
    }
    
    let url = form.attr('action');
    let data = arrayToJson(form.serializeArray());
    $.ajax({
        url: url,
        type: data._method.toUpperCase(),
        data: data,
        dataType: "json",
        cache: false
    }).done(function() {
        $('#nameModal').modal('hide');
        location.reload();
    }).fail(function() {
        $('#form-name > #feedback-other').show();
    });
});

$('#submitName').on('click', function () {
    $('#form-name').submit();
});

$('#form-role').submit(function (e) {
    let form = $(this);
    e.preventDefault();
    $('#form-role > #feedback-other').hide();
    
    let url = form.attr('action');
    let data = arrayToJson(form.serializeArray());
    $.ajax({
        url: url,
        type: data._method.toUpperCase(),
        data: data,
        dataType: "json",
        cache: false
    }).done(function() {
        $('#roleModal').modal('hide');
        location.reload();
    }).fail(function() {
        $('#form-role > #feedback-other').show();
    });
});

$('#submitRole').on('click', function () {
    $('#form-role').submit();
});

$('#form-lang').submit(function (e) {
    $('#form-lang > #feedback-other').hide();
    let form = $(this);
    e.preventDefault();
    let url = form.attr('action');
    let data = arrayToJson(form.serializeArray());
    $.ajax({
        url: url,
        type: data._method.toUpperCase(),
        data: data,
        dataType: "json",
        cache: false
    }).done(function() {
        $('#langModal').modal('hide');
        location.reload();
    }).fail(function() {
        $('#form-lang > #feedback-other').show();
    });
});

$('#submitLang').on('click', function () {
    $('#form-lang').submit();
});

function arrayToJson(array){
    var jsonObject = {};

    $.map(array, function(n, i){
        jsonObject[n['name']] = n['value'];
    });

    return jsonObject;
}