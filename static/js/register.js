$('form').on('submit', function (event) {
    let login = $('#login').val()
    let password = $('#password').val()
    let password2 = $('#password2').val()
    let error_text = ''
    let form_valid = true
    if (!login) {
        form_valid = false
        if (error_text) {
            error_text += '<br>'
        }
        error_text += 'Заполните поле "Логин"'
        $('#login').addClass('line-input-error')
    }
    if (!password) {
        form_valid = false
        if (error_text) {
            error_text += '<br>'
        }
        error_text += 'Заполните поле "Пароль"'
        $('#password').addClass('line-input-error')
    }
    if (!password2) {
        form_valid = false
        if (error_text) {
            error_text += '<br>'
        }
        error_text += 'Заполните поле "Повторите пароль"'
        $('#password2').addClass('line-input-error')
    }
    if (password !== password2) {
        form_valid = false
        if (error_text) {
            error_text += '<br>'
        }
        error_text += 'Пароли не совпадают'
        $('#password2').addClass('line-input-error')
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
