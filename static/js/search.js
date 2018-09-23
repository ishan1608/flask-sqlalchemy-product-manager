'use strict';

var ISG = ISG || {};

$(function() {
    let $searchButton = $('#search-button');
    let $searchInput = $('#search-input');

    // Changing search configuration
    const $searchConfig = $('#search-config');
    $searchConfig.find('.dropdown-item').on('click', function(event) {
        let $item = $(event.currentTarget);

        $searchButton.text($item.text());
        $searchButton.attr('data-type', $item.attr('data-type'));
    });

    // Execute search
    $searchButton.on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();

        let queryParams = {};
        let searchType = $searchButton.attr('data-type');
        queryParams.query = $searchInput.val();
        switch (searchType) {
            case 'name':
                queryParams.field = 'name';
                break;
            case 'sku':
                queryParams.field = 'sku';
                break;
        }

        // Display Products
        $.ajax({
            method: 'GET',
            url: ISG.searchUrl +'?' + $.param(queryParams),
        }).done(function (data) {
            let productsList = $('#products-list');
            productsList.html('');
            _.each(data.objects, function (object) {
                productsList.append(_.template($('#ProductTmpl').html())(object));
            });

            registerUpdateListener();
        });
    });
});

// TODO ishan 2018-09-23. This code block is used in many places and can be extracted out in a utility
let registerUpdateListener = function () {
    // Update Product
    $(':input[name="submit"]').on('click', function (event) {
        event.preventDefault();
        event.stopPropagation();

        let $elem = $(event.currentTarget);
        let productId = $elem.attr('data-id');

        let $productContainer = $elem.parent();
        let productName = $productContainer.find(':input[name="name"]').val();
        let productSku = $productContainer.find(':input[name="sku"]').val();
        let productDescription = $productContainer.find(':input[name="description"]').val();
        let productIsActive = $productContainer.find(':input[name="is_active"]').prop('checked');

        $.ajax({
            method: 'PUT',
            url: ISG.productResourceListUrl +productId + '/',
            data: {
                id: productId,
                is_active: productIsActive,
                name: productName,
                sku: productSku,
                description: productDescription
            }
        }).done(function (data) {
            toastr['success']('Product ' + productId + ' Updated', 'Success');
        }).fail(function () {
            toastr["error"]('Failed Updating Product ' + productId, "Success");
        });
    });
};
