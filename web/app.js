var dataUrl = 'http://jsonp.jit.su/?url=http%3A%2F%2Ffreeshell.de%2F~walot%2Fweb%2Fdata.json';
var fireUrl = 'https://vivid-fire-4385.firebaseio.com/';


Date.prototype.yyyymmdd = function() {
   var yyyy = this.getFullYear().toString();
   var mm = (this.getMonth()+1).toString(); // getMonth() is zero-based
   var dd  = this.getDate().toString();
   return yyyy + (mm[1]?mm:"0"+mm[0]) + (dd[1]?dd:"0"+dd[0]); // padding
};


var createSpinner = function (targetId) {
    var opts = {
      lines: 9, // The number of lines to draw
      length: 20, // The length of each line
      width: 10, // The line thickness
      radius: 30, // The radius of the inner circle
      corners: 1, // Corner roundness (0..1)
      rotate: 0, // The rotation offset
      direction: 1, // 1: clockwise, -1: counterclockwise
      color: '#fff', // #rgb or #rrggbb or array of colors
      speed: 1.5, // Rounds per second
      trail: 60, // Afterglow percentage
      shadow: false, // Whether to render a shadow
      hwaccel: false, // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9, // The z-index (defaults to 2000000000)
      top: '50%', // Top position relative to parent
      left: '50%' // Left position relative to parent
    };

    var spinTarget = document.getElementById(targetId);
    return new Spinner(opts).spin(spinTarget);
}


var createTagsList = function (dataUrl) {
    var updateContent = function (data) {
        var source = $('#template').html();
        var template = Handlebars.compile(source);
        var context = {
            time: data.meta.time,
            links: data.items
        }
        var html = template(context);

        $('#content').html(html);
    };

    var dataRef = new Firebase(fireUrl + 'data/');
    dataRef.once('value', function (snapshot) {
        updateContent(snapshot.val());
    });
}


var createEvents = function () {
    $('#content').delegate('[data-tag]', 'click', function (e) {
        var tag = $(e.target).data('tag');
        var tagRef = new Firebase(fireUrl + 'tags/' + tag);
        tagRef.transaction(function (current) { return current + 1; })

        var ymd = (new Date()).yyyymmdd();
        var countRef = new Firebase(fireUrl + 'counters/' + ymd);
        countRef.transaction(function (current) { return current + 1; })
    });
}


var init = function() {
    createSpinner('content');
    createTagsList(dataUrl);
    createEvents();
}
