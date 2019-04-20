$(function(){
  var hash = window.location.hash;
  hash && $('[href="' + hash + '"]').tab('show');

  $('a[data-toggle="tab"]').click(function (e) {
    $(this).tab('show');
    var scrollmem = $('body').scrollTop() || $('html').scrollTop();
    window.location.hash = this.hash;
    $('html,body').scrollTop(scrollmem);
  });
});
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})