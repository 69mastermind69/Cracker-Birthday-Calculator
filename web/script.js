"use strict";

/* =========================
   MOBILE MENU
========================= */

const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
        navLinks.classList.toggle("active");
    });

    document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => {
            navLinks.classList.remove("active");
        });
    });
}


/* =========================
   PARTICLES
========================= */

const particlesContainer = document.getElementById("particles");

if (particlesContainer) {
    const particleCount = window.innerWidth <= 650 ? 35 : 70;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement("span");

        particle.className = "particle";

        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 8}s`;
        particle.style.animationDuration = `${5 + Math.random() * 8}s`;
        particle.style.opacity = `${0.2 + Math.random() * 0.7}`;

        particlesContainer.appendChild(particle);
    }
}


/* =========================
   MODAL
========================= */

const modal = document.getElementById("calculatorModal");
const modalTitle = document.getElementById("modalTitle");
const modalBody = document.getElementById("modalBody");
const modalClose = document.getElementById("modalClose");

function openModal(title, content) {
    if (!modal || !modalTitle || !modalBody) return;

    modalTitle.textContent = title;
    modalBody.innerHTML = content;

    modal.classList.add("active");
    document.body.classList.add("modal-open");
}

function closeModal() {
    if (!modal) return;

    modal.classList.remove("active");
    document.body.classList.remove("modal-open");
}

if (modalClose) {
    modalClose.addEventListener("click", closeModal);
}

if (modal) {
    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeModal();
    }
});


/* =========================
   DATE HELPERS
========================= */

function formatDate(date) {
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric"
    });
}

function calculateAge(birthDate) {
    const today = new Date();

    let years = today.getFullYear() - birthDate.getFullYear();
    let months = today.getMonth() - birthDate.getMonth();
    let days = today.getDate() - birthDate.getDate();

    if (days < 0) {
        months--;

        const previousMonth = new Date(
            today.getFullYear(),
            today.getMonth(),
            0
        );

        days += previousMonth.getDate();
    }

    if (months < 0) {
        years--;
        months += 12;
    }

    const totalMilliseconds = today - birthDate;
    const totalDays = Math.floor(
        totalMilliseconds / (1000 * 60 * 60 * 24)
    );

    return {
        years,
        months,
        days,
        totalDays
    };
}


/* =========================
   BIRTHDAY CALCULATOR
========================= */

function showBirthdayCalculator() {
    openModal(
        "🎂 Birthday Calculator",
        `
        <div class="calculator-form">
            <label for="birthdayInput">Enter your birthday</label>

            <input
                type="date"
                id="birthdayInput"
                class="calculator-input"
            >

            <button
                id="birthdayCalculateBtn"
                class="calculator-button"
            >
                Calculate Age
            </button>

            <div id="birthdayResult" class="calculator-result"></div>
        </div>
        `
    );

    const button = document.getElementById("birthdayCalculateBtn");

    if (button) {
        button.addEventListener("click", () => {
            const input = document.getElementById("birthdayInput");
            const result = document.getElementById("birthdayResult");

            if (!input || !result || !input.value) {
                if (result) {
                    result.innerHTML = "⚠️ Please select your birthday.";
                }
                return;
            }

            const birthDate = new Date(`${input.value}T00:00:00`);
            const today = new Date();

            if (birthDate > today) {
                result.innerHTML = "⚠️ Birthday cannot be in the future.";
                return;
            }

            const age = calculateAge(birthDate);

            result.innerHTML = `
                <div class="result-box">
                    <h3>🎉 Your Age</h3>

                    <p>
                        <strong>
                            ${age.years} Years
                            ${age.months} Months
                            ${age.days} Days
                        </strong>
                    </p>

                    <p>
                        📅 Born: ${formatDate(birthDate)}
                    </p>

                    <p>
                        🕒 Total Days: ${age.totalDays.toLocaleString()}
                    </p>

                    <p>
                        ⏱️ Total Hours:
                        ${(age.totalDays * 24).toLocaleString()}
                    </p>
                </div>
            `;
        });
    }
}


/* =========================
   DATE DIFFERENCE
========================= */

function showDateDifference() {
    openModal(
        "📆 Date Difference Calculator",
        `
        <div class="calculator-form">

            <label for="firstDate">
                First Date
            </label>

            <input
                type="date"
                id="firstDate"
                class="calculator-input"
            >

            <label for="secondDate">
                Second Date
            </label>

            <input
                type="date"
                id="secondDate"
                class="calculator-input"
            >

            <button
                id="dateDifferenceBtn"
                class="calculator-button"
            >
                Calculate Difference
            </button>

            <div
                id="dateDifferenceResult"
                class="calculator-result"
            ></div>

        </div>
        `
    );

    const button = document.getElementById("dateDifferenceBtn");

    if (button) {
        button.addEventListener("click", () => {
            const first = document.getElementById("firstDate");
            const second = document.getElementById("secondDate");
            const result = document.getElementById(
                "dateDifferenceResult"
            );

            if (!first.value || !second.value) {
                result.innerHTML =
                    "⚠️ Please select both dates.";
                return;
            }

            const date1 = new Date(`${first.value}T00:00:00`);
            const date2 = new Date(`${second.value}T00:00:00`);

            const difference = Math.abs(date2 - date1);

            const totalDays = Math.floor(
                difference / (1000 * 60 * 60 * 24)
            );

            const weeks = Math.floor(totalDays / 7);
            const remainingDays = totalDays % 7;

            const totalHours = totalDays * 24;
            const totalMinutes = totalHours * 60;
            const totalSeconds = totalMinutes * 60;

            result.innerHTML = `
                <div class="result-box">

                    <h3>📊 Difference</h3>

                    <p>
                        📅 ${formatDate(date1)}
                    </p>

                    <p>
                        📅 ${formatDate(date2)}
                    </p>

                    <hr>

                    <p>
                        <strong>
                            ${totalDays.toLocaleString()}
                            Days
                        </strong>
                    </p>

                    <p>
                        📆 ${weeks} Weeks
                        ${remainingDays} Days
                    </p>

                    <p>
                        🕒 ${totalHours.toLocaleString()}
                        Hours
                    </p>

                    <p>
                        ⏱️ ${totalMinutes.toLocaleString()}
                        Minutes
                    </p>

                    <p>
                        ⚡ ${totalSeconds.toLocaleString()}
                        Seconds
                    </p>

                </div>
            `;
        });
    }
}


/* =========================
   COUNTDOWN
========================= */

let countdownInterval = null;

function showCountdown() {
    openModal(
        "⏳ Countdown",
        `
        <div class="calculator-form">

            <label for="countdownDate">
                Select Target Date & Time
            </label>

            <input
                type="datetime-local"
                id="countdownDate"
                class="calculator-input"
            >

            <button
                id="startCountdownBtn"
                class="calculator-button"
            >
                Start Countdown
            </button>

            <div
                id="countdownResult"
                class="calculator-result"
            ></div>

        </div>
        `
    );

    const button = document.getElementById(
        "startCountdownBtn"
    );

    if (button) {
        button.addEventListener("click", () => {
            const input = document.getElementById(
                "countdownDate"
            );

            const result = document.getElementById(
                "countdownResult"
            );

            if (!input.value) {
                result.innerHTML =
                    "⚠️ Please select a target date.";
                return;
            }

            const target = new Date(input.value);

            if (countdownInterval) {
                clearInterval(countdownInterval);
            }

            function updateCountdown() {
                const now = new Date();
                const difference = target - now;

                if (difference <= 0) {
                    clearInterval(countdownInterval);

                    result.innerHTML = `
                        <div class="result-box">
                            <h3>🎉 Time Reached!</h3>
                            <p>The countdown has finished.</p>
                        </div>
                    `;

                    return;
                }

                const days = Math.floor(
                    difference / (1000 * 60 * 60 * 24)
                );

                const hours = Math.floor(
                    (difference / (1000 * 60 * 60)) % 24
                );

                const minutes = Math.floor(
                    (difference / (1000 * 60)) % 60
                );

                const seconds = Math.floor(
                    (difference / 1000) % 60
                );

                result.innerHTML = `
                    <div class="result-box countdown-box">

                        <h3>⏰ Remaining</h3>

                        <div class="countdown-grid">

                            <div>
                                <strong>${days}</strong>
                                <span>Days</span>
                            </div>

                            <div>
                                <strong>${hours}</strong>
                                <span>Hours</span>
                            </div>

                            <div>
                                <strong>${minutes}</strong>
                                <span>Minutes</span>
                            </div>

                            <div>
                                <strong>${seconds}</strong>
                                <span>Seconds</span>
                            </div>

                        </div>

                    </div>
                `;
            }

            updateCountdown();

            countdownInterval =
                setInterval(updateCountdown, 1000);
        });
    }
}


/* =========================
   LIFE STATISTICS
========================= */

function showLifeStatistics() {
    openModal(
        "📊 Life Statistics",
        `
        <div class="calculator-form">

            <label for="lifeBirthday">
                Enter your birthday
            </label>

            <input
                type="date"
                id="lifeBirthday"
                class="calculator-input"
            >

            <button
                id="lifeStatsBtn"
                class="calculator-button"
            >
                Generate Statistics
            </button>

            <div
                id="lifeStatsResult"
                class="calculator-result"
            ></div>

        </div>
        `
    );

    const button = document.getElementById("lifeStatsBtn");

    if (button) {
        button.addEventListener("click", () => {
            const input =
                document.getElementById("lifeBirthday");

            const result =
                document.getElementById("lifeStatsResult");

            if (!input.value) {
                result.innerHTML =
                    "⚠️ Please select your birthday.";
                return;
            }

            const birthDate =
                new Date(`${input.value}T00:00:00`);

            const today = new Date();

            if (birthDate > today) {
                result.innerHTML =
                    "⚠️ Birthday cannot be in the future.";
                return;
            }

            const difference = today - birthDate;

            const days = Math.floor(
                difference / (1000 * 60 * 60 * 24)
            );

            const hours = days * 24;
            const minutes = hours * 60;
            const seconds = minutes * 60;

            result.innerHTML = `
                <div class="result-box">

                    <h3>📊 Life Statistics</h3>

                    <p>
                        🎂 Birthday:
                        ${formatDate(birthDate)}
                    </p>

                    <hr>

                    <p>
                        📅 Days Lived:
                        <strong>
                            ${days.toLocaleString()}
                        </strong>
                    </p>

                    <p>
                        🕒 Hours:
                        <strong>
                            ${hours.toLocaleString()}
                        </strong>
                    </p>

                    <p>
                        ⏱️ Minutes:
                        <strong>
                            ${minutes.toLocaleString()}
                        </strong>
                    </p>

                    <p>
                        ⚡ Seconds:
                        <strong>
                            ${seconds.toLocaleString()}
                        </strong>
                    </p>

                </div>
            `;
        });
    }
}


/* =========================
   AGE MILESTONES
========================= */

function showAgeMilestones() {
    openModal(
        "🎯 Age Milestones",
        `
        <div class="calculator-form">

            <label for="milestoneBirthday">
                Enter your birthday
            </label>

            <input
                type="date"
                id="milestoneBirthday"
                class="calculator-input"
            >

            <button
                id="milestoneBtn"
                class="calculator-button"
            >
                Check Milestones
            </button>

            <div
                id="milestoneResult"
                class="calculator-result"
            ></div>

        </div>
        `
    );

    const button = document.getElementById(
        "milestoneBtn"
    );

    if (button) {
        button.addEventListener("click", () => {
            const input = document.getElementById(
                "milestoneBirthday"
            );

            const result = document.getElementById(
                "milestoneResult"
            );

            if (!input.value) {
                result.innerHTML =
                    "⚠️ Please select your birthday.";
                return;
            }

            const birthDate =
                new Date(`${input.value}T00:00:00`);

            const today = new Date();

            if (birthDate > today) {
                result.innerHTML =
                    "⚠️ Birthday cannot be in the future.";
                return;
            }

            const milestones = [
                10,
                13,
                16,
                18,
                21,
                25,
                30,
                40,
                50,
                60,
                70,
                80,
                90,
                100
            ];

            let html = `
                <div class="result-box">
                    <h3>🎯 Milestones</h3>
            `;

            milestones.forEach((age) => {
                const milestoneDate =
                    new Date(birthDate);

                milestoneDate.setFullYear(
                    birthDate.getFullYear() + age
                );

                if (milestoneDate <= today) {
                    html += `
                        <p>
                            ✅ Age ${age} —
                            ${formatDate(milestoneDate)}
                        </p>
                    `;
                } else {
                    html += `
                        <p>
                            🔜 Age ${age} —
                            ${formatDate(milestoneDate)}
                        </p>
                    `;
                }
            });

            html += `</div>`;

            result.innerHTML = html;
        });
    }
}


/* =========================
   TELEGRAM BOT
========================= */

const telegramBotUrl =
    "https://t.me/cracker_team_05_bot";

function openTelegramBot() {
    window.open(
        telegramBotUrl,
        "_blank",
        "noopener,noreferrer"
    );
}


/* =========================
   CALCULATOR CARD ROUTER
========================= */

document.querySelectorAll(".calculator-card").forEach((card) => {

    card.addEventListener("click", () => {

        const calculator =
            card.dataset.calculator;

        switch (calculator) {

            case "birthday":
                showBirthdayCalculator();
                break;

            case "date-difference":
                showDateDifference();
                break;

            case "countdown":
                showCountdown();
                break;

            case "life-statistics":
                showLifeStatistics();
                break;

            case "milestones":
                showAgeMilestones();
                break;

            case "telegram":
                openTelegramBot();
                break;

            default:
                openModal(
                    "Coming Soon",
                    `
                    <div class="result-box">
                        <h3>🚀 Coming Soon</h3>
                        <p>
                            This calculator will be
                            available soon.
                        </p>
                    </div>
                    `
                );
        }
    });

});


/* =========================
   TELEGRAM BUTTONS
========================= */

document
    .querySelectorAll(
        '[data-action="telegram"]'
    )
    .forEach((button) => {

        button.addEventListener("click", (event) => {
            event.preventDefault();
            openTelegramBot();
        });

    });


/* =========================
   NAVIGATION
========================= */

document
    .querySelectorAll('a[href^="#"]')
    .forEach((link) => {

        link.addEventListener("click", (event) => {

            const targetId =
                link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target =
                document.querySelector(targetId);

            if (target) {
                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }

        });

    });


/* =========================
   MOUSE PARALLAX
========================= */

if (
    window.innerWidth > 900 &&
    !window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches
) {

    document.addEventListener("mousemove", (event) => {

        const x =
            (event.clientX / window.innerWidth - 0.5) * 2;

        const y =
            (event.clientY / window.innerHeight - 0.5) * 2;

        const orb =
            document.querySelector(".hero-orb");

        if (orb) {
            orb.style.transform = `
                translate(
                    ${x * 8}px,
                    ${y * 8}px
                )
            `;
        }

    });

}


/* =========================
   ACTIVE NAVIGATION
========================= */

const sections =
    document.querySelectorAll("section[id]");

const navigationLinks =
    document.querySelectorAll(".nav-link");

window.addEventListener("scroll", () => {

    let currentSection = "";

    sections.forEach((section) => {

        const sectionTop =
            section.offsetTop - 180;

        if (window.scrollY >= sectionTop) {
            currentSection = section.id;
        }

    });

    navigationLinks.forEach((link) => {

        link.classList.remove("active");

        const href =
            link.getAttribute("href");

        if (
            href &&
            href === `#${currentSection}`
        ) {
            link.classList.add("active");
        }

    });

});


/* =========================
   PAGE LOAD
========================= */

window.addEventListener("load", () => {

    document.body.classList.add("page-loaded");

});


/* =========================
   REDUCED MOTION
========================= */

if (
    window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches
) {

    document
        .querySelectorAll("*")
        .forEach((element) => {
            element.style.animationDuration = "0.01ms";
            element.style.animationIterationCount = "1";
            element.style.scrollBehavior = "auto";
        });

}
