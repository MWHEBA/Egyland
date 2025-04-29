/**
 * Seasonality management JavaScript
 * This file handles all functionality for seasonality management in the dashboard
 */

document.addEventListener('DOMContentLoaded', function () {
    // Toggle modals
    const addBtn = document.getElementById('addSeasonalityBtn');
    const addFirstBtn = document.getElementById('addFirstSeasonalityBtn');
    const addModal = document.getElementById('addSeasonalityModal');
    const editModal = document.getElementById('editSeasonalityModal');
    const deleteModal = document.getElementById('deleteSeasonalityModal');
    const closeBtns = document.querySelectorAll('.closeModal');

    // Product and variety dropdowns for add modal
    const productSelect = document.getElementById('id_product');
    const varietySelect = document.getElementById('id_variety');

    // Product and variety dropdowns for edit modal
    const editProductSelect = document.getElementById('edit_product');
    const editVarietySelect = document.getElementById('edit_variety');

    // Show Add modal
    if (addBtn) {
        addBtn.addEventListener('click', function () {
            addModal.classList.remove('hidden');
        });
    }

    // Add first button (when no items exist)
    if (addFirstBtn) {
        addFirstBtn.addEventListener('click', function () {
            addModal.classList.remove('hidden');
        });
    }

    // Close all modals
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            addModal.classList.add('hidden');
            editModal.classList.add('hidden');
            deleteModal.classList.add('hidden');
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function (e) {
        if (e.target === addModal) {
            addModal.classList.add('hidden');
        }
        if (e.target === editModal) {
            editModal.classList.add('hidden');
        }
        if (e.target === deleteModal) {
            deleteModal.classList.add('hidden');
        }
    });

    // Handle mutual exclusivity between product and variety in add modal
    if (productSelect && varietySelect) {
        productSelect.addEventListener('change', function () {
            if (this.value) {
                varietySelect.value = '';
            }
        });

        varietySelect.addEventListener('change', function () {
            if (this.value) {
                productSelect.value = '';
            }
        });
    }

    // Handle mutual exclusivity between product and variety in edit modal
    if (editProductSelect && editVarietySelect) {
        editProductSelect.addEventListener('change', function () {
            if (this.value) {
                editVarietySelect.value = '';
            }
        });

        editVarietySelect.addEventListener('change', function () {
            if (this.value) {
                editProductSelect.value = '';
            }
        });
    }

    // Add form submission with AJAX
    const addForm = document.getElementById('addSeasonalityForm');
    if (addForm) {
        addForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);

            // Check for existing seasonality before submission
            const selectedProduct = document.getElementById('id_product').value;
            const selectedVariety = document.getElementById('id_variety').value;
            const selectedType = document.getElementById('id_type').value;

            // التحقق من وجود تكرار باستخدام الدالة المعرفة في ملف HTML
            if (window.seasonalityDuplicateCheck && typeof window.seasonalityDuplicateCheck === 'function') {
                const isDuplicate = window.seasonalityDuplicateCheck(selectedProduct, selectedVariety, selectedType);
                if (isDuplicate) {
                    toastr.error('You cannot add the same seasonality twice.');
                    return; // Stop form submission if duplicate found
                }
            }

            // Send AJAX request
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    if (response.redirected) {
                        // On success redirect to the same page to refresh data
                        window.location.href = window.location.href;
                        return;
                    }
                    if (response.ok) {
                        // Hide modal on success
                        addModal.classList.add('hidden');
                        // Show success message with toastr
                        toastr.success('Seasonality created successfully!');
                        // Refresh the page after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                        return;
                    }
                    return response.text();
                })
                .then(html => {
                    if (html) {
                        // If error, we get the form with errors back
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const errors = doc.querySelectorAll('.text-red-600');
                        let errorMsg = 'Please correct the following errors:';
                        errors.forEach(error => {
                            errorMsg += ' ' + error.textContent;
                        });
                        toastr.error(errorMsg);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    toastr.error('Failed to create seasonality. Please try again.');
                });
        });
    }

    // Edit form submission with AJAX
    const editForm = document.getElementById('editSeasonalityForm');
    if (editForm) {
        editForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);

            // Send AJAX request
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    if (response.redirected) {
                        // On success redirect to the same page to refresh data
                        window.location.href = window.location.href;
                        return;
                    }
                    if (response.ok) {
                        // Hide modal on success
                        editModal.classList.add('hidden');
                        // Show success message with toastr
                        toastr.success('Seasonality updated successfully!');
                        // Refresh the page after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                        return;
                    }
                    return response.text();
                })
                .then(html => {
                    if (html) {
                        // If error, show with toastr
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const errors = doc.querySelectorAll('.text-red-600');
                        let errorMsg = 'Please correct the following errors:';
                        errors.forEach(error => {
                            errorMsg += ' ' + error.textContent;
                        });
                        toastr.error(errorMsg);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    toastr.error('Failed to update seasonality. Please try again.');
                });
        });
    }

    // Set up delete links
    document.querySelectorAll('.delete-seasonality').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const name = this.getAttribute('data-name');
            const type = this.getAttribute('data-type');

            document.getElementById('deleteConfirmText').textContent =
                `Are you sure you want to delete the seasonality information for "${name}" (${type})? This action cannot be undone.`;

            const deleteForm = document.getElementById('deleteSeasonalityForm');
            deleteForm.action = url;

            // Copy the seasonality chart data if needed
            if (this.getAttribute('data-chart-id')) {
                const chartId = this.getAttribute('data-chart-id');
                const chartSource = document.getElementById(chartId);
                if (chartSource) {
                    // Instead of copying the chart, we'll create a new one with checkmarks below the months
                    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    const monthValues = [];

                    // Collect month values from source chart
                    const sourceRow = chartSource.querySelector('tbody tr');
                    if (sourceRow) {
                        const cells = sourceRow.querySelectorAll('td');
                        cells.forEach(cell => {
                            // Check if cell contains a checkmark
                            const hasCheck = cell.querySelector('.fa-check') !== null;
                            monthValues.push(hasCheck);
                        });
                    }

                    // Create new chart with checkmarks below months
                    let html = `
                    <div class="py-2 rounded bg-white">
                        <div class="flex justify-between items-center px-2">
                            ${monthNames.map(month => `<div class="text-center text-xs font-medium text-gray-700">${month}</div>`).join('')}
                        </div>
                        <div class="flex justify-between items-center px-2 mt-1">
                            ${monthValues.map(isActive =>
                        isActive
                            ? `<div class="text-center"><i class="fas fa-check text-green-600"></i></div>`
                            : `<div class="text-center"><i class="fas fa-times text-gray-300"></i></div>`
                    ).join('')}
                        </div>
                    </div>`;

                    document.getElementById('deleteSeasionalityChart').innerHTML = html;
                }
            }

            // Show modal
            deleteModal.classList.remove('hidden');
        });
    });

    // Delete form submission with AJAX
    const deleteForm = document.getElementById('deleteSeasonalityForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Send AJAX request
            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    if (response.redirected || response.ok) {
                        // Hide modal on success
                        deleteModal.classList.add('hidden');
                        // Show success message with toastr
                        toastr.success('Seasonality deleted successfully!');
                        // Refresh the page after a short delay
                        setTimeout(() => {
                            window.location.href = window.location.href;
                        }, 1000);
                        return;
                    }
                    return response.text();
                })
                .then(html => {
                    if (html) {
                        toastr.error('Failed to delete seasonality. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    toastr.error('Failed to delete seasonality. Please try again.');
                });
        });
    }

    // Make month table cells clickable in add form
    const addMonthCells = document.querySelectorAll('#addSeasonalityForm .month-cell');
    addMonthCells.forEach(cell => {
        cell.addEventListener('click', function (e) {
            // Don't trigger if clicking directly on checkbox
            if (e.target.type !== 'checkbox') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;

                // Add background color for checked cells
                if (checkbox.checked) {
                    this.classList.add('bg-green-100');
                } else {
                    this.classList.remove('bg-green-100');
                }
            }
        });

        // Initialize background color
        const checkbox = cell.querySelector('input[type="checkbox"]');
        if (checkbox.checked) {
            cell.classList.add('bg-green-100');
        }

        // Update background when checkbox changes
        cell.querySelector('input[type="checkbox"]').addEventListener('change', function () {
            if (this.checked) {
                cell.classList.add('bg-green-100');
            } else {
                cell.classList.remove('bg-green-100');
            }
        });
    });

    // Same for edit form
    const editMonthCells = document.querySelectorAll('#editSeasonalityForm .month-cell');
    editMonthCells.forEach(cell => {
        cell.addEventListener('click', function (e) {
            // Don't trigger if clicking directly on checkbox
            if (e.target.type !== 'checkbox') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;

                // Add background color for checked cells
                if (checkbox.checked) {
                    this.classList.add('bg-green-100');
                } else {
                    this.classList.remove('bg-green-100');
                }
            }
        });

        // Update background when checkbox changes
        cell.querySelector('input[type="checkbox"]').addEventListener('change', function () {
            if (this.checked) {
                cell.classList.add('bg-green-100');
            } else {
                cell.classList.remove('bg-green-100');
            }
        });
    });

    // Additional code to update the background color when loading data in edit form
    const updateEditMonthCellBackgrounds = () => {
        editMonthCells.forEach(cell => {
            const checkbox = cell.querySelector('input[type="checkbox"]');
            if (checkbox.checked) {
                cell.classList.add('bg-green-100');
            } else {
                cell.classList.remove('bg-green-100');
            }
        });
    };

    // Fetch seasonality data for edit modal
    document.querySelectorAll('.edit-seasonality').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.getAttribute('data-url') + '?format=json';

            // Fetch the data via AJAX
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    // Populate the edit form with the fetched data
                    document.getElementById('editSeasonalityForm').action = url.split('?')[0];

                    // Set product/variety
                    document.getElementById('edit_product').value = data.product_id || '';
                    document.getElementById('edit_variety').value = data.variety_id || '';
                    document.getElementById('edit_type').value = data.type;

                    // Set month checkboxes
                    document.getElementById('edit_jan').checked = data.jan;
                    document.getElementById('edit_feb').checked = data.feb;
                    document.getElementById('edit_mar').checked = data.mar;
                    document.getElementById('edit_apr').checked = data.apr;
                    document.getElementById('edit_may').checked = data.may;
                    document.getElementById('edit_jun').checked = data.jun;
                    document.getElementById('edit_jul').checked = data.jul;
                    document.getElementById('edit_aug').checked = data.aug;
                    document.getElementById('edit_sep').checked = data.sep;
                    document.getElementById('edit_oct').checked = data.oct;
                    document.getElementById('edit_nov').checked = data.nov;
                    document.getElementById('edit_dec').checked = data.dec;

                    // Update the styling for month cells
                    updateEditMonthCellBackgrounds();

                    // Show modal
                    editModal.classList.remove('hidden');
                })
                .catch(error => {
                    console.error('Error fetching seasonality data:', error);
                    toastr.error('Error loading seasonality data. Please try again.');
                });
        });
    });
}); 