// Form validation and enhancement
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#strategyForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }

    // Add input validation on change
    document.addEventListener('change', function(e) {
        if (e.target.tagName === 'INPUT' && e.target.type === 'number') {
            validateInput(e.target);
        }
    });

    // Add input validation on blur
    document.addEventListener('blur', function(e) {
        if (e.target.tagName === 'INPUT' && e.target.type === 'number') {
            validateInput(e.target);
        }
    }, true);
});

// Validate individual input
function validateInput(input) {
    const value = parseFloat(input.value);
    const name = input.name;

    let isValid = true;
    let message = '';

    // Specific validation rules
    if (name === 'start_balance') {
        if (value <= 0) {
            isValid = false;
            message = 'Starting balance must be positive';
        }
    } else if (name === 'daily_return') {
        if (value < 0) {
            isValid = false;
            message = 'Daily return cannot be negative';
        }
    } else if (name === 'win_rate') {
        if (value < 0 || value > 100) {
            isValid = false;
            message = 'Win rate must be between 0 and 100%';
        }
    } else if (name === 'rr_ratio' || name === 'leverage' || name === 'sl_pips') {
        if (value <= 0) {
            isValid = false;
            message = input.previousElementSibling?.textContent + ' must be positive';
        }
    }

    if (isValid) {
        input.style.borderColor = '#00e676';
        input.style.boxShadow = 'none';
    } else {
        input.style.borderColor = '#ff4444';
        input.style.boxShadow = '0 0 8px rgba(255, 68, 68, 0.3)';
        if (message) {
            showTooltip(input, message);
        }
    }

    return isValid;
}

