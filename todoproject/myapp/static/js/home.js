
document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const cartItemsList = document.getElementById('cart-items');
    const checkoutBtn = document.getElementById('checkout-btn'); // Ensure this ID is correct

    // Function to handle adding items to cart
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

    // Handle checkout
    checkoutBtn.addEventListener('click', function() {
        if (cartItemsList.children.length === 0) {
            alert('Your cart is empty!');
        } else {
            alert('Proceeding to checkout...');

            // Calculate the total amount (in paise)
            let totalAmount = 0;
            Array.from(cartItemsList.children).forEach(item => {
                const price = parseFloat(item.textContent.split(' - ')[1].replace('₹', '').trim());
                totalAmount += price * 100; // Converting to paise
            });

            // Make an AJAX call to the Django view to create an order
            fetch('/checkout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    cart_items: Array.from(cartItemsList.children).map(item => item.textContent),
                    total_amount: totalAmount // Send the total amount
                })
            })
            .then(response => response.json())
            .then(order => {
                var options = {
                    key: 'rzp_test_A9x6MsabeOqNop', // Your Razorpay Key ID
                    amount: order.amount, // Amount in paise (sent from server)
                    currency: 'INR',
                    name: 'My Store',
                    description: 'Order payment',
                    order_id: order.id, // Razorpay order ID from the server
                    handler: function (response) {
                        // On successful payment
                        console.log(response);
                        window.location.href = '/success/'; // Redirect to success page
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

                var rzp1 = new Razorpay(options);
                rzp1.open();
            })
            .catch(error => console.error('Error creating Razorpay order:', error));
        }
    });
});
