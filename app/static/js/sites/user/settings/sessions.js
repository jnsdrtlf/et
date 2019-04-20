'use strict';

$('[id="buttonRemove"]').on('click', function () {
    let url = $(this).data("url");
    let id = $(this).data("id");
    $.ajax({
        url: url,
        type: 'DELETE',
        dataType: "json",
        cache: false
    }).done(function () {
        $('#session' + id).remove();
    });
});