/**
 * Create a calendar html dom
 * 
 * The main purpose of this function is to call the individual
 * functions for the different calendar sizes.
 * 
 * Options: 
 *    - `size` determens the style of the calendar.
 *      Either `small` or `large` (default `small`)
 *    - `container` query for container element
 *    - `date` used for current date, default `new Date()`
 *    - `sessions` array of dates with description
 *
 * `sessions`:
 *    7 arrays starting with sunday
 *    - `title`
 *    - `url`
 *
 * Requires: 
 *    - `moment`
 *    - `jquery`
 *
 * @param {object} options
 * @public
 */
function createCalendar(options) {
    let _options = options || {};
    if (options.size === 'large') {
        _createCalendarLarge(_options);
    } else {
        _createCalendarSmall(_options);
    }
}

/**
 * Create a calendar html dom
 * See `createCalendar` for details
 *
 * @param {object} options
 * @private
 */
function _createCalendarSmall(options) {
    let _options = options || {};
    let sessions = _options.sessions || new Array(7);

    let date = moment(_options.date || new Date());

    let firstDayOfWeek = moment.localeData().firstDayOfWeek();
    let weekdays = _sortWeekdays(moment.weekdaysMin(), firstDayOfWeek);

    $(_options.container).empty();

    let table = $('<table/>')
            .addClass('table text-center table-sm table-hover')
            .appendTo($(_options.container));
    let thead = $('<thead/>').appendTo(table);
    let theadEntry = $('<tr/>').appendTo(thead);

    for (var day = 0; day < weekdays.length; day++) {
        let th = $('<th/>')
            .attr('scope', 'col')
            //.addClass('bg-dark text-light')
            .text(weekdays[day])
            .appendTo(theadEntry);
    }

    // goto first day of first week
    let month = date.month()
    let _date = moment(date).date(1).weekday(0);


    let tbody = $('<tbody/>').appendTo(table);

    while (!(_date.weekday() == 0 && ((_date.month() > month && !(_date.month() == 11 && month == 0)) || (_date.month() == 0 && month == 11)))) {
        let tr = $('<tr/>').appendTo(tbody);
        while (true) {
            let td = $('<td/>').text(_date.date());
            if (sessions[_date.day()] && sessions[_date.day()].length > 0) {
                td.empty();
                let a = $('<a>').attr('href', '#').text(_date.date());
                a.addClass('font-weight-bold');
                td.append(a);
                let entries = ''
                for (session in sessions[_date.day()]) {
                    entries += '<a href="'+ sessions[_date.day()][session].url +'">'+ sessions[_date.day()][session].title +'</a><br>'
                }
                td.popover({
                    content: entries,
                    html: true,
                    placement: 'bottom',
                    //trigger: 'focus'
                });
            }
            if (_date.month() != month) {
                td.addClass('text-muted bg-light');
            } else {
                //td.addClass('font-weight-bold');
            }
            td.appendTo(tr);
            _date.add(1, 'd');
            if (_date.weekday() == 0) break;
        }
    }
}

/**
 * Cahnge order of weekday array according to locale setting
 * @private
 */
function _sortWeekdays(weekdays, firstDayOfWeek) {
    let firstHalf = weekdays.slice(firstDayOfWeek);
    let lastHalf = weekdays.slice(0, firstDayOfWeek);
    return firstHalf.concat(lastHalf);
}