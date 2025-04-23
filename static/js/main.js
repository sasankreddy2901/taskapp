/**
 * Main JavaScript file for Kapil Agro application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 3 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 3000);
    });
    
    // Enable tooltips everywhere
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Table row highlighting
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicked on a button or link
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a') || e.target.closest('button')) {
                return;
            }
            
            // Get the first link in the row and click it
            const firstLink = this.querySelector('a');
            if (firstLink) {
                firstLink.click();
            }
        });
    });
    
    // Mobile navigation handling - COMPLETELY REWRITTEN
    function setupMobileNavigation() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const dropdownToggle = document.querySelector('#userDropdown');
        
        if (!navbarToggler || !navbarCollapse) return;
        
        // Get all regular nav links (not dropdowns)
        const regularNavLinks = document.querySelectorAll('.navbar-nav .nav-link:not([data-bs-toggle="dropdown"])');
        
        // Create Bootstrap collapse instance
        const bsCollapse = new bootstrap.Collapse(navbarCollapse, { toggle: false });
        
        // Close navbar when regular links are clicked
        regularNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 768 && navbarCollapse.classList.contains('show')) {
                    bsCollapse.hide();
                }
            });
        });
        
        // Fix dropdown functionality in mobile view
        if (dropdownToggle) {
            // We need to manually track dropdown state to fix the toggle behavior
            let dropdownOpen = false;
            
            dropdownToggle.addEventListener('click', function(e) {
                if (window.innerWidth < 768) {
                    // Prevent event from causing navbar collapse
                    e.stopPropagation();
                    
                    // Get the associated dropdown menu
                    const dropdownMenu = document.querySelector('.dropdown-menu[aria-labelledby="userDropdown"]');
                    if (!dropdownMenu) return;
                    
                    // Toggle dropdown menu manually
                    if (dropdownOpen) {
                        dropdownMenu.classList.remove('show');
                        dropdownToggle.setAttribute('aria-expanded', 'false');
                        dropdownOpen = false;
                    } else {
                        dropdownMenu.classList.add('show');
                        dropdownToggle.setAttribute('aria-expanded', 'true');
                        dropdownOpen = true;
                    }
                    
                    // Prevent Bootstrap's default dropdown behavior
                    e.preventDefault();
                }
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (window.innerWidth < 768 && dropdownOpen) {
                    const dropdownMenu = document.querySelector('.dropdown-menu[aria-labelledby="userDropdown"]');
                    
                    // If click is outside dropdown toggle and dropdown menu
                    if (!dropdownToggle.contains(e.target) && 
                        dropdownMenu && !dropdownMenu.contains(e.target)) {
                        dropdownMenu.classList.remove('show');
                        dropdownToggle.setAttribute('aria-expanded', 'false');
                        dropdownOpen = false;
                    }
                }
            });
            
            // Ensure dropdown menu closes when navbar collapses
            navbarCollapse.addEventListener('hide.bs.collapse', function() {
                if (dropdownOpen) {
                    const dropdownMenu = document.querySelector('.dropdown-menu[aria-labelledby="userDropdown"]');
                    if (dropdownMenu) {
                        dropdownMenu.classList.remove('show');
                        dropdownToggle.setAttribute('aria-expanded', 'false');
                        dropdownOpen = false;
                    }
                }
            });
        }
        
        // Handle window resize events
        window.addEventListener('resize', function() {
            // Reset dropdown state when switching between mobile and desktop
            if (window.innerWidth >= 768) {
                // Reset any manual dropdown state if we switch to desktop
                const dropdownMenu = document.querySelector('.dropdown-menu[aria-labelledby="userDropdown"]');
                if (dropdownMenu && dropdownMenu.classList.contains('show') && 
                    !dropdownToggle.getAttribute('aria-expanded') === 'true') {
                    dropdownMenu.classList.remove('show');
                }
            }
        });
    }
    
    // Initialize mobile navigation
    setupMobileNavigation();
    
    // Add form dirty check to prevent accidental navigation away from unsaved forms
    const forms = document.querySelectorAll('form:not(.no-dirty-check)');
    forms.forEach(form => {
        let formIsDirty = false;
        
        // Mark form as dirty when any input changes
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                formIsDirty = true;
            });
            
            input.addEventListener('keyup', () => {
                formIsDirty = true;
            });
        });
        
        // Reset dirty flag on submit
        form.addEventListener('submit', () => {
            formIsDirty = false;
        });
        
        // Check before navigating away
        window.addEventListener('beforeunload', (e) => {
            if (formIsDirty) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    });
    
    // Format date inputs to locale format for display
    const dateDisplayElements = document.querySelectorAll('.date-display');
    dateDisplayElements.forEach(element => {
        const rawDate = element.getAttribute('data-date');
        if (rawDate) {
            const date = new Date(rawDate);
            if (!isNaN(date.getTime())) {
                element.textContent = date.toLocaleDateString();
            }
        }
    });
    
    // Enhance form validation feedback
    const enhancedForms = document.querySelectorAll('form.enhanced-validation');
    enhancedForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            this.classList.add('was-validated');
            
            // Focus on the first invalid field
            const invalidField = this.querySelector(':invalid');
            if (invalidField) {
                invalidField.focus();
            }
        });
    });
    
    // Dynamic table sorting
    document.querySelectorAll('th.sortable').forEach(headerCell => {
        headerCell.addEventListener('click', () => {
            const tableElement = headerCell.closest('table');
            const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
            const currentIsAscending = headerCell.classList.contains('th-sort-asc');
            
            // Remove sort classes from all headers
            tableElement.querySelectorAll('th').forEach(th => {
                th.classList.remove('th-sort-asc', 'th-sort-desc');
            });
            
            // Set the appropriate sort class
            headerCell.classList.toggle('th-sort-asc', !currentIsAscending);
            headerCell.classList.toggle('th-sort-desc', currentIsAscending);
            
            // Get and sort the rows
            const tableBody = tableElement.querySelector('tbody');
            const rows = Array.from(tableBody.querySelectorAll('tr'));
            
            // Sort the rows
            const sortedRows = rows.sort((a, b) => {
                const aColText = a.querySelector(`td:nth-child(${headerIndex + 1})`).textContent.trim();
                const bColText = b.querySelector(`td:nth-child(${headerIndex + 1})`).textContent.trim();
                
                return currentIsAscending
                    ? aColText.localeCompare(bColText)
                    : bColText.localeCompare(aColText);
            });
            
            // Remove all existing rows
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }
            
            // Re-add the newly sorted rows
            tableBody.append(...sortedRows);
        });
    });
    
    // Handle confirmation dialogs
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});