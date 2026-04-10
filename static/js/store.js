/* TrendVault Store JavaScript */

function addToCart(productId, quantity = 1) {
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            qty: quantity,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(`Added to cart! (${data.cart_count} items)`);
                updateCartBadge(data.cart_count);
            } else {
                showToast('Error adding to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error adding to cart', 'error');
        });
}

function updateCart(productId, quantity) {
    fetch('/api/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            qty: quantity,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showToast('Error updating cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating cart', 'error');
        });
}

function removeFromCart(productId) {
    if (confirm('Are you sure you want to remove this item?')) {
        fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    showToast('Error removing item', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error removing item', 'error');
            });
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast show`;

    if (type === 'error') {
        toast.style.borderColor = '#ef4444';
        toast.style.color = '#ef4444';
    } else {
        toast.style.borderColor = '#7c3aed';
        toast.style.color = '#7c3aed';
    }

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
    } else if (count > 0) {
        const cartLink = document.querySelector('.cart-link');
        if (cartLink) {
            const newBadge = document.createElement('span');
            newBadge.className = 'cart-badge';
            newBadge.textContent = count;
            cartLink.appendChild(newBadge);
        }
    }
}

// Initialize page interactions
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Add animation to product cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.product-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        observer.observe(card);
    });
});

// Auto-hide toast after certain time
window.addEventListener('load', function() {
    const toast = document.getElementById('toast');
    if (toast && toast.classList.contains('show')) {
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});
