// =====================================
// ELEMENTS
// =====================================

const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const uploadForm = document.querySelector(".upload-card form");


// =====================================
// SHOW IMAGE PREVIEW
// =====================================

function showPreview(imageSource) {
    if (!preview || !imageSource) return;

    preview.src = imageSource;
    preview.style.display = "block";
    preview.style.opacity = "0";
    preview.style.transform = "scale(.95)";

    setTimeout(() => {
        preview.style.transition = ".35s ease";
        preview.style.opacity = "1";
        preview.style.transform = "scale(1)";
    }, 80);
}


// =====================================
// CREATE SMALL PREVIEW FOR STORAGE
// =====================================

function createStoredPreview(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onerror = () => {
            reject(new Error("Could not read image"));
        };

        reader.onload = function () {
            const temporaryImage = new Image();

            temporaryImage.onerror = () => {
                reject(new Error("Could not load image"));
            };

            temporaryImage.onload = function () {
                const maximumSize = 1200;

                let width = temporaryImage.width;
                let height = temporaryImage.height;

                if (width > maximumSize || height > maximumSize) {
                    const scale = Math.min(
                        maximumSize / width,
                        maximumSize / height
                    );

                    width = Math.round(width * scale);
                    height = Math.round(height * scale);
                }

                const canvas = document.createElement("canvas");

                canvas.width = width;
                canvas.height = height;

                const context = canvas.getContext("2d");

                context.drawImage(
                    temporaryImage,
                    0,
                    0,
                    width,
                    height
                );

                resolve(
                    canvas.toDataURL("image/jpeg", 0.85)
                );
            };

            temporaryImage.src = reader.result;
        };

        reader.readAsDataURL(file);
    });
}


// =====================================
// RESTORE PREVIEW AFTER SCAN
// =====================================

const restorePreview =
    sessionStorage.getItem("restoreLeafPreviewOnce");

const storedPreview =
    sessionStorage.getItem("selectedLeafPreview");

if (
    restorePreview === "true" &&
    storedPreview &&
    preview
) {
    showPreview(storedPreview);
}

/*
Clear immediately after restoring.

Because of this:
- prediction reload keeps the image once
- manual browser refresh removes the image
*/
sessionStorage.removeItem("restoreLeafPreviewOnce");
sessionStorage.removeItem("selectedLeafPreview");


// =====================================
// NEW IMAGE SELECTED
// =====================================

if (imageInput && preview) {
    imageInput.addEventListener("change", async function () {
        const file = this.files[0];

        if (!file) return;

        /*
        Selecting another image replaces the old preview.
        */
        sessionStorage.removeItem("restoreLeafPreviewOnce");
        sessionStorage.removeItem("selectedLeafPreview");

        try {
            const previewData = await createStoredPreview(file);

            showPreview(previewData);

            sessionStorage.setItem(
                "selectedLeafPreview",
                previewData
            );
        } catch (error) {
            console.error("Preview error:", error);

            /*
            Fallback preview if browser storage fails.
            */
            showPreview(
                URL.createObjectURL(file)
            );
        }
    });
}


// =====================================
// KEEP PREVIEW AFTER SCAN
// =====================================

if (uploadForm && imageInput) {
    uploadForm.addEventListener("submit", async function (event) {
        const file = imageInput.files[0];

        if (!file) return;

        const storedImage =
            sessionStorage.getItem("selectedLeafPreview");

        if (storedImage) {
            sessionStorage.setItem(
                "restoreLeafPreviewOnce",
                "true"
            );

            return;
        }

        /*
        Stop submission briefly if image processing
        has not finished yet.
        */
        event.preventDefault();

        try {
            const previewData = await createStoredPreview(file);

            sessionStorage.setItem(
                "selectedLeafPreview",
                previewData
            );

            sessionStorage.setItem(
                "restoreLeafPreviewOnce",
                "true"
            );
        } catch (error) {
            console.error("Storage error:", error);
        }

        /*
        Submit without triggering this event again.
        */
        uploadForm.submit();
    });
}


// =====================================
// ENGLISH / KANNADA TEXT
// =====================================

const english = {
    title: "AI Leaf Disease Detection",

    subtitle:
        "Detect crop diseases instantly using Artificial Intelligence.",

    heroHeading:
        "AI Powered Crop Disease Detection",

    heroText:
        "Upload a leaf image and receive an instant AI-powered prediction along with disease information and treatment recommendations.",

    uploadTitle:
        "Upload Leaf Image",

    uploadSub:
        "PNG • JPG • JPEG",

    scanBtn:
        "Scan Disease",

    features: [
        "✔ Fast Prediction",
        "✔ High Accuracy",
        "✔ Farmer Friendly"
    ]
};


const kannada = {
    title:
        "ಎಐ ಎಲೆ ರೋಗ ಪತ್ತೆ",

    subtitle:
        "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯಿಂದ ಬೆಳೆ ರೋಗ ಪತ್ತೆ.",

    heroHeading:
        "ಎಐ ಆಧಾರಿತ ಬೆಳೆ ರೋಗ ಪತ್ತೆ",

    heroText:
        "ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಕೆಲವೇ ಕ್ಷಣಗಳಲ್ಲಿ ರೋಗವನ್ನು ಪತ್ತೆಹಚ್ಚಿ.",

    uploadTitle:
        "ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",

    uploadSub:
        "PNG • JPG • JPEG",

    scanBtn:
        "ರೋಗ ಪತ್ತೆ ಮಾಡಿ",

    features: [
        "✔ ವೇಗವಾದ ಪತ್ತೆ",
        "✔ ಹೆಚ್ಚು ನಿಖರತೆ",
        "✔ ರೈತ ಸ್ನೇಹಿ"
    ]
};


