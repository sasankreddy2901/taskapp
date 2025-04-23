/**
 * QR Code Scanner utility for Kapil Agro application
 */

class KapilAgroQRScanner {
    constructor(options = {}) {
        // Default options
        this.options = {
            videoElementId: 'qr-video',
            videoContainerId: 'qr-video-container',
            resultContainerId: 'qr-result-container',
            trayNumberElementId: 'qr-tray-number',
            resultStatusElementId: 'qr-result-status',
            continueLinkId: 'continue-link',
            scanAgainButtonId: 'scan-again',
            startCameraButtonId: 'start-camera',
            spinnerElementClass: 'spinner-border',
            apiEndpoint: '/api/check-tray/',
            ...options
        };
        
        // Scanner state
        this.scanning = false;
        this.stream = null;
        
        // Get DOM elements
        this.elements = {
            video: document.getElementById(this.options.videoElementId),
            videoContainer: document.getElementById(this.options.videoContainerId),
            resultContainer: document.getElementById(this.options.resultContainerId),
            trayNumberElement: document.getElementById(this.options.trayNumberElementId),
            resultStatusElement: document.getElementById(this.options.resultStatusElementId),
            continueLink: document.getElementById(this.options.continueLinkId),
            scanAgainButton: document.getElementById(this.options.scanAgainButtonId),
            startCameraButton: document.getElementById(this.options.startCameraButtonId),
            spinner: document.querySelector(`.${this.options.spinnerElementClass}`)
        };
        
        // Initialize if all required elements exist
        if (this.validateElements()) {
            this.init();
        } else {
            console.error('QR Scanner: Missing required elements');
        }
    }
    
    // Validate that all required elements exist
    validateElements() {
        return (
            this.elements.video &&
            this.elements.videoContainer &&
            this.elements.resultContainer &&
            this.elements.trayNumberElement &&
            this.elements.resultStatusElement &&
            this.elements.continueLink &&
            this.elements.scanAgainButton &&
            this.elements.startCameraButton &&
            this.elements.spinner
        );
    }
    
    // Initialize the scanner
    init() {
        // Set up event listeners
        this.elements.startCameraButton.addEventListener('click', () => this.startCamera());
        this.elements.scanAgainButton.addEventListener('click', () => this.scanAgain());
        
        // Clean up when leaving the page
        window.addEventListener('beforeunload', () => this.stopCamera());
    }
    
    // Start the camera
    startCamera() {
        this.elements.spinner.style.display = 'inline-block';
        this.elements.startCameraButton.style.display = 'none';
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: "environment",
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            })
            .then(mediaStream => {
                this.stream = mediaStream;
                this.elements.video.srcObject = mediaStream;
                this.elements.video.setAttribute('playsinline', true);
                this.elements.video.play();
                this.elements.videoContainer.style.display = 'block';
                this.elements.spinner.style.display = 'none';
                
                this.scanning = true;
                requestAnimationFrame(() => this.scanQRCode());
            })
            .catch(error => {
                console.error("Camera error:", error);
                this.elements.spinner.style.display = 'none';
                this.elements.startCameraButton.style.display = 'block';
                
                // Show error message to user
                alert(`Error accessing camera: ${error.message}. Please make sure you've granted camera permissions.`);
            });
        } else {
            alert("Sorry, your browser doesn't support camera access. Please try a different browser.");
            this.elements.spinner.style.display = 'none';
            this.elements.startCameraButton.style.display = 'block';
        }
    }
    
    // Stop the camera
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.scanning = false;
    }
    
    // Scan for QR codes in the video feed
    scanQRCode() {
        if (!this.scanning) return;
        
        if (this.elements.video.readyState === this.elements.video.HAVE_ENOUGH_DATA) {
            const canvas = document.createElement('canvas');
            const canvasContext = canvas.getContext('2d');
            
            canvas.width = this.elements.video.videoWidth;
            canvas.height = this.elements.video.videoHeight;
            canvasContext.drawImage(this.elements.video, 0, 0, canvas.width, canvas.height);
            
            const imageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
            
            // Use jsQR library to detect QR code
            try {
                const code = jsQR(imageData.data, imageData.width, imageData.height, {
                    inversionAttempts: "dontInvert",
                });
                
                if (code) {
                    // Successfully scanned QR code
                    this.scanning = false;
                    this.handleQRCode(code.data);
                }
            } catch (e) {
                console.error("QR scan error:", e);
            }
        }
        
        if (this.scanning) {
            requestAnimationFrame(() => this.scanQRCode());
        }
    }
    
    // Handle scanned QR code data
    handleQRCode(trayNumber) {
        // Display the scanned tray number
        this.elements.trayNumberElement.textContent = trayNumber;
        this.elements.resultContainer.style.display = 'block';
        this.elements.videoContainer.style.display = 'none';
        
        // Check if tray exists in the system
        this.checkTrayExists(trayNumber);
    }
    
    // Check if tray exists in the database
    checkTrayExists(trayNumber) {
        this.elements.resultStatusElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Checking tray...';
        this.elements.resultStatusElement.className = 'alert alert-info';
        
        fetch(`${this.options.apiEndpoint}?tray_number=${encodeURIComponent(trayNumber)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.exists) {
                    // Tray exists - update form
                    this.elements.resultStatusElement.innerHTML = '<i class="fas fa-info-circle me-2"></i> This tray already exists in the system. You can edit its details.';
                    this.elements.resultStatusElement.className = 'alert alert-info';
                    this.elements.continueLink.innerHTML = '<i class="fas fa-edit me-2"></i> Edit Tray Data';
                } else {
                    // New tray - create new entry
                    this.elements.resultStatusElement.innerHTML = '<i class="fas fa-plus-circle me-2"></i> New tray detected. Please enter the details.';
                    this.elements.resultStatusElement.className = 'alert alert-success';
                    this.elements.continueLink.innerHTML = '<i class="fas fa-plus me-2"></i> Add Tray Data';
                }
                this.elements.continueLink.href = data.form_url;
            })
            .catch(error => {
                console.error('Error:', error);
                this.elements.resultStatusElement.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> Error checking tray. Please try again.';
                this.elements.resultStatusElement.className = 'alert alert-danger';
            });
    }
    
    // Scan again after showing result
    scanAgain() {
        this.elements.resultContainer.style.display = 'none';
        this.elements.videoContainer.style.display = 'block';
        this.scanning = true;
        requestAnimationFrame(() => this.scanQRCode());
    }
}

// Initialize the scanner when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the QR scanning page
    if (document.getElementById('qr-video')) {
        // Create a new scanner instance
        window.qrScanner = new KapilAgroQRScanner();
    }
});