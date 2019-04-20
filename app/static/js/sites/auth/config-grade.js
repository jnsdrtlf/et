'use strict';

var form = $('.form-auth');
var url = form.attr('action');

function addGrade() {
    var $list = $('#gradeList');
    var $first = $list.children().get(0);
    $($first).clone().appendTo($list).children('.form-control').val('');
    $('.remove').on('click', function() {
        if ($('#gradeList').children().length > 1)
            $(this).parent().parent().remove();
    });
}



form.submit(function (ev) {
    ev.preventDefault();
    ev.stopPropagation();

    $('.is-invalid').removeClass('is-invalid');
    form.removeClass('was-validated');

    if (!form[0].checkValidity()) {
        form.addClass('was-validated');
        return;
    }

    let data = arrayToJson(form.serializeArray());
    data.subjects = data.subjects.split(/\r\n|\r|\n/g);
    data.grades = data.grades.split(/\r\n|\r|\n/g);
    console.log(data);
    $('#buttonSubmit').button('loading');
    $.post(url, data)
        .done(function (res) {
            window.location = res.redirect;
        })
        .fail(function (res) {
            $('#feedback-other').show();
        })
        .always(function () {
            $('#buttonSubmit').button('reset');
        })

});

$('input').on('change', function () {
    $(this).removeClass('is-invalid');
});

function arrayToJson(array){
    var jsonObject = {};

    $.map(array, function(n, i){
        jsonObject[n['name']] = n['value'];
    });

    return jsonObject;
}