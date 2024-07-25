$(document).ready(function() {
    function updateDateTime() {
        var now = new Date();
        var formattedDateTime = now.toLocaleString();
        $('#current-datetime').text(formattedDateTime);
    }
    updateDateTime();
    setInterval(updateDateTime, 1000);
    function updateCart(cart) {
        var cartList = $('#cart-list');
                cartList.empty();  // Clear the existing cart list
                cart.forEach(function(item) {
                    var truncatedName = item.name.length > 30 ? item.name.substring(0, 30) + '...' : item.name;
                    cartList.append(
                        `<li class="cart-item" data-product-id="${item.id}">
                        <span class="cart-item-name" title="${item.name}">${truncatedName}</span>
                        <span class="cart-item-quantity">x${item.quantity}</span>
                        <span class="cart-item-price">&#8369;${item.price.toFixed(2)}</span>
                        <button class="remove-from-cart" data-product-id="${item.id}">VOID</button>
                        </li>`
                        );
                });
                $('#total').text(cart.reduce((total, item) => total + item.price * item.quantity, 0).toFixed(2));
            }
            $('.product-item').click(function() {
                var productId = $(this).data('product-id');
                $.post(`/add_to_cart/${productId}`, function(data) {
                    updateCart(data.cart);
                });
            });
            $(document).on('click', '.remove-from-cart', function() {
                var productId = $(this).data('product-id');
                $.post(`/remove_from_cart/${productId}`, function(data) {
                    updateCart(data.cart);
                });
            });
            $('#process-payment').click(function() {
                var customerId = $('#customer-select').val();
                var paymentAmount = $('#payment-amount').val();
                $.post('/process_payment', {
                    customer_id: customerId,
                    payment_amount: paymentAmount
                }, function(data) {
                    if (data.success) {
                        alert(data.message);
                        updateCart([]);  // Clear the cart display
                        $('#customer-select').val('');
                        $('#payment-amount').val('');
                        var modal = document.getElementById("myModal");
                        modal.style.display = "none";
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
            });
        });
// Get the modal
var modal = document.getElementById("myModal");
// Get the button that opens the modal
var btn = document.getElementById("myBtn");
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
// When the user clicks the button, open the modal 
btn.onclick = function() {
  modal.style.display = "block";
}
// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
}
}