// Initialize Particles.js Background
particlesJS("particles-js", {
    particles: {
        number: { value: 60, density: { enable: true, value_area: 800 } },
        color: { value: ["#06B6D4", "#8B5CF6", "#22C55E"] },
        shape: { type: "circle" },
        opacity: { value: 0.5, random: true },
        size: { value: 3, random: true },
        line_linked: { enable: true, distance: 150, color: "#ffffff", opacity: 0.1, width: 1 },
        move: { enable: true, speed: 1.5, direction: "none", random: false, straight: false, out_mode: "out", bounce: false }
    },
    interactivity: {
        detect_on: "canvas",
        events: { onhover: { enable: true, mode: "grab" }, resize: true },
        modes: { grab: { distance: 140, line_linked: { opacity: 0.5 } } }
    },
    retina_detect: true
});

// Scroll Reveal Animations
function reveal() {
    var reveals = document.querySelectorAll(".reveal");
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 100;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
    }
}
window.addEventListener("scroll", reveal);
reveal(); // Trigger on load

// Number Counter Animation for Stats
const counters = document.querySelectorAll('.counter');
const speed = 200; // Lower is slower

const animateCounters = () => {
    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText;
            const inc = target / speed;
            if (count < target) {
                counter.innerText = Math.ceil(count + inc);
                setTimeout(updateCount, 10);
            } else {
                counter.innerText = target + (target % 1 !== 0 ? "" : ""); // Handle decimals gracefully if needed
            }
        };
        updateCount();
    });
};

// Start counters when stats section is visible
let counted = false;
window.addEventListener('scroll', () => {
    const statsSection = document.querySelector('.stats-section');
    if(!counted && window.scrollY + window.innerHeight > statsSection.offsetTop + 100) {
        animateCounters();
        counted = true;
    }
});

// API Integration and UI State Management
const form = document.getElementById("predictionForm");
const formCard = document.querySelector(".form-card");
const loadingState = document.getElementById("loadingState");
const resultCard = document.getElementById("resultCard");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // 1. Gather Data
    const data = {
        pregnancies: parseInt(document.getElementById("pregnancies").value),
        glucose: parseFloat(document.getElementById("glucose").value),
        blood_pressure: parseFloat(document.getElementById("bloodPressure").value),
        skin_thickness: parseFloat(document.getElementById("skinThickness").value),
        insulin: parseFloat(document.getElementById("insulin").value),
        bmi: parseFloat(document.getElementById("bmi").value),
        diabetes_pedigree_function: parseFloat(document.getElementById("diabetesPedigreeFunction").value),
        age: parseInt(document.getElementById("age").value)
    };

    // 2. Show Loading UI
    loadingState.classList.remove("hidden");
    
    // Artificial delay to show off the premium AI loading animation
    await new Promise(resolve => setTimeout(resolve, 2000));

    try {
        // 3. Make API Call
        const API_URL = "https://diabetes-medi-ai.vercel.app/predict";
        const response = await fetch(API_URL, {
          method: "POST",
          headers: {
                "Content-Type": "application/json"
  },
  body: JSON.stringify(data)
});

        const result = await response.json();
        
        // 4. Update UI with Result
        showResult(result.outcome);

    } catch (error) {
        console.error("API Error:", error);
        showResult("Error");
    }
});

function showResult(outcome) {
    // Hide Form and Loading
    formCard.classList.add("hidden");
    loadingState.classList.add("hidden");
    
    // Setup Result UI elements
    const resultIcon = document.getElementById("resultIcon");
    const resultTitle = document.getElementById("resultTitle");
    const resultMessage = document.getElementById("resultMessage");
    
    // Reset previous classes
    resultCard.className = "result-card glass";

    if (outcome === "Diabetic") {
        resultCard.classList.add("diabetic");
        resultIcon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
        resultTitle.innerHTML = "High Risk of Diabetes Detected";
        resultMessage.innerHTML = "The AI model has detected patterns consistent with diabetes. We strongly recommend consulting a healthcare professional for a formal clinical diagnosis.";
        resultTitle.style.color = "var(--red)";
    } else if (outcome === "Not Diabetic") {
        resultCard.classList.add("non-diabetic");
        resultIcon.innerHTML = '<i class="fa-solid fa-shield-check"></i>';
        resultTitle.innerHTML = "Low Risk of Diabetes Detected";
        resultMessage.innerHTML = "The AI model did not detect significant indicators of diabetes. Continue maintaining a healthy lifestyle and regular medical checkups.";
        resultTitle.style.color = "var(--green)";
    } else {
        resultIcon.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i>';
        resultTitle.innerHTML = "Connection Error";
        resultMessage.innerHTML = "Unable to reach the AI prediction server. Please verify your connection or try again later.";
    }

    // Display Result Card
    resultCard.classList.remove("hidden");
}

function resetForm() {
    form.reset();
    resultCard.classList.add("hidden");
    formCard.classList.remove("hidden");
    
    // Scroll back slightly to form
    document.getElementById("predict-section").scrollIntoView({ behavior: "smooth" });
}
