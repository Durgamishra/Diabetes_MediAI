// Initialize Particles.js Background
particlesJS("particles-js", {
    particles: {
        number: { value: 60, density: { enable: true, value_area: 800 } },
        color: { value: ["#06B6D4", "#8B5CF6", "#22C55E"] },
        shape: { type: "circle" },
        opacity: { value: 0.5, random: true },
        size: { value: 3, random: true },
        line_linked: {
            enable: true,
            distance: 150,
            color: "#ffffff",
            opacity: 0.1,
            width: 1
        },
        move: {
            enable: true,
            speed: 1.5,
            direction: "none",
            random: false,
            straight: false,
            out_mode: "out",
            bounce: false
        }
    },
    interactivity: {
        detect_on: "canvas",
        events: {
            onhover: {
                enable: true,
                mode: "grab"
            },
            resize: true
        },
        modes: {
            grab: {
                distance: 140,
                line_linked: {
                    opacity: 0.5
                }
            }
        }
    },
    retina_detect: true
});

// Scroll Reveal Animations
function reveal() {
    const reveals = document.querySelectorAll(".reveal");

    reveals.forEach((element) => {
        const windowHeight = window.innerHeight;
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 100;

        if (elementTop < windowHeight - elementVisible) {
            element.classList.add("active");
        }
    });
}

window.addEventListener("scroll", reveal);
reveal();

// Number Counter Animation
const counters = document.querySelectorAll(".counter");
const speed = 200;

const animateCounters = () => {
    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.getAttribute("data-target");
            const count = +counter.innerText;

            const increment = target / speed;

            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(updateCount, 10);
            } else {
                counter.innerText = target;
            }
        };

        updateCount();
    });
};

let counted = false;

window.addEventListener("scroll", () => {
    const statsSection = document.querySelector(".stats-section");

    if (
        !counted &&
        window.scrollY + window.innerHeight >
        statsSection.offsetTop + 100
    ) {
        animateCounters();
        counted = true;
    }
});

// Form Elements
const form = document.getElementById("predictionForm");
const formCard = document.querySelector(".form-card");
const loadingState = document.getElementById("loadingState");
const resultCard = document.getElementById("resultCard");

// Prediction Form Submit
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        pregnancies: parseInt(document.getElementById("pregnancies").value),
        glucose: parseFloat(document.getElementById("glucose").value),
        blood_pressure: parseFloat(document.getElementById("bloodPressure").value),
        skin_thickness: parseFloat(document.getElementById("skinThickness").value),
        insulin: parseFloat(document.getElementById("insulin").value),
        bmi: parseFloat(document.getElementById("bmi").value),
        diabetes_pedigree_function: parseFloat(
            document.getElementById("diabetesPedigreeFunction").value
        ),
        age: parseInt(document.getElementById("age").value)
    };

    loadingState.classList.remove("hidden");

    try {
        await new Promise(resolve => setTimeout(resolve, 1500));

        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(
                `HTTP ${response.status}: ${errorText}`
            );
        }

        const result = await response.json();

        loadingState.classList.add("hidden");

        if (result.outcome) {
            showResult(result.outcome);
        } else {
            showResult("Error");
        }

    } catch (error) {
        console.error("API Error:", error);

        loadingState.classList.add("hidden");

        showResult("Error");
    }
});

// Display Result
function showResult(outcome) {

    formCard.classList.add("hidden");
    loadingState.classList.add("hidden");

    const resultIcon = document.getElementById("resultIcon");
    const resultTitle = document.getElementById("resultTitle");
    const resultMessage = document.getElementById("resultMessage");

    resultCard.className = "result-card glass";

    if (outcome === "Diabetic") {

        resultCard.classList.add("diabetic");

        resultIcon.innerHTML =
            '<i class="fa-solid fa-triangle-exclamation"></i>';

        resultTitle.textContent =
            "High Risk of Diabetes Detected";

        resultMessage.textContent =
            "The AI model detected patterns associated with diabetes. Please consult a healthcare professional for proper medical evaluation.";

        resultTitle.style.color = "var(--red)";

    } else if (outcome === "Not Diabetic") {

        resultCard.classList.add("non-diabetic");

        resultIcon.innerHTML =
            '<i class="fa-solid fa-shield-check"></i>';

        resultTitle.textContent =
            "Low Risk of Diabetes Detected";

        resultMessage.textContent =
            "The AI model did not detect significant indicators of diabetes. Continue maintaining healthy lifestyle habits.";

        resultTitle.style.color = "var(--green)";

    } else {

        resultIcon.innerHTML =
            '<i class="fa-solid fa-circle-exclamation"></i>';

        resultTitle.textContent =
            "Connection Error";

        resultMessage.textContent =
            "Unable to connect to the prediction server. Please try again later.";

        resultTitle.style.color = "var(--red)";
    }

    resultCard.classList.remove("hidden");
}

// Reset Form
function resetForm() {

    form.reset();

    resultCard.classList.add("hidden");

    formCard.classList.remove("hidden");

    document
        .getElementById("predict-section")
        .scrollIntoView({
            behavior: "smooth"
        });
}
