$('form').on('submit', function (event) {
    let email = $('#email').val()
    let error_text = ''
    let form_valid = true
    if (!email) {
        form_valid = false
        if (error_text) {
            error_text += '<br>'
        }
        error_text += 'Заполните поле "Электронный адрес"'
        $('#email').addClass('line-input-error')
    }
    if (!form_valid) {
        event.preventDefault()
        $('#errors').html(error_text).fadeIn(200)
    }
})

$('form input').on('click', function (event) {
    $(this).removeClass('line-input-error')
    $('#errors').fadeOut(200, function () {
        $(this).html('')
    })
})
