$('.service').each(function (e) {
    setTimeout(() => {
        $(this).children('.spinner-border').fadeIn(100)
    }, e*2000);
    setTimeout(() => {
        $(this).children('.spinner-border').hide(0)
        $(this).addClass('service-complete')
        console.log($('.service').length === (e + 1), $('.service').length, (e - 1))
        if ($('.service').length === (e + 1)) {
            $('#status-text').text('Готово!')
            $('#to-profile').fadeIn(200)
        }
    }, (e+1)*2000);
})