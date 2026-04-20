document.addEventListener("DOMContentLoaded", () => {
    // --- DOM Elements ---
    const uploadZone = document.getElementById("upload-zone");
    const fileInput = document.getElementById("file-input");
    const viewerZone = document.getElementById("viewer-zone");
    const sourceImage = document.getElementById("source-image");
    const heatmapOverlay = document.getElementById("heatmap-overlay");
    const heatmapToggle = document.getElementById("heatmap-toggle");
    const imageLoader = document.getElementById("image-loader");
    const btnReset = document.getElementById("btn-reset");
    
    const predictionsList = document.getElementById("predictions-list");
    const clinicalInsight = document.getElementById("clinical-insight");
    
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");
    
    const chatHistory = document.getElementById("chat-history");
    const chatInput = document.getElementById("chat-input");
    const btnSendChat = document.getElementById("send-chat");

    // --- State ---
    let currentContext = []; // stores predicted labels
    let heatmapsStore = {}; // condition -> base64 string
    let topCondition = null;

    // --- UI Interactions: Tabs ---
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tabContents.forEach(tc => tc.style.display = "none");
            
            tab.classList.add("active");
            document.getElementById(tab.dataset.target).style.display = "flex";
            
            if(tab.dataset.target === "chat-tab" && currentContext.length > 0) {
                chatInput.focus();
            }
        });
    });

    // --- File Upload Logic ---
    uploadZone.addEventListener("click", () => fileInput.click());
    
    uploadZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadZone.classList.add("dragover");
    });
    
    uploadZone.addEventListener("dragleave", () => {
        uploadZone.classList.remove("dragover");
    });
    
    uploadZone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    btnReset.addEventListener("click", () => {
        uploadZone.classList.remove("hidden");
        viewerZone.classList.add("hidden");
        sourceImage.src = "";
        heatmapOverlay.src = "";
        heatmapToggle.checked = false;
        heatmapToggle.disabled = true;
        predictionsList.innerHTML = '<div class="placeholder-text">Upload a scan to initiate analysis.</div>';
        clinicalInsight.innerHTML = '<p class="placeholder-text">Awaiting diagnostic targets...</p>';
        chatInput.disabled = true;
        btnSendChat.disabled = true;
        currentContext = [];
        heatmapsStore = {};
    });

    // --- Heatmap Toggle ---
    heatmapToggle.addEventListener("change", (e) => {
        if(e.target.checked && currentContext.length > 0 && heatmapsStore[topCondition]) {
            heatmapOverlay.src = heatmapsStore[topCondition];
            heatmapOverlay.classList.remove("hidden");
            heatmapOverlay.classList.add("active");
        } else {
            heatmapOverlay.classList.remove("active");
            setTimeout(() => heatmapOverlay.classList.add("hidden"), 400);
        }
    });

    // --- Core API Routine ---
    function handleFile(file) {
        if (!file.type.startsWith("image/")) {
            alert("Please upload a valid image file (PNG/JPG).");
            return;
        }

        // Setup UI for analysis
        const url = URL.createObjectURL(file);
        sourceImage.src = url;
        uploadZone.classList.add("hidden");
        viewerZone.classList.remove("hidden");
        imageLoader.classList.remove("hidden");
        predictionsList.innerHTML = '';
        clinicalInsight.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;margin:0"></div> Generating clinical insight...';

        const formData = new FormData();
        formData.append("file", file);

        fetch("/api/analyze", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            imageLoader.classList.add("hidden");
            if (data.error) {
                alert("Error during analysis: " + data.error);
                return;
            }

            // 1. Process Predictions
            const preds = data.predictions;
            currentContext = preds.map(p => p.condition);
            heatmapsStore = data.heatmaps;
            
            if(preds.length > 0) {
                topCondition = preds[0].condition;
                heatmapToggle.disabled = false;
                
                preds.forEach(p => {
                    const confPercent = (p.confidence * 100).toFixed(1);
                    let barClass = "low";
                    if (p.confidence > 0.7) barClass = "high";
                    else if (p.confidence > 0.3) barClass = "med";
                    
                    const el = document.createElement("div");
                    el.className = "prediction-item";
                    el.innerHTML = `
                        <div class="pred-header">
                            <span class="pred-label">${p.condition}</span>
                            <span class="pred-val">${confPercent}%</span>
                        </div>
                        <div class="pred-bar-bg">
                            <div class="pred-bar ${barClass}" style="width: 0%"></div>
                        </div>
                    `;
                    predictionsList.appendChild(el);
                    // Animate bar
                    setTimeout(() => {
                        el.querySelector('.pred-bar').style.width = `${confPercent}%`;
                    }, 100);
                });

                // Auto-enable heatmap for top condition if it exists
                if(heatmapsStore[topCondition]) {
                    heatmapToggle.checked = true;
                    heatmapOverlay.src = heatmapsStore[topCondition];
                    heatmapOverlay.classList.remove("hidden");
                    heatmapOverlay.classList.add("active");
                }
            } else {
                predictionsList.innerHTML = '<div class="placeholder-text">No significant abnormalities detected above threshold.</div>';
            }

            // 2. Process Clinical Insight (Markdown to HTML)
            if (data.clinical_insight) {
                clinicalInsight.innerHTML = marked.parse(data.clinical_insight);
            }

            // 3. Enable Chat
            chatInput.disabled = false;
            btnSendChat.disabled = false;
        })
        .catch(err => {
            imageLoader.classList.add("hidden");
            alert("Network error: " + err);
        });
    }

    // --- Copilot Chat Logic ---
    function sendChat() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add User Bubble
        addChatBubble(text, "user");
        chatInput.value = "";
        
        // Add Temporary System Loader
        const loaderId = "loader-" + Date.now();
        addChatBubble('<div class="spinner" style="width:15px;height:15px;border-width:2px;margin:0;"></div>', "system", loaderId);

        fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: text, context: currentContext })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById(loaderId).remove();
            if(data.error) {
                addChatBubble("Error: " + data.error, "system");
            } else {
                addChatBubble(marked.parse(data.response), "system");
            }
        })
        .catch(err => {
            document.getElementById(loaderId).remove();
            addChatBubble("Network Error: " + err, "system");
        });
    }

    function addChatBubble(html, type, id="") {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${type}`;
        if (id) bubble.id = id;
        
        // If it's pure text, set innerHTML directly (marked.parse handles HTML)
        bubble.innerHTML = html;
        chatHistory.appendChild(bubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    btnSendChat.addEventListener("click", sendChat);
    chatInput.addEventListener("keypress", (e) => {
        if(e.key === "Enter") sendChat();
    });
});
