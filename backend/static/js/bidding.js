/* ================================
   MANDI CONNECT - BIDDING JAVASCRIPT
   ================================ */

/**
 * Bidding System Utilities
 * Handles real-time updates, validation, and WebSocket communication
 */

// Global WebSocket instance
let biddingSocket = null;

/**
 * Initialize WebSocket connection for bidding
 */
function initializeBiddingSocket() {
    if (biddingSocket && biddingSocket.connected) {
        return biddingSocket;
    }

    biddingSocket = io();

    biddingSocket.on('connect', () => {
        console.log('✅ Connected to bidding server');
    });

    biddingSocket.on('connect_error', (error) => {
        console.error('❌ WebSocket connection error:', error);
        showNotification('Connection error. Some features may not work.', 'warning');
    });

    biddingSocket.on('disconnect', () => {
        console.log('⚠️ Disconnected from bidding server');
    });

    return biddingSocket;
}

/**
 * Join auction room
 * @param {string} auctionId - Auction ID
 */
function joinAuctionRoom(auctionId) {
    const socket = initializeBiddingSocket();
    
    socket.emit('join_auction', { auction_id: auctionId }, (response) => {
        if (response.success) {
            console.log('✅ Joined auction room:', auctionId);
        } else {
            console.error('❌ Failed to join auction:', response.message);
        }
    });
}

/**
 * Leave auction room
 * @param {string} auctionId - Auction ID
 */
function leaveAuctionRoom(auctionId) {
    const socket = initializeBiddingSocket();
    
    socket.emit('leave_auction', { auction_id: auctionId }, (response) => {
        console.log('Left auction room:', auctionId);
    });
}

/**
 * Place a manual bid
 * @param {string} auctionId - Auction ID
 * @param {number} bidAmount - Bid amount in rupees
 * @returns {Promise}
 */
function placeBidSocket(auctionId, bidAmount) {
    return new Promise((resolve, reject) => {
        const socket = initializeBiddingSocket();
        
        socket.emit('place_bid', {
            auction_id: auctionId,
            bid_amount: bidAmount
        }, (response) => {
            if (response.success) {
                resolve(response);
            } else {
                reject(new Error(response.message || 'Failed to place bid'));
            }
        });
    });
}

/**
 * Setup auto-bidding
 * @param {string} auctionId - Auction ID
 * @param {number} maxBid - Maximum bid amount
 * @param {number} increment - Auto-bid increment
 * @returns {Promise}
 */
function setupAutoBidSocket(auctionId, maxBid, increment) {
    return new Promise((resolve, reject) => {
        const socket = initializeBiddingSocket();
        
        socket.emit('auto_bid', {
            auction_id: auctionId,
            max_bid_amount: maxBid,
            auto_increment: increment
        }, (response) => {
            if (response.success) {
                resolve(response);
            } else {
                reject(new Error(response.message || 'Failed to setup auto-bid'));
            }
        });
    });
}

/**
 * Listen to bid placed event
 * @param {Function} callback - Callback function
 */
function onBidPlaced(callback) {
    const socket = initializeBiddingSocket();
    socket.on('bid_placed', callback);
}

/**
 * Listen to outbid notification
 * @param {Function} callback - Callback function
 */
function onOutbid(callback) {
    const socket = initializeBiddingSocket();
    socket.on('you_were_outbid', callback);
}

/**
 * Listen to auction ended event
 * @param {Function} callback - Callback function
 */
function onAuctionEnded(callback) {
    const socket = initializeBiddingSocket();
    socket.on('auction_ended', callback);
}

/**
 * Fetch base price for a crop
 * @param {string} cropName - Crop name
 * @returns {Promise<number>} - Base price
 */
async function getBasePrice(cropName) {
    try {
        const response = await fetch(`/bidding/get-base-price/${cropName}`);
        const data = await response.json();
        return data.price || 5000;
    } catch (error) {
        console.error('Error fetching base price:', error);
        return 5000; // Default fallback
    }
}

/**
 * Fetch all crop prices
 * @returns {Promise<Object>} - Object with crop prices
 */
async function getAllCropPrices() {
    try {
        const response = await fetch('/bidding/crop-prices');
        const data = await response.json();
        return data.prices || {};
    } catch (error) {
        console.error('Error fetching crop prices:', error);
        return {};
    }
}

