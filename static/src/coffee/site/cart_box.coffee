$ ->
  $.get '/order/cart_box/', (data) -> $('.cart_box').html(data)