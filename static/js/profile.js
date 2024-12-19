$('#plane-add').on('click', function (e) {
    $('#plane-add-panel').fadeIn(100, function () {
        $('#profile-form input').focus()
    })
})

$('#plane-add-cancel').on('click', function (e) {
    $('#plane-add-panel').fadeOut(100, function () {
        $('#profile-form input').removeClass('line-input-error')
        $('#profile-form input').val('')
    })
})

$('#profile-form').submit(function (e) {
    if ($('#profile-form input').val() === '') {
        $('#profile-form input').addClass('line-input-error')
        e.preventDefault()
    }
})

$('#profile-form input').click(function () {
    $('form input').removeClass('line-input-error')
})