// Show tooltip on input
function showTooltip(input, message) {
    // Remove existing tooltip if any
    const existingTooltip = input.parentElement.querySelector('.input-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }

    // Create and show tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'input-tooltip';
    tooltip.textContent = message;
    tooltip.style.cssText = `
        color: #ff4444;
        font-size: 0.8rem;
        margin-top: 4px;
        padding: 4px 8px;
        background: rgba(255, 68, 68, 0.1);
        border-left: 2px solid #ff4444;
        border-radius: 3px;
    `;
    input.parentElement.appendChild(tooltip);

    // Remove tooltip after 5 seconds
    setTimeout(() => {
        tooltip.remove();
    }, 5000);
}

// Comprehensive form validation
function validateForm() {
    const startBalance = parseFloat(document.getElementById('start_balance').value);
    const riskReward = parseFloat(document.getElementById('rr_ratio').value);
    const winRate = parseFloat(document.getElementById('win_rate').value);
    const leverage = parseFloat(document.getElementById('leverage').value);
    const slPips = parseFloat(document.getElementById('sl_pips').value);

    let allValid = true;

    // Validate required fields
    const requiredInputs = document.querySelectorAll('input[required]');
    requiredInputs.forEach(input => {
        if (!input.value || parseFloat(input.value) <= 0) {
            input.style.borderColor = '#ff4444';
            allValid = false;
        }
    });

    // Specific validations
    if (startBalance <= 0) {
        showNotification('❌ Starting balance must be greater than 0', 'error');
        return false;
    }

    if (riskReward <= 0) {
        showNotification('❌ Risk/Reward ratio must be greater than 0', 'error');
        return false;
    }

    if (winRate < 0 || winRate > 100) {
        showNotification('❌ Win rate must be between 0 and 100%', 'error');
        return false;
    }

    if (leverage < 1) {
        showNotification('❌ Leverage must be at least 1x', 'error');
        return false;
    }

    if (slPips <= 0) {
        showNotification('❌ Stop loss must be positive', 'error');
        return false;
    }

    // Validate milestones
    const milestones = document.querySelectorAll('input[name="milestone[]"]');
    const targetPercents = document.querySelectorAll('input[name="target_percent[]"]');

    if (milestones.length === 0 || targetPercents.length === 0) {
        showNotification('❌ Please add at least one milestone', 'error');
        return false;
    }

    if (milestones.length !== targetPercents.length) {
        showNotification('❌ Each milestone must have a target percentage', 'error');
        return false;
    }

    // Check milestone values
    for (let i = 0; i < milestones.length; i++) {
        const milestone = parseFloat(milestones[i].value);
        const target = parseFloat(targetPercents[i].value);

        if (milestone <= 0) {
            showNotification(`❌ Milestone ${i + 1}: Balance must be positive`, 'error');
            return false;
        }

        if (target <= 0 || target > 100) {
            showNotification(`❌ Milestone ${i + 1}: Target must be between 0 and 100%`, 'error');
            return false;
        }
    }

    return allValid;
}

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-pane');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active from buttons
    const btns = document.querySelectorAll('.tab-btn');
    btns.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Mark button as active
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

// Apply preset function
function applyPreset(presetType) {
    fetch(`/api/preset/${presetType}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('daily_return').value = data.daily_return;
            document.getElementById('win_rate').value = data.win_rate;
            document.getElementById('rr_ratio').value = data.rr_ratio;
            document.getElementById('leverage').value = data.leverage;
            document.getElementById('sl_pips').value = data.sl_pips;
            
            // Switch to manual tab
            const tabPanes = document.querySelectorAll('.tab-pane');
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById('manual-tab').classList.add('active');
            
            const btns = document.querySelectorAll('.tab-btn');
            btns.forEach(btn => btn.classList.remove('active'));
            btns[1].classList.add('active');
            
            // Scroll to form
            setTimeout(() => {
                const form = document.getElementById('strategyForm');
                if (form) {
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            }, 100);
            
            showNotification(`✅ ${data.name} strategy loaded!`);
        })
        .catch(err => {
            console.error('Error loading preset:', err);
            showNotification('❌ Error loading preset', 'error');
        });
}

// Milestone management
function addMilestone() {
    const container = document.getElementById('milestones-container');
    const newGroup = document.createElement('div');
    newGroup.className = 'milestone-group';
    const count = container.children.length + 1;
    newGroup.innerHTML = `
        <div class="form-group">
            <label>Milestone ${count} Balance ($)</label>
            <input type="number" step="0.01" name="milestone[]" placeholder="e.g., 15000" required>
        </div>
        <div class="form-group">
            <label>Target Profit (%)</label>
            <input type="number" step="0.01" name="target_percent[]" placeholder="e.g., 2.0" required>
        </div>
        <button type="button" class="btn-remove" onclick="removeMilestone(this)">❌</button>
    `;
    container.appendChild(newGroup);
    showNotification(`✅ Milestone ${count} added`);
}

function removeMilestone(btn) {
    const container = document.getElementById('milestones-container');
    if (container.children.length > 1) {
        btn.parentElement.remove();
        showNotification('Milestone removed');
    } else {
        showNotification('You must have at least one milestone', 'error');
    }
}

// Notification system
function showNotification(message, type = 'success') {
    const notif = document.createElement('div');
    notif.className = `notification ${type}`;
    notif.textContent = message;
    document.body.appendChild(notif);
    
    // Force reflow to trigger animation
    setTimeout(() => {
        notif.classList.add('show');
    }, 10);
    
    // Remove notification
    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => notif.remove(), 300);
    }, 4000);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Format percentage
function formatPercentage(value) {
    return value.toFixed(2) + '%';
}

// Real-time input feedback
document.addEventListener('input', function(e) {
    if (e.target.type === 'number') {
        const value = parseFloat(e.target.value);
        
        // Clear error state while typing
        if (value > 0 || e.target.value === '') {
            e.target.style.borderColor = '#00e676';
            e.target.style.boxShadow = 'none';
        }
    }
});

// Prevent form submission on Enter in milestone inputs
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && 
        (e.target.name === 'milestone[]' || e.target.name === 'target_percent[]')) {
        e.preventDefault();
        addMilestone();
    }
});

console.log('Insights360 - Enhanced trading strategy planner loaded successfully!');
