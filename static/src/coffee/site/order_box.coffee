$ -> $('html.product').each ->
  $.get '/order/order_box/', (data) -> $('.order_box').html(data)
