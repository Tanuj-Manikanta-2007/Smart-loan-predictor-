const API_BASE_URL = 'http://localhost:8001';

document.getElementById('loanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await submitPrediction();
});

async function submitPrediction() {
    const form = document.getElementById('loanForm');
    const submitBtn = form.querySelector('.btn-submit');
    
    // Show loading state
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'none';
    submitBtn.disabled = true;

    try {
        // Collect form data
        const formData = new FormData(form);
        const existingLoans = parseInt(formData.get('existingLoans'));
        
        const payload = {
            person_age: parseInt(formData.get('age')),
            person_gender: formData.get('gender'),
            person_education: capitalizeEducation(formData.get('education')),
            person_income: parseFloat(formData.get('income')),
            person_emp_exp: parseInt(formData.get('employmentYears')),
            person_home_ownership: formData.get('homeOwnership').toUpperCase(),
            loan_amnt: parseFloat(formData.get('loanAmount')),
            loan_intent: formData.get('loanPurpose').toUpperCase(),
            loan_int_rate: 11.5,
            loan_percent_income: parseFloat(formData.get('loanAmount')) / parseFloat(formData.get('income')),
            cb_person_cred_hist_length: parseInt(formData.get('employmentYears')),
            credit_score: parseInt(formData.get('creditScore')),
            previous_loan_defaults_on_file: existingLoans > 2 ? "YES" : "NO"
        };

        // Validate input
        if (!validateInput(payload)) {
            throw new Error('Please fill in all fields with valid values');
        }

        // Make API request
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get prediction');
        }

        const result = await response.json();
        displayResult(result);

    } catch (error) {
        displayError(error.message);
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
        submitBtn.disabled = false;
    }
}

function validateInput(data) {
    return (
        data.person_gender && data.person_gender !== '' &&
        data.person_age >= 18 && data.person_age <= 100 &&
        data.person_education && data.person_education !== '' &&
        data.person_emp_exp >= 0 &&
        data.person_income > 0 &&
        data.person_home_ownership && data.person_home_ownership !== '' &&
        data.credit_score >= 0 && data.credit_score <= 850 &&
        data.loan_amnt > 0 &&
        data.loan_intent && data.loan_intent !== ''
    );
}

function capitalizeEducation(edu) {
    const eduMap = {
        'high_school': 'High School',
        'bachelor': 'Bachelor',
        'master': 'Master',
        'phd': 'Doctor'
    };
    return eduMap[edu] || 'Bachelor';
}

function displayResult(result) {
    const isApproved = result.prediction === 'Approved';
    
    // Prediction
    const predictionClass = isApproved ? 'approved' : 'rejected';
    const predictionEmoji = isApproved ? '✅' : '❌';
    document.getElementById('predictionResult').innerHTML = 
        `<strong>${predictionEmoji} Prediction:</strong> <span class="${predictionClass}">${result.prediction}</span>`;

    // Probability
    const probabilityPercent = (result.probability * 100).toFixed(2);
    document.getElementById('probabilityResult').innerHTML = 
        `<strong>📊 Approval Probability:</strong> ${probabilityPercent}%`;

    // Risk Level
    const riskLevel = result.probability > 0.7 ? 'Low' : result.probability > 0.4 ? 'Medium' : 'High';
    const riskClass = `risk-${riskLevel.toLowerCase()}`;
    const riskEmoji = getRiskEmoji(riskLevel);
    document.getElementById('riskResult').innerHTML = 
        `<strong>${riskEmoji} Risk Level:</strong> <span class="${riskClass}">${riskLevel}</span>`;

    // Recommendation
    const recommendation = isApproved ? 
        'Your loan application looks good! Consider maintaining your credit score.' :
        'Consider improving your credit score and reducing existing debts.';
    document.getElementById('recommendationResult').innerHTML = 
        `<strong>💡 Recommendation:</strong> ${recommendation}`;

    // Show result container
    document.getElementById('resultContainer').style.display = 'block';
}

function displayError(message) {
    document.getElementById('errorMessage').textContent = `Error: ${message}`;
    document.getElementById('errorContainer').style.display = 'block';
}

function getRiskEmoji(riskLevel) {
    switch(riskLevel.toLowerCase()) {
        case 'low':
            return '🟢';
        case 'medium':
            return '🟡';
        case 'high':
            return '🔴';
        default:
            return '❓';
    }
}

// Test API connection on page load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/docs`);
        if (!response.ok) {
            console.warn('API server is not responding');
        }
    } catch (error) {
        console.warn('Cannot connect to API server. Make sure it is running on http://localhost:8001');
    }
});
