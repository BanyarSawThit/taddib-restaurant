document.addEventListener('DOMContentLoaded', function() {
    const editBtn = document.getElementById('edit-order-btn');
    if (editBtn) {
        const editIcon = editBtn.querySelector('.edit-icon'); // Target the SVG icon
        let textSpan = editBtn.querySelector('.edit-btn-text');

        // Clean up duplicate text nodes (if any)
        const existingTextNodes = Array.from(editBtn.childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== '');
        existingTextNodes.forEach(node => node.remove());

        // Create span if it doesn't exist
        if (!textSpan) {
            textSpan = document.createElement('span');
            textSpan.className = 'edit-btn-text';
            textSpan.textContent = 'Edit Order';
            editBtn.appendChild(textSpan);
        }

        editBtn.addEventListener('click', function() {
            const isEditing = textSpan.textContent === 'Done Editing';

            // Toggle remove buttons
            document.querySelectorAll('.cart-item-actions').forEach(btn => {
                btn.style.display = isEditing ? 'none' : 'block';
            });

            // Update button text
            textSpan.textContent = isEditing ? 'Edit Order' : 'Done Editing';

            // Toggle icon visibility
            editIcon.style.display = isEditing ? 'inline-block' : 'none';
        });
    }

    // Hide remove buttons initially
    document.querySelectorAll('.cart-item-actions').forEach(btn => {
        btn.style.display = 'none';
    });
});