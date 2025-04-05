document.addEventListener('DOMContentLoaded', function() {
    // Only keep the edit/remove toggle functionality
    const editBtn = document.getElementById('edit-order-btn');
    if (editBtn) {
        editBtn.addEventListener('click', function() {
            const isEditing = this.textContent === 'Done Editing';
            const removeButtons = document.querySelectorAll('.cart-item-actions');

            removeButtons.forEach(btn => {
                btn.style.display = isEditing ? 'none' : 'block';
            });
            this.textContent = isEditing ? 'Edit Order' : 'Done Editing';
        });
    }

    // Initialize - hide all remove buttons on load
    document.querySelectorAll('.cart-item-actions').forEach(btn => {
        btn.style.display = 'none';
    });
});