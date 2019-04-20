const a = '<a href="" class="my-2 mb-0 list-group-item list-group-item-action border-0 rounded shadow">';
const container = '<div class="d-flex align-items-center flex-row">';
const image = '<img class="rounded-circle" alt="" width="30px" height="30px">';
const name = '<div class="ml-2">';
const containerSubjects = '<div class="ml-4 text-muted small">';
const item = '<span class="ml-2">';
const itemEnabledClass = 'text-primary';
const arrow = '<i class="ml-auto" data-feather="chevron-right">';


$('#subjectForm > button').on('click', function() {
    _subjects = []
    // the active class is added after this function call
    $('#subjectForm > button').each(function() {
        if ($(this).hasClass('active')) {
            _subjects.push($(this).data('id'));
        }
    });

    if (!$(this).hasClass('active')) {
        _subjects.push($(this).data('id'));
    } else {
        let index = _subjects.indexOf($(this).data('id'));
        if (index > -1) {
            _subjects.splice(index, 1);
        }
    }

    $.get($('#subjectForm').attr('action'), {'subjects[]': _subjects}, function(data) {
        $('#container').empty();
        if (data.length == 0) {
            $('#notFound').show();
            return;
        } else {
            $('#notFound').hide();
        }
        for (let i = 0; i < data.length; i++) {
            let user = data[i];
            let _a = $(a);
            _a.attr('href', '/user/' + user.id);

            let _container = $(container);
            _container.appendTo(_a);

            let _image = $(image);
            _image.attr('src', user.picture);
            _image.attr('alt', user.name);
            _image.appendTo(_container);

            let _name = $(name);
            _name.text(user.name);
            _name.appendTo(_container);

            let _containerSubjects = $(containerSubjects);
            _containerSubjects.appendTo(_container);

            for (let s = 0; s < user.subjects.length; s++) {
                let _subject = $(item);
                _subject.text(user.subjects[s].name);
                _subject.appendTo(_containerSubjects);
            }
            for (let w = 0; w < user.weekdays.length; w++) {
                let _weekday = $(item);
                if (user.weekdays[w].available) _weekday.addClass(itemEnabledClass);
                _weekday.text(user.weekdays[w].name);
                _weekday.appendTo(_containerSubjects);   
            }

            $(arrow).appendTo(_container);
            _a.appendTo($('#container'));
            feather.replace();
        }
    });
});