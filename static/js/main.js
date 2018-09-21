// Global
ISG = {};

ISG.updateCount = function(type, count) {
    var selector;
    switch (type) {
        case 'active':
            selector = $('#active-product-count');
            break;
        case 'inactive':
            selector = $('#inactive-product-count');
            break;
        default:
            break;
    }
    selector.text(count);
};

$(function () {
    ISG.productHeadRequest = $.ajax({
        method: 'HEAD',
        url: '/product/',
    }).done(function () {
        ISG.updateCount('active', ISG.productHeadRequest.getResponseHeader('ACTIVE_COUNT'));
        ISG.updateCount('inactive', ISG.productHeadRequest.getResponseHeader('INACTIVE_COUNT'));
    });
});