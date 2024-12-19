$('#service-add').on('click', function () {
    $('#services-menu-list').hide()
    $('#service-add-panel').show()
})

$('#service-add-back').on('click', function () {
    $('#services-menu-list').show()
    $('#service-add-panel').hide()
})

$('#service-remove').on('click', function () {
    $('#services-menu-list').hide()
    $('#service-remove-panel').show()
})

$('#service-remove-back').on('click', function () {
    $('#services-menu-list').show()
    $('#service-remove-panel').hide()
})


let service_items = []
$('.service-item').on('click', function (event) {
    let item_id = $(this).attr('name').slice(3)
    if (service_items.includes(item_id)) {
        let index = service_items.indexOf(item_id);
        service_items.splice(index, 1);
        $(this).removeClass('service-item-choose')
        if (service_items.length <= 0) {
            $('#service-add-btn').prop("disabled", true)
        }
    } else {
        service_items.push(item_id)
        $(this).addClass('service-item-choose')
        $('#service-add-btn').prop("disabled", false)
    }
})

let service_items_delete = []
$('.service-item-delete').on('click', function (event) {
    let item_id = $(this).attr('name').slice(3)
    if (service_items_delete.includes(item_id)) {
        let index = service_items_delete.indexOf(item_id);
        service_items_delete.splice(index, 1);
        $(this).removeClass('service-item-choose-delete')
        if (service_items_delete.length <= 0) {
            $('#service-delete-btn').prop("disabled", true)
        }
    } else {
        service_items_delete.push(item_id)
        $(this).addClass('service-item-choose-delete')
        $('#service-delete-btn').prop("disabled", false)
    }
})
