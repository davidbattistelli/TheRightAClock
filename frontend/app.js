/**
 * SleepCycle-Alarm Frontend JavaScript
 * Handles form submission and API communication
 */

// Configuration
// Auto-detect API URL based on environment
const API_BASE_URL = window.location.hostname === "localhost"
    ? "http://localhost:8000/api/v1"
    : "https://therightaclock.onrender.com/api/v1";  // Update this with your actual backend URL

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
let countdownIntervals = {}; // Store countdown intervals by bedtime
let notificationPermission = null;

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

    // Request notification permission
    requestNotificationPermission();

    console.log("SleepCycle-Alarm initialized");
}

/**
 * Request notification permission from user
 */
async function requestNotificationPermission() {
    if (!("Notification" in window)) {
        console.log("This browser does not support notifications");
        return;
    }

    if (Notification.permission === "granted") {
        notificationPermission = "granted";
    } else if (Notification.permission !== "denied") {
        const permission = await Notification.requestPermission();
        notificationPermission = permission;
    }
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
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

        const response = await fetch(`${API_BASE_URL}/calculate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error("Request timeout. The server might be waking up (can take 30-60 seconds on free hosting). Please try again.");
        }
        if (error.message === 'Failed to fetch' || error.message.includes('NetworkError')) {
            throw new Error("Cannot connect to server. It might be waking up from sleep (takes 30-60 seconds on free hosting). Please wait and try again.");
        }
        throw error;
    }
}

/**
 * Display calculation results
 * @param {Object} data - API response data
 */
function displayResults(data) {
    // Clear previous results and intervals
    resultsContainer.innerHTML = "";
    Object.values(countdownIntervals).forEach(clearInterval);
    countdownIntervals = {};

    // Set wake time in header
    resultsWakeTime.textContent = data.wake_time;

    // Create result cards
    data.options.forEach((option, index) => {
        const card = createResultCard(option, data.wake_time, index === 0);
        resultsContainer.appendChild(card);
    });

    // Show results section
    resultsSection.style.display = "block";

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Calculate time until bedtime
 * @param {string} bedtime - Bedtime in HH:MM format
 * @returns {Object} Hours and minutes until bedtime
 */
function getTimeUntilBedtime(bedtime) {
    const now = new Date();
    const [hours, minutes] = bedtime.split(":").map(Number);

    const bedtimeDate = new Date();
    bedtimeDate.setHours(hours, minutes, 0, 0);

    // If bedtime is earlier than current time, it's for today (past bedtime)
    // Otherwise check if it's in the past (already happened today)
    let diff = bedtimeDate - now;

    // If negative and less than -12 hours, assume it's for tonight (add 24 hours)
    if (diff < 0 && diff > -12 * 60 * 60 * 1000) {
        bedtimeDate.setDate(bedtimeDate.getDate() + 1);
        diff = bedtimeDate - now;
    }

    const totalMinutes = Math.floor(diff / 1000 / 60);
    const hoursUntil = Math.floor(totalMinutes / 60);
    const minutesUntil = totalMinutes % 60;

    return { hours: hoursUntil, minutes: minutesUntil, totalMinutes, isPast: totalMinutes < 0 };
}

/**
 * Update countdown display
 * @param {HTMLElement} element - Countdown element
 * @param {string} bedtime - Bedtime in HH:MM format
 */
function updateCountdown(element, bedtime) {
    const { hours, minutes, totalMinutes, isPast } = getTimeUntilBedtime(bedtime);

    if (isPast) {
        element.textContent = "Time has passed";
        element.className = "countdown past";
        return false; // Stop countdown
    }

    if (totalMinutes === 0) {
        element.textContent = "🔔 Time to sleep now!";
        element.className = "countdown now";
        sendBedtimeNotification(bedtime);
        return false; // Stop countdown
    }

    element.textContent = `⏱️ ${hours}h ${minutes}m until bedtime`;
    element.className = "countdown active";
    return true; // Continue countdown
}

/**
 * Send browser notification for bedtime
 * @param {string} bedtime - Bedtime in HH:MM format
 */
function sendBedtimeNotification(bedtime) {
    if (notificationPermission === "granted") {
        new Notification("Time to Sleep! 😴", {
            body: `It's ${bedtime} - Time to go to bed to wake up refreshed!`,
            icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75'>😴</text></svg>",
            requireInteraction: true,
        });
    }
}

/**
 * Generate .ics calendar file content
 * @param {string} bedtime - Bedtime in HH:MM format
 * @param {string} wakeTime - Wake time in HH:MM format
 * @param {number} cycles - Number of sleep cycles
 * @returns {string} .ics file content
 */
