/**
 * Weather AI Recommendation System - Frontend Logic
 * Handles loading, displaying, and interacting with AI-powered weather recommendations
 */

class WeatherAIManager {
    constructor() {
        this.farmerName = '';
        this.currentRecommendations = null;
        this.weatherForecast = null;
        this.cacheExpiresAt = null;
        this.chatContext = [];
        this.isLoadingChat = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.loadRecommendations();
    }

    initializeElements() {
        // Main elements
        this.locationText = document.getElementById('locationText');
        this.farmerNameEl = document.getElementById('farmerName');
        this.recommendationsSection = document.getElementById('recommendationsSection');
        this.forecastCards = document.getElementById('forecastCards');
        this.currentWeatherMini = document.getElementById('currentWeatherMini');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.toggleForecast = document.getElementById('toggleForecast');

        // Chat elements
        this.chatWidget = document.getElementById('chatWidget');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMinimize = document.getElementById('chatMinimize');
        this.chatToggle = document.getElementById('chatToggle');
    }

    attachEventListeners() {
        this.refreshBtn?.addEventListener('click', () => this.handleRefresh());
        this.sendBtn?.addEventListener('click', () => this.handleSendMessage());
        this.chatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        this.chatMinimize?.addEventListener('click', () => this.minimizeChat());
        this.chatToggle?.addEventListener('click', () => this.maximizeChat());
        this.toggleForecast?.addEventListener('click', () => this.toggleForecastVisibility());
        
        // Add click listeners to recommendation cards
        document.addEventListener('click', (e) => {
            const card = e.target.closest('.recommendation-card');
            if (card) {
                const detailType = card.dataset.detailType;
                if (detailType) {
                    e.preventDefault();
                    window.location.href = `/weather/details/${detailType}`;
                }
            }
        });
    }

