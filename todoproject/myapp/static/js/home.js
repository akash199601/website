document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const cartItemsList = document.getElementById('cart-items');
    const checkoutBtn = document.getElementById('checkout-btn');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.parentElement;
            const productName = productCard.querySelector('h3').textContent;
            const productPrice = productCard.querySelector('p').textContent;

            const cartItem = document.createElement('li');
            cartItem.textContent = `${productName} - ${productPrice}`;
            cartItemsList.appendChild(cartItem);
        });
    });


    // Contact Section

const checkbox = document.querySelector('.my-form input[type="checkbox"]');
const btns = document.querySelectorAll(".my-form button");

checkbox.addEventListener("change", function () {
  const checked = this.checked;
  for (const btn of btns) {
    btn.disabled = !checked;
  }
});


    checkoutBtn.addEventListener('click', function() {
        if (cartItemsList.children.length === 0) {
            alert('Your cart is empty!');
            return;
        }

        let totalAmount = 0;
        Array.from(cartItemsList.children).forEach(item => {
            const price = parseFloat(item.textContent.split(' - ')[1].replace('$', '').trim());
            totalAmount += price * 100;
        });

        fetch('/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify({
                cart_items: Array.from(cartItemsList.children).map(item => item.textContent),
                total_amount: totalAmount
            })
        })
        .then(response => response.json())
        .then(order => {
            const options = {
                key: 'rzp_test_A9x6MsabeOqNop',
                amount: order.amount,
                currency: 'INR',
                name: 'My Store',
                description: 'Order payment',
                order_id: order.id,
                handler: function(response) {
                    console.log(response);
                    window.location.href = '/success/';
                },
                prefill: {
                    name: 'John Doe',
                    email: 'john.doe@example.com',
                    contact: '9876543210'
                },
                notes: {
                    address: 'Razorpay Corporate Office'
                },
                theme: {
                    color: '#F37254'
                }
            };

            const rzp1 = new Razorpay(options);
            rzp1.open();
        })
        .catch(error => {
            console.error('Error creating Razorpay order:', error);
        });
    });
});
