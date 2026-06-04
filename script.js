// ─────────────────────────────────────────────
//  Particles.js Background
// ─────────────────────────────────────────────
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

// ─────────────────────────────────────────────
//  Scroll Reveal
// ─────────────────────────────────────────────
function reveal() {
    document.querySelectorAll(".reveal").forEach(el => {
        if (el.getBoundingClientRect().top < window.innerHeight - 100) {
            el.classList.add("active");
        }
    });
}
window.addEventListener("scroll", reveal);
reveal();

// ─────────────────────────────────────────────
//  Counter Animation
// ─────────────────────────────────────────────
let counted = false;
function animateCounters() {
    document.querySelectorAll(".counter").forEach(counter => {
        const target = +counter.getAttribute("data-target");
        const increment = target / 200;
        const update = () => {
            const current = +counter.innerText;
            if (current < target) {
                counter.innerText = Math.ceil(current + increment);
                setTimeout(update, 10);
            } else {
                counter.innerText = target;
            }
        };
        update();
    });
}

window.addEventListener("scroll", () => {
    const statsSection = document.querySelector(".stats-section");
    if (!counted && window.scrollY + window.innerHeight > statsSection.offsetTop + 100) {
        animateCounters();
        counted = true;
    }
});

// ─────────────────────────────────────────────
//  DOM References
// ─────────────────────────────────────────────
const form        = document.getElementById("predictionForm");
const formCard    = document.querySelector(".form-card");
const loadingState = document.getElementById("loadingState");
const resultCard  = document.getElementById("resultCard");
const submitBtn   = document.getElementById("submitBtn");

// ─────────────────────────────────────────────
//  API base URL — same Vercel project, use relative
// ─────────────────────────────────────────────
const API_URL = "/api/predict";

// ─────────────────────────────────────────────
//  Form Submit
// ─────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        pregnancies:                 parseInt(document.getElementById("pregnancies").value),
        glucose:                     parseFloat(document.getElementById("glucose").value),
        blood_pressure:              parseFloat(document.getElementById("bloodPressure").value),
        skin_thickness:              parseFloat(document.getElementById("skinThickness").value),
        insulin:                     parseFloat(document.getElementById("insulin").value),
        bmi:                         parseFloat(document.getElementById("bmi").value),
        diabetes_pedigree_function:  parseFloat(document.getElementById("diabetesPedigreeFunction").value),
        age:                         parseInt(document.getElementById("age").value),
    };

    // Show loading overlay
    submitBtn.disabled = true;
    loadingState.classList.remove("hidden");

    try {
        // Minimum 1.5s loading so the animation is visible
        const [response] = await Promise.all([
            fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
            new Promise(r => setTimeout(r, 1500))
        ]);

        if (!response.ok) {
            let detail = `Server error ${response.status}`;
            try {
                const err = await response.json();
                detail = err.detail || detail;
            } catch (_) {}
            throw new Error(detail);
        }

        const result = await response.json();
        showResult(result.outcome, result.risk_score);

    } catch (error) {
        console.error("Prediction error:", error);
        showResult("Error", null, error.message);
    } finally {
        loadingState.classList.add("hidden");
        submitBtn.disabled = false;
    }
});

// ─────────────────────────────────────────────
//  Show Result
// ─────────────────────────────────────────────
function showResult(outcome, riskScore = null, errorMsg = "") {
    formCard.classList.add("hidden");

    const resultIcon    = document.getElementById("resultIcon");
    const resultTitle   = document.getElementById("resultTitle");
    const resultMessage = document.getElementById("resultMessage");
    const meterFill     = document.getElementById("meterFill");
    const meterText     = document.getElementById("meterText");

    // Reset classes
    resultCard.className = "result-card glass";

    if (outcome === "Diabetic") {
        resultCard.classList.add("diabetic");
        resultIcon.innerHTML     = '<i class="fa-solid fa-triangle-exclamation"></i>';
        resultTitle.textContent  = "High Risk of Diabetes Detected";
        resultTitle.style.color  = "var(--red)";
        resultMessage.textContent = "The AI model detected patterns strongly associated with diabetes. Please consult a healthcare professional for a full medical evaluation.";

    } else if (outcome === "Not Diabetic") {
        resultCard.classList.add("non-diabetic");
        resultIcon.innerHTML     = '<i class="fa-solid fa-shield-check"></i>';
        resultTitle.textContent  = "Low Risk of Diabetes Detected";
        resultTitle.style.color  = "var(--green)";
        resultMessage.textContent = "The AI model did not detect significant diabetes indicators. Continue maintaining a healthy lifestyle and schedule regular checkups.";

    } else {
        resultCard.classList.add("error");
        resultIcon.innerHTML     = '<i class="fa-solid fa-circle-exclamation"></i>';
        resultTitle.textContent  = "Connection Error";
        resultTitle.style.color  = "var(--red)";
        resultMessage.textContent = errorMsg
            ? `Unable to reach prediction server: ${errorMsg}`
            : "Unable to connect to the prediction server. Please try again later.";
    }

    // Update confidence meter with live risk score
    if (riskScore !== null) {
        const pct = Math.round(riskScore * 100);
        // Animate meter after a brief delay so CSS transition fires
        setTimeout(() => {
            meterFill.style.width = `${pct}%`;
        }, 100);
        meterText.textContent = `${pct}%`;
        document.querySelector(".confidence-meter span").textContent = "AI Risk Score";
    } else {
        meterFill.style.width = "0%";
        meterText.textContent = "N/A";
    }

    resultCard.classList.remove("hidden");
}

// ─────────────────────────────────────────────
//  Reset Form
// ─────────────────────────────────────────────
function resetForm() {
    form.reset();
    document.getElementById("meterFill").style.width = "0%";
    document.getElementById("meterText").textContent = "—";
    resultCard.classList.add("hidden");
    formCard.classList.remove("hidden");
    document.getElementById("predict-section").scrollIntoView({ behavior: "smooth" });
}
