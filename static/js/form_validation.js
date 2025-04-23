/**
 * Form validation helper functions for Kapil Agro application
 */

// Validate date inputs
function validateDateInputs(formId, dateFields, messages = {}) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    
    // Default messages
    const defaultMessages = {
        required: "This field is required.",
        future: "Date cannot be in the future.",
        order: "This date must be after the previous cutting date.",
        invalid: "Please enter a valid date."
    };
    
    // Merge with custom messages
    const errorMessages = { ...defaultMessages, ...messages };
    
    // Clear previous error messages
    const errorElements = form.querySelectorAll('.date-error');
    errorElements.forEach(el => el.remove());
    
    // Get current date (midnight)
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Check each field
    let previousDate = null;
    let previousFieldName = '';
    
    dateFields.forEach(field => {
        const inputElement = form.querySelector(`[name="${field}"]`);
        if (!inputElement) return;
        
        // Remove invalid class from previous validations
        inputElement.classList.remove('is-invalid');
        
        // Skip if empty and not required
        if (!inputElement.value && !inputElement.required) {
            return;
        }
        
        // Required check
        if (inputElement.required && !inputElement.value) {
            displayError(inputElement, errorMessages.required);
            isValid = false;
            return;
        }
        
        // Valid date check
        const dateValue = new Date(inputElement.value);
        if (isNaN(dateValue.getTime())) {
            displayError(inputElement, errorMessages.invalid);
            isValid = false;
            return;
        }
        
        // Future date check (if applicable)
        if (inputElement.dataset.noFuture === 'true' && dateValue > today) {
            displayError(inputElement, errorMessages.future);
            isValid = false;
            return;
        }
        
        // Sequential date check (if applicable)
        if (previousDate && inputElement.dataset.afterField === previousFieldName && dateValue < previousDate) {
            displayError(inputElement, errorMessages.order);
            isValid = false;
            return;
        }
        
        // Store for next iteration if needed
        previousDate = dateValue;
        previousFieldName = field;
    });
    
    return isValid;
    
    // Helper function to display error
    function displayError(inputElement, message) {
        inputElement.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback date-error';
        errorDiv.textContent = message;
        
        inputElement.parentNode.appendChild(errorDiv);
    }
}

// Validate numeric inputs
function validateNumericInputs(formId, numericFields, messages = {}) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    
    // Default messages
    const defaultMessages = {
        required: "This field is required.",
        positive: "Value must be greater than zero.",
        number: "Please enter a valid number.",
        max: "Value exceeds maximum allowed.",
        min: "Value is below minimum allowed."
    };
    
    // Merge with custom messages
    const errorMessages = { ...defaultMessages, ...messages };
    
    // Clear previous error messages
    const errorElements = form.querySelectorAll('.numeric-error');
    errorElements.forEach(el => el.remove());
    
    // Check each field
    numericFields.forEach(field => {
        const inputElement = form.querySelector(`[name="${field}"]`);
        if (!inputElement) return;
        
        // Remove invalid class from previous validations
        inputElement.classList.remove('is-invalid');
        
        // Skip if empty and not required
        if (!inputElement.value && !inputElement.required) {
            return;
        }
        
        // Required check
        if (inputElement.required && !inputElement.value) {
            displayError(inputElement, errorMessages.required);
            isValid = false;
            return;
        }
        
        // Valid number check
        const numValue = parseFloat(inputElement.value);
        if (isNaN(numValue)) {
            displayError(inputElement, errorMessages.number);
            isValid = false;
            return;
        }
        
        // Positive check (if applicable)
        if (inputElement.dataset.positive === 'true' && numValue <= 0) {
            displayError(inputElement, errorMessages.positive);
            isValid = false;
            return;
        }
        
        // Min value check (if applicable)
        if (inputElement.min && numValue < parseFloat(inputElement.min)) {
            displayError(inputElement, errorMessages.min);
            isValid = false;
            return;
        }
        
        // Max value check (if applicable)
        if (inputElement.max && numValue > parseFloat(inputElement.max)) {
            displayError(inputElement, errorMessages.max);
            isValid = false;
            return;
        }
    });
    
    return isValid;
    
    // Helper function to display error
    function displayError(inputElement, message) {
        inputElement.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback numeric-error';
        errorDiv.textContent = message;
        
        inputElement.parentNode.appendChild(errorDiv);
    }
}

// Validate tray form
function validateTrayForm(formId) {
    const dateFields = ['sowing_date', 'first_cutting_date', 'second_cutting_date', 'third_cutting_date'];
    const numericFields = ['yield_1', 'yield_2', 'yield_3'];
    
    const dateValid = validateDateInputs(formId, dateFields, {
        order: "This cutting date must be after the previous cutting date."
    });
    
    const numericValid = validateNumericInputs(formId, numericFields, {
        positive: "Yield must be greater than zero."
    });
    
    return dateValid && numericValid;
}

// Set up tray form validation
function setupTrayFormValidation() {
    const trayForm = document.getElementById('trayForm');
    if (!trayForm) return;
    
    trayForm.addEventListener('submit', function(event) {
        if (!validateTrayForm('trayForm')) {
            event.preventDefault();
            // Scroll to first error
            const firstError = document.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });
    
    // Set up data attributes for validation
    const sowingDateInput = document.querySelector('[name="sowing_date"]');
    if (sowingDateInput) {
        sowingDateInput.dataset.noFuture = 'true';
    }
    
    const firstCuttingInput = document.querySelector('[name="first_cutting_date"]');
    if (firstCuttingInput) {
        firstCuttingInput.dataset.afterField = 'sowing_date';
    }
    
    const secondCuttingInput = document.querySelector('[name="second_cutting_date"]');
    if (secondCuttingInput) {
        secondCuttingInput.dataset.afterField = 'first_cutting_date';
    }
    
    const thirdCuttingInput = document.querySelector('[name="third_cutting_date"]');
    if (thirdCuttingInput) {
        thirdCuttingInput.dataset.afterField = 'second_cutting_date';
    }
    
    const yieldInputs = document.querySelectorAll('[name^="yield_"]');
    yieldInputs.forEach(input => {
        input.dataset.positive = 'true';
    });
}

// Initialize validation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupTrayFormValidation();
});