/**
 * Format currency value
 * @param {number} amount - Amount in rupees
 * @returns {string} - Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Format large number
 * @param {number} num - Number
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Format date/time
 * @param {string|Date} dateString - Date string or Date object
 * @param {boolean} includeTime - Include time in output
 * @returns {string} - Formatted date
 */
function formatDate(dateString, includeTime = true) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleString('en-IN', options);
}

/**
 * Get time remaining until end time
 * @param {string|Date} endTime - End time
 * @returns {string} - Readable time remaining
 */
function getTimeRemaining(endTime) {
    const now = new Date();
    const end = new Date(endTime);
    const diff = end - now;

    if (diff <= 0) return 'Ended';
    
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff % 86400000) / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    if (days > 0) {
        return `${days}d ${hours}h`;
    } else if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds}s`;
    } else {
        return `${seconds}s`;
    }
}

/**
 * Show notification toast
 * @param {string} message - Message text
 * @param {string} type - Type: success, error, warning, info
 * @param {number} duration - Duration in ms (default: 5000)
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notif = document.createElement('div');
    notif.className = `notification notification-${type}`;
    notif.textContent = message;
    notif.style.zIndex = '9999';
    document.body.appendChild(notif);

    setTimeout(() => {
        notif.style.opacity = '0';
        notif.style.transform = 'translateX(400px)';
        setTimeout(() => notif.remove(), 300);
    }, duration);
}

/**
 * Show modal dialog
 * @param {string} title - Modal title
 * @param {string} message - Modal message
 * @param {string} confirmText - Confirm button text
 * @param {Function} onConfirm - Callback on confirm
 */
function showConfirmDialog(title, message, confirmText = 'Confirm', onConfirm = null) {
    const modal = document.createElement('div');
    modal.className = 'confirm-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <h3>${title}</h3>
                <p>${message}</p>
                <div class="modal-buttons">
                    <button class="btn-secondary" onclick="this.closest('.confirm-modal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="this.closest('.confirm-modal').remove(); window.confirmCallback();">
                        ${confirmText}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    window.confirmCallback = onConfirm || (() => {});
    document.body.appendChild(modal);
}

/**
 * Validate bid amount
 * @param {number} bidAmount - Bid amount
 * @param {number} currentHighestBid - Current highest bid
 * @param {number} minBid - Minimum bid
 * @returns {Object} - { isValid: boolean, message: string }
 */
function validateBid(bidAmount, currentHighestBid, minBid) {
    bidAmount = parseInt(bidAmount) || 0;

    if (isNaN(bidAmount) || bidAmount < 0) {
        return {
            isValid: false,
            message: 'Bid amount must be a valid number'
        };
    }

    if (bidAmount < minBid) {
        return {
            isValid: false,
            message: `Bid must be at least ₹${formatNumber(minBid)}`
        };
    }

    if (bidAmount <= currentHighestBid) {
        return {
            isValid: false,
            message: `Bid must exceed current highest bid (₹${formatNumber(currentHighestBid)})`
        };
    }

    return {
        isValid: true,
        message: 'Valid bid amount'
    };
}

/**
 * Validate quantity input
 * @param {number} quantity - Quantity
 * @returns {Object} - { isValid: boolean, message: string }
 */
function validateQuantity(quantity) {
    quantity = parseInt(quantity) || 0;

    if (isNaN(quantity) || quantity < 1) {
        return {
            isValid: false,
            message: 'Quantity must be at least 1'
        };
    }

    if (quantity > 10000) {
        return {
            isValid: false,
            message: 'Quantity cannot exceed 10000'
        };
    }

    return {
        isValid: true,
        message: 'Valid quantity'
    };
}

/**
 * Debounce function for API calls
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in ms
 * @returns {Function} - Debounced function
 */
function debounce(func, delay = 500) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} delay - Delay in ms
 * @returns {Function} - Throttled function
 */
function throttle(func, delay = 500) {
    let lastCall = 0;
    return function (...args) {
        const now = Date.now();
        if (now - lastCall >= delay) {
            func(...args);
            lastCall = now;
        }
    };
}

/**
 * Start auction timer update
 * @param {string} auctionId - Auction ID
 * @param {Function} onUpdate - Callback with time remaining
 * @param {number} interval - Update interval in ms
 * @returns {Function} - Stop function
 */
function startAuctionTimer(auctionId, onUpdate, interval = 1000) {
    const timerInterval = setInterval(() => {
        fetch(`/bidding/auction/${auctionId}/live-updates`)
            .then(res => res.json())
            .then(data => {
                onUpdate(data.time_remaining || 0);
            })
            .catch(err => console.error('Timer update error:', err));
    }, interval);

    return () => clearInterval(timerInterval);
}

/**
 * Get user auction history
 * @returns {Promise<Array>} - Array of auction objects
 */
async function getUserAuctionHistory() {
    try {
        const response = await fetch('/bidding/farmer/my-auctions');
        const data = await response.json();
        return data.auctions || [];
    } catch (error) {
        console.error('Error fetching auction history:', error);
        return [];
    }
}

/**
 * Get user bid history
 * @returns {Promise<Array>} - Array of bid objects
 */
async function getUserBidHistory() {
    try {
        const response = await fetch('/bidding/buyer/my-bids');
        const data = await response.json();
        return data.bids || [];
    } catch (error) {
        console.error('Error fetching bid history:', error);
        return [];
    }
}

/**
 * Get auction statistics
 * @returns {Promise<Object>} - Statistics object
 */
async function getAuctionStats() {
    try {
        const response = await fetch('/bidding/stats');
        const data = await response.json();
        return data.stats || {};
    } catch (error) {
        console.error('Error fetching stats:', error);
        return {};
    }
}

/**
 * Export data as CSV
 * @param {Array} data - Array of objects
 * @param {string} filename - Output filename
 */
function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        showNotification('No data to export', 'warning');
        return;
    }

    const headers = Object.keys(data[0]);
    const csv = [
        headers.join(','),
        ...data.map(obj => 
            headers.map(header => {
                const value = obj[header];
                return typeof value === 'string' && value.includes(',') 
                    ? `"${value}"` 
                    : value;
            }).join(',')
        )
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Print document
 * @param {string} elementId - ID of element to print
 */
function printDocument(elementId) {
    const printWindow = window.open('', '', 'height=400,width=800');
    const element = document.getElementById(elementId);
    
    if (!element) {
        showNotification('Element not found', 'error');
        return;
    }

    printWindow.document.write(element.innerHTML);
    printWindow.document.close();
    printWindow.print();
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>}
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('✅ Copied to clipboard', 'success');
        return true;
    } catch (error) {
        console.error('Copy failed:', error);
        showNotification('❌ Failed to copy', 'error');
        return false;
    }
}

/**
 * Highlight search text
 * @param {string} text - Text to search
 * @param {string} searchTerm - Search term
 * @returns {string} - HTML with highlights
 */
function highlightText(text, searchTerm) {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

/**
 * API error handler
 * @param {Error} error - Error object
 * @returns {string} - User-friendly error message
 */
function handleApiError(error) {
    if (error.response?.status === 401) {
        return 'Please log in to continue';
    } else if (error.response?.status === 403) {
        return 'You do not have permission to perform this action';
    } else if (error.response?.status === 404) {
        return 'Resource not found';
    } else if (error.response?.status === 500) {
        return 'Server error. Please try again later';
    } else if (error.message === 'Network Error') {
        return 'Network connection error';
    } else {
        return error.message || 'An error occurred. Please try again';
    }
}

/**
 * Session timeout handler
 * @param {number} timeout - Timeout in ms
 */
function setupSessionTimeout(timeout = 1800000) { // 30 minutes default
    let timeoutId;
    
    const resetTimer = () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            showNotification('⚠️ Your session has expired. Please log in again.', 'warning');
            window.location.href = '/login';
        }, timeout);
    };

    document.addEventListener('click', resetTimer);
    document.addEventListener('keypress', resetTimer);
    
    resetTimer();
}

// Export functions for use in other modules
window.biddingUtils = {
    initializeBiddingSocket,
    joinAuctionRoom,
    leaveAuctionRoom,
    placeBidSocket,
    setupAutoBidSocket,
    onBidPlaced,
    onOutbid,
    onAuctionEnded,
    getBasePrice,
    getAllCropPrices,
    formatCurrency,
    formatNumber,
    formatDate,
    getTimeRemaining,
    showNotification,
    showConfirmDialog,
    validateBid,
    validateQuantity,
    debounce,
    throttle,
    startAuctionTimer,
    getUserAuctionHistory,
    getUserBidHistory,
    getAuctionStats,
    exportToCSV,
    printDocument,
    copyToClipboard,
    highlightText,
    handleApiError,
    setupSessionTimeout
};

console.log('✅ Bidding utilities loaded');