    /**
     * Load recommendations from API
     */
    async loadRecommendations() {
        try {
            this.showLoading('recommendationsSection', 'AI सिफारिशें जेनरेट हो रही हैं...');
            const response = await fetch('/weather/api/recommendations', {
                method: 'GET',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.currentRecommendations = data.recommendations;
                this.weatherForecast = data.weather_data;
                this.cacheExpiresAt = new Date(data.expires_at);
                
                // Store recommendations in sessionStorage for detail page
                sessionStorage.setItem('recommendations', JSON.stringify(data.recommendations));
                
                this.renderRecommendations();
                this.renderForecast();
                this.updateCurrentWeather();
            } else {
                this.showError('recommendationsSection', data.error || 'सिफारिशें लोड नहीं कर सके');
            }
        } catch (error) {
            console.error('Error loading recommendations:', error);
            this.showError('recommendationsSection', 'सिफारिशें लोड करने में विफल: ' + error.message);
        }
    }

    renderRecommendations() {
        if (!this.currentRecommendations) return;

        const recs = this.currentRecommendations;
        let html = '';

        // Critical Alerts (show first with high priority)
        if (recs.critical_alerts && recs.critical_alerts.length > 0) {
            recs.critical_alerts.forEach(alert => {
                const alertType = alert.type || alert.hindi_summary || 'चेतावनी';
                const alertSummary = alert.hindi_summary || alert.summary || alertType;
                html += `<div class="recommendation-card rec-critical" style="grid-column: 1/-1;">
                    <div class="rec-header">
                        <h3 class="rec-title">🚨 ${alertType}</h3>
                        <span class="severity-badge ${alert.severity || 'high'}">${(alert.severity || 'उच्च').toUpperCase()}</span>
                    </div>
                    <div class="rec-key-info">${alertSummary}</div>
                    <div class="rec-content">${alert.hindi_details || alert.details || alertSummary}</div>
                    <div class="rec-action">📋 कार्रवाई: ${alert.hindi_action || alert.action || 'जल निकास सुनिश्चित करें'}</div>
                    <a href="/weather/details/alerts" class="detail-btn">विवरण देखें →</a>
                </div>`;
            });
        }

        // Irrigation Advice
        if (recs.irrigation_advice && Object.keys(recs.irrigation_advice).length > 0) {
            const advice = recs.irrigation_advice;
            const summary = advice.hindi_summary || advice.summary || 'सिंचाई सलाह';
            const details = advice.hindi_details || advice.details || summary;
            const needed = advice.needed ? 'हाँ' : 'नहीं';
            const timing = advice.timing || 'तदनुसार';
            html += this.renderDetailedCard(
                '💧 सिंचाई सलाह',
                'rec-irrigation',
                `आवश्यक: ${needed} | समय: ${timing}`,
                summary,
                details,
                'irrigation'
            );
        }

        // Pest/Disease Alerts
        if (recs.pest_disease_alerts && recs.pest_disease_alerts.length > 0) {
            recs.pest_disease_alerts.forEach((pest, idx) => {
                const riskClass = pest.risk_level ? `risk-${pest.risk_level}` : '';
                const riskBadge = pest.risk_level ? `<span class="risk-badge ${pest.risk_level}">${pest.risk_level.toUpperCase()}</span>` : '';
                const pestName = pest.pest_disease_hindi || pest.pest || 'अज्ञात कीट/रोग';
                const summary = pest.hindi_summary || pest.summary || pestName;
                const details = pest.hindi_details || pest.details || summary;
                const prevention = pest.hindi_prevention || pest.prevention || '';
                
                html += `<div class="recommendation-card rec-pest ${riskClass}" data-detail-type="pest" style="cursor: pointer;">
                    <div class="rec-header">
                        <h3 class="rec-title">🐛 ${pestName}</h3>
                        ${riskBadge}
                    </div>
                    <div class="rec-key-info">${summary}</div>
                    <div class="rec-content">${details}</div>
                    ${prevention ? `<div class="rec-prevention">🛡️ निवारण: ${prevention}</div>` : ''}
                    <a href="/weather/details/pest" class="detail-btn">विवरण देखें →</a>
                </div>`;
            });
        }

        // Fertilizer Timing
        if (recs.fertilizer_timing && Object.keys(recs.fertilizer_timing).length > 0) {
            const fert = recs.fertilizer_timing;
            const summary = fert.hindi_summary || fert.summary || 'खाद का समय';
            const details = fert.hindi_details || fert.details || summary;
            const nextDay = fert.next_application_day || '3';
            const type = fert.type || 'मिश्रित';
            const quantity = fert.quantity_kg_per_hectare || '50';
            
            html += `<div class="recommendation-card rec-fertilizer" data-detail-type="fertilizer" style="cursor: pointer;">
                <div class="rec-header">
                    <h3 class="rec-title">🌾 खाद का समय</h3>
                </div>
                <div class="rec-key-info">दिन ${nextDay} को ${type} (${quantity} किग्रा/हे)</div>
                <div class="rec-content">${summary}</div>
                <div class="rec-details">${details}</div>
                <div class="rec-precautions">⚠️ सावधानियां: ${fert.precautions_hindi || fert.precautions || 'वर्षा के 1-2 दिन पहले लगाएं'}</div>
                <a href="/weather/details/fertilizer" class="detail-btn">विवरण देखें →</a>
            </div>`;
        }

        // Weather Warnings
        if (recs.weather_warnings && recs.weather_warnings.length > 0) {
            recs.weather_warnings.forEach(warning => {
                const condition = warning.condition_hindi || warning.condition || 'मौसम की चेतावनी';
                const summary = warning.hindi_summary || warning.summary || condition;
                const details = warning.hindi_details || warning.details || summary;
                const preparedness = warning.preparedness_hindi || warning.preparedness || '';
                
                html += `<div class="recommendation-card rec-weather" data-detail-type="weather" style="cursor: pointer;">
                    <div class="rec-header">
                        <h3 class="rec-title">⚠️ ${condition}</h3>
                    </div>
                    <div class="rec-key-info">${summary}</div>
                    <div class="rec-content">${details}</div>
                    ${preparedness ? `<div class="rec-preparedness">🚨 तैयारी: ${preparedness}</div>` : ''}
                    <a href="/weather/details/weather" class="detail-btn">विवरण देखें →</a>
                </div>`;
            });
        }

        // Soil Management
        if (recs.soil_management && Object.keys(recs.soil_management).length > 0) {
            const soil = recs.soil_management;
            const summary = soil.hindi_summary || soil.summary || 'मिट्टी प्रबंधन';
            const details = soil.hindi_details || soil.details || summary;
            
            html += `<div class="recommendation-card rec-soil" data-detail-type="soil" style="cursor: pointer;">
                <div class="rec-header">
                    <h3 class="rec-title">🌱 मिट्टी प्रबंधन</h3>
                </div>
                <div class="rec-content">${summary}</div>
                <div class="rec-details">${details}</div>
                ${soil.mulching_required ? `<div class="rec-action">✓ गीली घास की आवश्यकता है</div>` : ''}
                ${soil.drainage_required ? `<div class="rec-action">✓ जल निकास की आवश्यकता है</div>` : ''}
                <a href="/weather/details/soil" class="detail-btn">विवरण देखें →</a>
            </div>`;
        }

        // Seasonal Insights
        if (recs.seasonal_insights && Object.keys(recs.seasonal_insights).length > 0) {
            const seasonal = recs.seasonal_insights;
            const summary = seasonal.hindi_summary || seasonal.summary || 'मौसमी सुझाव';
            const details = seasonal.hindi_details || seasonal.details || summary;
            
            html += `<div class="recommendation-card rec-seasonal" data-detail-type="seasonal" style="cursor: pointer;">
                <div class="rec-header">
                    <h3 class="rec-title">📈 मौसमी सुझाव</h3>
                </div>
                <div class="rec-content">${summary}</div>
                <div class="rec-details">${details}</div>
                ${seasonal.optimal_practices ? `<div class="rec-practices">💡 सर्वोत्तम प्रथाएं: ${seasonal.optimal_practices}</div>` : ''}
                <a href="/weather/details/seasonal" class="detail-btn">विवरण देखें →</a>
            </div>`;
        }

        this.recommendationsSection.innerHTML = html || this.getEmptyState();
    }

    /**
     * Render detailed recommendation card with more information
     */
    renderDetailedCard(title, className, keyInfo, summary, details, detailType, badge = '') {
        return `
            <div class="recommendation-card ${className}" data-detail-type="${detailType}" style="cursor: pointer;">
                <div class="rec-header">
                    <h3 class="rec-title">${title}</h3>
                    ${badge}
                </div>
                <div class="rec-key-info">${keyInfo}</div>
                <div class="rec-content">${summary}</div>
                <div class="rec-details">${details}</div>
                <a href="/weather/details/${detailType}" class="detail-btn">विवरण देखें →</a>
            </div>
        `;
    }

    /**
     * Render individual recommendation card HTML
     */
    renderRecommendationCard(title, className, keyInfo, summary, detailType, badge = '') {
        return `
            <div class="recommendation-card ${className}" data-detail-type="${detailType}" style="cursor: pointer;">
                <div class="rec-header">
                    <h3 class="rec-title">${title}</h3>
                    ${badge}
                </div>
                <div class="rec-key-info">${keyInfo}</div>
                <div class="rec-content">${summary}</div>
                <a href="/weather/details/${detailType}" class="detail-btn">विवरण देखें →</a>
            </div>
        `;
    }

    /**
     * Render 7-day weather forecast
     */
    renderForecast() {
        if (!this.weatherForecast || !Array.isArray(this.weatherForecast)) {
            this.forecastCards.innerHTML = '<p>पूर्वानुमान डेटा उपलब्ध नहीं है</p>';
            return;
        }

        let html = '';
        for (const day of this.weatherForecast.slice(0, 7)) {
            const date = new Date(day.date);
            const dateStr = date.toLocaleDateString('hi-IN', { month: 'short', day: '2-digit' });
            const dayStr = date.toLocaleDateString('hi-IN', { weekday: 'short' });
            const emoji = this.getWeatherEmoji(day.summary);

            html += `
                <div class="forecast-card">
                    <div class="forecast-date">${dayStr}</div>
                    <div class="forecast-date" style="font-size: 11px; color: #666;">${dateStr}</div>
                    <div class="forecast-emoji">${emoji}</div>
                    <div class="forecast-temp">${day.temp_min}°-${day.temp_max}°C</div>
                    <div class="forecast-detail">🌧️ ${day.precip_mm}मिमी</div>
                    <div class="forecast-detail">💨 ${day.wind_kmh}किमी/घंटा</div>
                </div>
            `;
        }

        this.forecastCards.innerHTML = html;
    }

    /**
     * Update current weather in header
     */
    updateCurrentWeather() {
        if (this.weatherForecast && this.weatherForecast.length > 0) {
            const today = this.weatherForecast[0];
            const emoji = this.getWeatherEmoji(today.summary);
            this.currentWeatherMini.innerHTML = `<div>${emoji} ${today.temp_max}°C</div>`;
            
            // Get farmer location from session or API
            this.getFarmerInfo();
        }
    }

    /**
     * Get farmer information
     */
    async getFarmerInfo() {
        // We can get this from localStorage or make an API call
        // For now, we'll use the session-stored farmer name
        const farmerName = sessionStorage.getItem('farmerName') || 'किसान';
        this.farmerNameEl.textContent = farmerName;
        this.locationText.textContent = '📍 लोड हो रहा है...';
    }

    /**
     * Handle refresh button click
     */
    async handleRefresh() {
        this.refreshBtn.classList.add('loading');
        this.refreshBtn.disabled = true;

        try {
            const response = await fetch('/weather/api/refresh', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success) {
                this.currentRecommendations = data.recommendations;
                this.weatherForecast = data.weather_data;
                this.cacheExpiresAt = new Date(data.expires_at);
                this.renderRecommendations();
                this.renderForecast();
                this.updateCurrentWeather();
                this.addChatMessage('सिफारिशें सफलतापूर्वक रिफ्रेश कर दी गई हैं।', 'assistant');
            } else {
                this.addChatMessage('रिफ्रेश विफल: ' + (data.error || 'अज्ञात त्रुटि'), 'assistant');
            }
        } catch (error) {
            console.error('Refresh error:', error);
            this.addChatMessage('रिफ्रेश में त्रुटि: ' + error.message, 'assistant');
        } finally {
            this.refreshBtn.classList.remove('loading');
            this.refreshBtn.disabled = false;
            // Ensure loading state is fully cleared
            void this.refreshBtn.offsetWidth; // Force reflow
        }
    }

    /**
     * Handle chat message send
     */
    async handleSendMessage() {
        const question = this.chatInput.value.trim();
        if (!question) return;

        // Add user message to chat
        this.addChatMessage(question, 'user');
        this.chatInput.value = '';
        this.sendBtn.disabled = true;
        this.sendBtn.classList.add('loading');

        // Add typing indicator
        const typingId = 'typing-' + Date.now();
        this.addTypingIndicator(typingId);

        try {
            const response = await fetch('/weather/api/ask-followup', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);

            if (data.success) {
                this.addChatMessage(data.answer, 'assistant');
            } else {
                this.addChatMessage(
                    'उत्तर नहीं मिल सका: ' + (data.error || 'अज्ञात त्रुटि'),
                    'assistant'
                );
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.removeTypingIndicator(typingId);
            this.addChatMessage(
                'चैट त्रुटि: ' + error.message,
                'assistant'
            );
        } finally {
            this.sendBtn.disabled = false;
            this.sendBtn.classList.remove('loading');
            this.chatInput.focus();
        }
    }

    /**
     * Add typing indicator
     */
    addTypingIndicator(typingId) {
        const typingEl = document.createElement('div');
        typingEl.id = typingId;
        typingEl.className = 'message assistant typing-indicator';
        typingEl.innerHTML = '<span></span><span></span><span></span>';
        this.chatMessages.appendChild(typingEl);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * Remove typing indicator
     */
    removeTypingIndicator(typingId) {
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();
    }

    /**
     * Add message to chat
     */
    addChatMessage(text, role) {
        const msgEl = document.createElement('div');
        msgEl.className = `message ${role}`;
        msgEl.textContent = text;

        // Remove welcome message if present
        const welcome = this.chatMessages.querySelector('.chat-welcome');
        if (welcome) welcome.remove();

        this.chatMessages.appendChild(msgEl);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

        this.chatContext.push({ role, content: text });
    }



    /**
     * Minimize chat
     */
    minimizeChat() {
        this.chatWidget.style.display = 'none';
        this.chatToggle.style.display = 'block';
    }

    /**
     * Maximize chat
     */
    maximizeChat() {
        this.chatWidget.style.display = 'flex';
        this.chatToggle.style.display = 'none';
        this.chatInput.focus();
    }

    /**
     * Toggle forecast visibility
     */
    toggleForecastVisibility() {
        const cards = document.querySelector('.forecast-cards');
        const isHidden = cards.style.display === 'none';
        
        cards.style.display = isHidden ? 'grid' : 'none';
        this.toggleForecast.classList.toggle('collapsed');
    }

    /**
     * Start cache timer
     */
    startCacheTimer() {
        if (!this.cacheExpiresAt) return;

        const updateTimer = () => {
            const now = new Date();
            const diff = this.cacheExpiresAt - now;

            if (diff <= 0) {
                this.cacheTimer.textContent = '⏰ कैश समाप्त';
                clearInterval(this.timerInterval);
            } else {
                // Show expiry time in 12-hour format
                const expiryTime = new Date(this.cacheExpiresAt);
                const hours = String(expiryTime.getHours() % 12 || 12).padStart(2, '0');
                const minutes = String(expiryTime.getMinutes()).padStart(2, '0');
                const ampm = expiryTime.getHours() >= 12 ? 'PM' : 'AM';
                this.cacheTimer.textContent = `⏰ ${hours}:${minutes} ${ampm}`;
            }
        };

        updateTimer();
        this.timerInterval = setInterval(updateTimer, 60000); // Update every minute
    }

    /**
     * Show loading state
     */
    showLoading(elementId, message) {
        const el = document.getElementById(elementId);
        el.innerHTML = `
            <div class="section-loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Show error state
     */
    showError(elementId, message) {
        const el = document.getElementById(elementId);
        el.innerHTML = `
            <div class="section-loading" style="color: #d32f2f;">
                <div style="font-size: 32px; margin-bottom: 12px;">❌</div>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Get empty state HTML
     */
    getEmptyState() {
        return `
            <div style="text-align: center; padding: 40px 20px; grid-column: 1/-1;">
                <div style="font-size: 48px; margin-bottom: 12px;">🤔</div>
                <p style="color: #999;">कोई सिफारिशें उपलब्ध नहीं हैं।</p>
            </div>
        `;
    }

    /**
     * Get weather emoji based on condition
     */
    getWeatherEmoji(summary) {
        const lower = (summary || '').toLowerCase();
        if (lower.includes('sunny') || lower.includes('clear')) return '☀️';
        if (lower.includes('rain') || lower.includes('rainy')) return '🌧️';
        if (lower.includes('cloudy') || lower.includes('cloud')) return '☁️';
        if (lower.includes('storm') || lower.includes('thunder')) return '⛈️';
        if (lower.includes('snow')) return '❄️';
        if (lower.includes('wind')) return '🌬️';
        if (lower.includes('fog') || lower.includes('foggy')) return '🌫️';
        return '🌤️';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.weatherAIManager = new WeatherAIManager();
});
