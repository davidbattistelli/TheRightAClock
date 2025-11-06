/**
 * SleepCycle-Alarm Frontend JavaScript
 * Handles form submission and API communication
 */

// Configuration
const API_BASE_URL = "http://localhost:8000/api/v1";

// DOM Elements
const form = document.getElementById("calculator-form");
const toggleAdvancedBtn = document.getElementById("toggle-advanced");
const advancedOptions = document.getElementById("advanced-options");
const resultsSection = document.getElementById("results-section");
const resultsContainer = document.getElementById("results-container");
const resultsWakeTime = document.getElementById("results-wake-time");
const errorMessage = document.getElementById("error-message");
const errorText = document.getElementById("error-text");
const calculateBtn = document.getElementById("calculate-btn");

// State
let isAdvancedOpen = false;

/**
 * Initialize the application
 */
function init() {
    // Event listeners
    form.addEventListener("submit", handleSubmit);
    toggleAdvancedBtn.addEventListener("click", toggleAdvanced);

    // Set current time + 8 hours as default wake time
    const now = new Date();
    now.setHours(now.getHours() + 8);
    const defaultWakeTime = now.toTimeString().slice(0, 5);
    document.getElementById("wake-time").value = defaultWakeTime;

    console.log("SleepCycle-Alarm initialized");
}

/**
 * Toggle advanced options visibility
 */
function toggleAdvanced() {
    isAdvancedOpen = !isAdvancedOpen;
    if (isAdvancedOpen) {
        advancedOptions.classList.add("open");
        toggleAdvancedBtn.textContent = "⚙️ Hide Advanced Options";
    } else {
        advancedOptions.classList.remove("open");
        toggleAdvancedBtn.textContent = "⚙️ Advanced Options";
    }
}

/**
 * Handle form submission
 * @param {Event} e - Submit event
 */
async function handleSubmit(e) {
    e.preventDefault();

    // Hide previous results/errors
    hideError();
    hideResults();

    // Get form values
    const formData = getFormData();

    // Validate form data
    const validation = validateFormData(formData);
    if (!validation.valid) {
        showError(validation.error);
        return;
    }

    // Show loading state
    setLoadingState(true);

    try {
        // Call API
        const results = await calculateBedtimes(formData);

        // Display results
        displayResults(results);

    } catch (error) {
        console.error("Error calculating bedtimes:", error);
        showError(error.message || "Failed to calculate bedtimes. Please try again.");
    } finally {
        setLoadingState(false);
    }
}

/**
 * Get form data as object
 * @returns {Object} Form data
 */
function getFormData() {
    return {
        wake_time: document.getElementById("wake-time").value,
        sleep_latency_min: parseInt(document.getElementById("sleep-latency").value),
        cycle_length_min: parseInt(document.getElementById("cycle-length").value),
        min_cycles: parseInt(document.getElementById("min-cycles").value),
        max_cycles: parseInt(document.getElementById("max-cycles").value),
    };
}

/**
 * Validate form data
 * @param {Object} data - Form data
 * @returns {Object} Validation result {valid: boolean, error?: string}
 */
function validateFormData(data) {
    if (!data.wake_time) {
        return { valid: false, error: "Please enter a wake time" };
    }

    if (data.sleep_latency_min < 0 || data.sleep_latency_min > 60) {
        return { valid: false, error: "Sleep latency must be between 0 and 60 minutes" };
    }

    if (data.cycle_length_min < 60 || data.cycle_length_min > 110) {
        return { valid: false, error: "Cycle length must be between 60 and 110 minutes" };
    }

    if (data.min_cycles < 1 || data.min_cycles > 10) {
        return { valid: false, error: "Min cycles must be between 1 and 10" };
    }

    if (data.max_cycles < 1 || data.max_cycles > 10) {
        return { valid: false, error: "Max cycles must be between 1 and 10" };
    }

    if (data.min_cycles > data.max_cycles) {
        return { valid: false, error: "Min cycles must be less than or equal to max cycles" };
    }

    return { valid: true };
}

/**
 * Call the API to calculate bedtimes
 * @param {Object} data - Form data
 * @returns {Promise<Object>} API response
 */
async function calculateBedtimes(data) {
    const response = await fetch(`${API_BASE_URL}/calculate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    return await response.json();
}

/**
 * Display calculation results
 * @param {Object} data - API response data
 */
function displayResults(data) {
    // Clear previous results
    resultsContainer.innerHTML = "";

    // Set wake time in header
    resultsWakeTime.textContent = data.wake_time;

    // Create result cards
    data.options.forEach((option, index) => {
        const card = createResultCard(option, index === 0);
        resultsContainer.appendChild(card);
    });

    // Show results section
    resultsSection.style.display = "block";

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Create a result card element
 * @param {Object} option - Bedtime option
 * @param {boolean} isFirst - Whether this is the first option
 * @returns {HTMLElement} Result card element
 */
function createResultCard(option, isFirst) {
    const card = document.createElement("div");
    card.className = `result-card ${option.recommended ? "recommended" : ""}`;

    // Format sleep duration
    const hours = Math.floor(option.total_sleep_hours);
    const minutes = Math.round((option.total_sleep_hours - hours) * 60);
    const durationText = `${hours}h ${minutes}m`;

    card.innerHTML = `
        <div class="result-header">
            <div class="bedtime">🛏️ ${option.bedtime}</div>
            <div class="cycles-badge">${option.cycles} cycle${option.cycles > 1 ? "s" : ""}</div>
        </div>
        <div class="sleep-info">
            Total sleep: <span class="sleep-duration">${durationText}</span>
            (${option.total_sleep_minutes} minutes)
        </div>
        <div class="sleep-note">
            ${option.note}
        </div>
    `;

    return card;
}

/**
 * Show error message
 * @param {string} message - Error message
 */
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = "block";
    errorMessage.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = "none";
}

/**
 * Hide results section
 */
function hideResults() {
    resultsSection.style.display = "none";
}

/**
 * Set loading state for calculate button
 * @param {boolean} loading - Whether loading or not
 */
function setLoadingState(loading) {
    if (loading) {
        calculateBtn.classList.add("loading");
        calculateBtn.disabled = true;
        calculateBtn.textContent = "Calculating";
    } else {
        calculateBtn.classList.remove("loading");
        calculateBtn.disabled = false;
        calculateBtn.textContent = "Calculate Bedtimes";
    }
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}

// Export for testing (if needed)
if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        validateFormData,
        calculateBedtimes,
    };
}