// =====================================
// SAFE TEXT UPDATE
// =====================================

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.innerText = value;
    }
}


function applyLanguage(languageData) {
    setText("title", languageData.title);
    setText("subtitle", languageData.subtitle);
    setText("heroHeading", languageData.heroHeading);
    setText("heroText", languageData.heroText);
    setText("uploadTitle", languageData.uploadTitle);
    setText("uploadSub", languageData.uploadSub);
    setText("scanBtn", languageData.scanBtn);

    const featureList =
        document.querySelectorAll(".feature");

    featureList.forEach((item, index) => {
        if (languageData.features[index]) {
            item.innerText =
                languageData.features[index];
        }
    });
}


// =====================================
// LANGUAGE BUTTONS
// =====================================

const enBtn = document.getElementById("enBtn");
const knBtn = document.getElementById("knBtn");


function updateActiveButton(languageCode) {
    if (!enBtn || !knBtn) return;

    if (languageCode === "kn") {
        knBtn.classList.add("active");
        enBtn.classList.remove("active");
    } else {
        enBtn.classList.add("active");
        knBtn.classList.remove("active");
    }
}


async function changeLanguage(languageCode) {
    const languageData =
        languageCode === "kn"
            ? kannada
            : english;

    localStorage.setItem(
        "selectedLanguage",
        languageCode
    );

    applyLanguage(languageData);
    updateActiveButton(languageCode);

    try {
        const response = await fetch(
            `/language/${languageCode}`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                "Language update failed"
            );
        }

        window.location.reload();

    } catch (error) {
        console.error(error);

        alert(
            languageCode === "kn"
                ? "ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
                : "Could not change the language."
        );
    }
}


if (enBtn) {
    enBtn.addEventListener("click", function () {
        changeLanguage("en");
    });
}


if (knBtn) {
    knBtn.addEventListener("click", function () {
        changeLanguage("kn");
    });
}


const savedLanguage =
    localStorage.getItem("selectedLanguage") || "en";

if (savedLanguage === "kn") {
    applyLanguage(kannada);
    updateActiveButton("kn");
} else {
    applyLanguage(english);
    updateActiveButton("en");
}


// =====================================
// CONFIDENCE BAR COLOR
// =====================================

const fill = document.querySelector(".progress-fill");

if (fill) {
    const width = parseFloat(fill.style.width);

    if (width >= 95) {
        fill.style.background = "#16a34a";
    } else if (width >= 80) {
        fill.style.background = "#22c55e";
    } else if (width >= 60) {
        fill.style.background = "#eab308";
    } else {
        fill.style.background = "#ef4444";
    }
}


// =====================================
// CARD FADE ANIMATION
// =====================================

const cards = document.querySelectorAll(".info-card");

cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(25px)";

    setTimeout(() => {
        card.style.transition = ".55s ease";
        card.style.opacity = "1";
        card.style.transform = "translateY(0)";
    }, 180 * index);
});


// =====================================
// BUTTON RIPPLE EFFECT
// =====================================

const scanButton =
    document.querySelector(".scan-btn");

if (scanButton) {
    scanButton.addEventListener(
        "click",
        function (event) {
            const circle =
                document.createElement("span");

            const diameter = Math.max(
                this.clientWidth,
                this.clientHeight
            );

            circle.style.width =
                diameter + "px";

            circle.style.height =
                diameter + "px";

            circle.style.left =
                event.offsetX -
                diameter / 2 +
                "px";

            circle.style.top =
                event.offsetY -
                diameter / 2 +
                "px";

            circle.classList.add("ripple");

            const oldRipple =
                this.getElementsByClassName(
                    "ripple"
                )[0];

            if (oldRipple) {
                oldRipple.remove();
            }

            this.appendChild(circle);
        }
    );
}

// =====================================
// CLEAR RESULT ONLY ON MANUAL REFRESH
// =====================================

(function () {
    const keepResultKey = "keepPredictionOnLanguageChange";

    /*
    When a language button is clicked, allow the result
    to remain during the automatic page reload.
    */
    ["enBtn", "knBtn"].forEach(function (buttonId) {
        const button = document.getElementById(buttonId);

        if (button) {
            button.addEventListener(
                "click",
                function () {
                    sessionStorage.setItem(
                        keepResultKey,
                        "true"
                    );
                },
                { capture: true }
            );
        }
    });

    const navigationEntry =
        performance.getEntriesByType("navigation")[0];

    const resultSection =
        document.querySelector(".result-section");

    const keepResult =
        sessionStorage.getItem(keepResultKey) === "true";

    /*
    Remove the one-time permission immediately.
    The next manual refresh will clear the result.
    */
    if (keepResult) {
        sessionStorage.removeItem(keepResultKey);
    }

    /*
    Manual browser refresh:
    clear prediction and display the normal page + footer.
    */
    if (
        resultSection &&
        navigationEntry &&
        navigationEntry.type === "reload" &&
        !keepResult
    ) {
        window.location.replace("/clear-result");
    }
})();

// =====================================
// KEEP PREVIEW WHEN LANGUAGE CHANGES
// =====================================

(function () {
    const previewImage = document.getElementById("preview");

    ["enBtn", "knBtn"].forEach(function (buttonId) {
        const button = document.getElementById(buttonId);

        if (!button) return;

        button.addEventListener(
            "click",
            function () {
                if (
                    previewImage &&
                    previewImage.hasAttribute("src") &&
                    previewImage.getAttribute("src")
                ) {
                    sessionStorage.setItem(
                        "selectedLeafPreview",
                        previewImage.src
                    );

                    sessionStorage.setItem(
                        "restoreLeafPreviewOnce",
                        "true"
                    );
                }
            },
            { capture: true }
        );
    });
})();