function generateICSFile(bedtime, wakeTime, cycles) {
    const now = new Date();
    const [bedHours, bedMinutes] = bedtime.split(":").map(Number);
    const [wakeHours, wakeMinutes] = wakeTime.split(":").map(Number);

    // Create bedtime date (tonight or tomorrow if past)
    const bedtimeDate = new Date();
    bedtimeDate.setHours(bedHours, bedMinutes, 0, 0);
    if (bedtimeDate < now) {
        bedtimeDate.setDate(bedtimeDate.getDate() + 1);
    }

    // Create wake time date (next day from bedtime)
    const wakeTimeDate = new Date(bedtimeDate);
    wakeTimeDate.setDate(wakeTimeDate.getDate() + 1);
    wakeTimeDate.setHours(wakeHours, wakeMinutes, 0, 0);

    // Create alarm time (15 min before bedtime for reminder)
    const alarmDate = new Date(bedtimeDate);
    alarmDate.setMinutes(alarmDate.getMinutes() - 15);

    // Format dates for .ics (YYYYMMDDTHHMMSS)
    const formatDate = (date) => {
        return date.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
    };

    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SleepCycle-Alarm//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:${Date.now()}@sleepcycle-alarm.app
DTSTAMP:${formatDate(now)}
DTSTART:${formatDate(bedtimeDate)}
DTEND:${formatDate(wakeTimeDate)}
SUMMARY:💤 Bedtime - ${cycles} sleep cycles
DESCRIPTION:Go to bed at ${bedtime} to wake up refreshed at ${wakeTime} after ${cycles} sleep cycles.
BEGIN:VALARM
TRIGGER:-PT15M
DESCRIPTION:Time to start winding down for bed!
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR`;

    return icsContent;
}

/**
 * Download .ics calendar file
 * @param {string} bedtime - Bedtime in HH:MM format
 * @param {string} wakeTime - Wake time in HH:MM format
 * @param {number} cycles - Number of sleep cycles
 */
function downloadCalendarEvent(bedtime, wakeTime, cycles) {
    const icsContent = generateICSFile(bedtime, wakeTime, cycles);
    const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `bedtime-${bedtime.replace(":", "")}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

/**
 * Toggle browser notifications for a specific bedtime
 * @param {string} bedtime - Bedtime in HH:MM format
 * @param {HTMLElement} button - The button element that was clicked
 */
function toggleNotifications(bedtime, button) {
    if (notificationPermission !== "granted") {
        if (Notification.permission === "denied") {
            alert("Notifications are blocked. Please enable them in your browser settings.");
        } else {
            Notification.requestPermission().then((permission) => {
                notificationPermission = permission;
                if (permission === "granted") {
                    button.textContent = "✓ Alert Enabled";
                    button.classList.add("enabled");
                    // Test notification
                    new Notification("Notifications Enabled! 🔔", {
                        body: `You'll be notified when it's ${bedtime}`,
                    });
                } else {
                    alert("Please enable notifications to use this feature.");
                }
            });
        }
    } else {
        button.textContent = "✓ Alert Enabled";
        button.classList.add("enabled");
        button.disabled = true;
        // Test notification
        new Notification("Notifications Enabled! 🔔", {
            body: `You'll be notified when it's ${bedtime}`,
        });
    }
}

/**
 * Create a result card element
 * @param {Object} option - Bedtime option
 * @param {boolean} isFirst - Whether this is the first option
 * @param {string} wakeTime - Wake time in HH:MM format
 * @returns {HTMLElement} Result card element
 */
function createResultCard(option, wakeTime, isFirst) {
    const card = document.createElement("div");
    card.className = `result-card ${option.recommended ? "recommended" : ""}`;

    // Format sleep duration
    const hours = Math.floor(option.total_sleep_hours);
    const minutes = Math.round((option.total_sleep_hours - hours) * 60);
    const durationText = `${hours}h ${minutes}m`;

    // Create countdown element
    const countdownId = `countdown-${option.bedtime.replace(":", "")}`;

    card.innerHTML = `
        <div class="result-header">
            <div class="bedtime">🛏️ ${option.bedtime}</div>
            <div class="cycles-badge">${option.cycles} cycle${option.cycles > 1 ? "s" : ""}</div>
        </div>
        <div class="countdown active" id="${countdownId}">⏱️ Calculating...</div>
        <div class="sleep-info">
            Total sleep: <span class="sleep-duration">${durationText}</span>
            (${option.total_sleep_minutes} minutes)
        </div>
        <div class="sleep-note">
            ${option.note}
        </div>
        <div class="action-buttons">
            <button class="btn-action btn-calendar" onclick="downloadCalendarEvent('${option.bedtime}', '${wakeTime}', ${option.cycles})">
                📅 Add to Calendar
            </button>
            <button class="btn-action btn-notify" onclick="toggleNotifications('${option.bedtime}', this)">
                🔔 Enable Alert
            </button>
        </div>
    `;

    // Start countdown
    const countdownElement = card.querySelector(`#${countdownId}`);
    updateCountdown(countdownElement, option.bedtime);

    // Set up interval to update countdown every minute
    const intervalId = setInterval(() => {
        const shouldContinue = updateCountdown(countdownElement, option.bedtime);
        if (!shouldContinue) {
            clearInterval(intervalId);
            delete countdownIntervals[option.bedtime];
        }
    }, 60000); // Update every minute

    countdownIntervals[option.bedtime] = intervalId;

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
