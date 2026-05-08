/* ═════════════════════════════════════════════════════════ */
/*  CINE-NLP — Frontend Application Logic                    */
/* ═════════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;

const DEMO_TEXT = `I absolootely luved the mvie! It was an amazeing exprince with graet acting and a beautifl plot. However, the ending was a bit confusing and slightly disappointing. The pacing started off well but felt rushed towards the finale. Overall, I highly recommend watching it.`;

// ─── DOM Elements ────────────────────────────────────────
const pipelineInput   = document.getElementById('pipeline-input');
const btnDemo         = document.getElementById('btn-demo');
const btnClear        = document.getElementById('btn-clear');
const btnMic          = document.getElementById('btn-mic');
const btnRun          = document.getElementById('btn-run');
const btnRunDefault   = document.querySelector('.btn-run-default');
const btnRunLoading   = document.querySelector('.btn-run-loading');
const sentimentDot    = document.getElementById('sentiment-dot');
const sentimentLabel  = document.getElementById('sentiment-label');
const pipelineProgress = document.getElementById('pipeline-progress');
const resultsArea     = document.getElementById('results-area');
const navbar          = document.getElementById('navbar');
const hamburger       = document.getElementById('nav-hamburger');
const mobileMenu      = document.getElementById('mobile-menu');

// Voice Recorder Elements
const voiceRecorderModal   = document.getElementById('voice-recorder-modal');
const voiceRecorderBackdrop = document.querySelector('.voice-recorder-backdrop');
const voiceRecorderClose   = document.getElementById('voice-recorder-close');
const btnStartRecording    = document.getElementById('btn-start-recording');
const btnStopRecording     = document.getElementById('btn-stop-recording');
const btnUseRecording      = document.getElementById('btn-use-recording');
const voiceRecorderCancel  = document.getElementById('voice-recorder-cancel');
const voiceStatus          = document.getElementById('voice-status');
const voiceTimer           = document.getElementById('voice-timer');
const voiceWaveform        = document.getElementById('voice-waveform');

// Movie Search Elements
const tmdbKeyInput     = document.getElementById('tmdb-api-key');
const movieQueryInput  = document.getElementById('movie-query');
const btnSearchMovie   = document.getElementById('btn-search-movie');
const searchBtnText    = document.querySelector('.search-btn-text');
const searchBtnLoader  = document.querySelector('.search-btn-loader');
const movieResultsWrap = document.getElementById('movie-results');
const movieDetailWrap  = document.getElementById('movie-selection-detail');
const btnAnalyzePlot   = document.getElementById('btn-analyze-plot');

const btnCopySummary   = document.getElementById('btn-copy-summary');

// ═══════════════════════════════════════════════════════════
//  SCROLL ANIMATIONS (Intersection Observer)
// ═══════════════════════════════════════════════════════════
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -60px 0px'
    });

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// ═══════════════════════════════════════════════════════════
//  NAVBAR
// ═══════════════════════════════════════════════════════════
function initNavbar() {
    // Scroll style
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Hamburger
    hamburger.addEventListener('click', () => {
        mobileMenu.classList.toggle('open');
        const spans = hamburger.querySelectorAll('span');
        if (mobileMenu.classList.contains('open')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
        } else {
            spans[0].style.transform = '';
            spans[1].style.opacity = '';
            spans[2].style.transform = '';
        }
    });

    // Close mobile menu on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('open');
            const spans = hamburger.querySelectorAll('span');
            spans[0].style.transform = '';
            spans[1].style.opacity = '';
            spans[2].style.transform = '';
        });
    });
}

// ═══════════════════════════════════════════════════════════
//  FAQ ACCORDION
// ═══════════════════════════════════════════════════════════
function initFAQ() {
    document.querySelectorAll('.faq-question').forEach(btn => {
        btn.addEventListener('click', () => {
            const item = btn.closest('.faq-item');
            const isOpen = item.classList.contains('open');

            // Close all others
            document.querySelectorAll('.faq-item.open').forEach(openItem => {
                if (openItem !== item) {
                    openItem.classList.remove('open');
                    openItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
                }
            });

            // Toggle current
            item.classList.toggle('open', !isOpen);
            btn.setAttribute('aria-expanded', !isOpen);
        });
    });
}

// ═══════════════════════════════════════════════════════════
//  DEMO & CLEAR BUTTONS
// ═══════════════════════════════════════════════════════════
function initInputActions() {
    btnDemo.addEventListener('click', () => {
        pipelineInput.value = DEMO_TEXT;
        pipelineInput.dispatchEvent(new Event('input'));
        pipelineInput.focus();

        // Brief visual feedback
        btnDemo.style.background = 'rgba(90, 228, 167, 0.15)';
        setTimeout(() => { btnDemo.style.background = ''; }, 400);
    });

    btnClear.addEventListener('click', () => {
        pipelineInput.value = '';
        pipelineInput.dispatchEvent(new Event('input'));
        resultsArea.style.display = 'none';
        pipelineProgress.style.display = 'none';
        pipelineInput.focus();
    });
}

// ═══════════════════════════════════════════════════════════
//  LIVE SENTIMENT (Debounced)
// ═══════════════════════════════════════════════════════════
let sentimentTimer = null;

function initLiveSentiment() {
    pipelineInput.addEventListener('input', () => {
        const text = pipelineInput.value.trim();

        if (!text) {
            sentimentDot.className = 'live-sentiment-dot';
            sentimentLabel.textContent = 'Waiting for input...';
            return;
        }

        // Debounce: wait 400ms after user stops typing
        clearTimeout(sentimentTimer);
        sentimentLabel.textContent = 'Analyzing...';

        sentimentTimer = setTimeout(async () => {
            try {
                const resp = await fetch(`${API_BASE}/api/sentiment`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                const data = await resp.json();

                const sentiment = data.sentiment || 'Neutral';
                sentimentDot.className = 'live-sentiment-dot ' + sentiment.toLowerCase();

                const icons = { Positive: '🟢', Negative: '🔴', Neutral: '⚪' };
                sentimentLabel.textContent = `${icons[sentiment] || '⚪'} Live Tone: ${sentiment}`;
            } catch {
                sentimentLabel.textContent = '⚪ Live Tone: Unable to connect';
            }
        }, 400);
    });
}

// ═══════════════════════════════════════════════════════════
//  PIPELINE EXECUTION
// ═══════════════════════════════════════════════════════════
async function animateProgress() {
    const steps = document.querySelectorAll('.progress-step');
    for (let i = 0; i < steps.length; i++) {
        steps[i].classList.add('active');
        await sleep(250);
        steps[i].classList.remove('active');
        steps[i].classList.add('done');
    }
}

function resetProgress() {
    document.querySelectorAll('.progress-step').forEach(s => {
        s.classList.remove('active', 'done');
    });
}

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

function initPipeline() {
    btnRun.addEventListener('click', async () => {
        const text = pipelineInput.value.trim();
        if (!text) {
            // Flash the textarea border
            pipelineInput.style.outline = '2px solid #e85d75';
            pipelineInput.setAttribute('placeholder', '⚠️ Please enter some text first...');
            setTimeout(() => {
                pipelineInput.style.outline = '';
                pipelineInput.setAttribute('placeholder', 'Type or paste your text here...');
            }, 2000);
            return;
        }

        // Lock UI
        btnRun.disabled = true;
        btnRunDefault.style.display = 'none';
        btnRunLoading.style.display = 'flex';
        resultsArea.style.display = 'none';

        // Show progress
        resetProgress();
        pipelineProgress.style.display = 'block';

        // Animate progress steps in parallel with API call
        const progressPromise = animateProgress();

        try {
            const resp = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || 'Pipeline failed');
            }

            const data = await resp.json();

            // Wait for progress animation to finish
            await progressPromise;
            await sleep(300);

            // Render results
            renderResults(data);

        } catch (error) {
            await progressPromise;
            alert(`Pipeline Error: ${error.message}\n\nMake sure the Flask server is running on ${API_BASE}`);
        } finally {
            btnRun.disabled = false;
            btnRunDefault.style.display = 'flex';
            btnRunLoading.style.display = 'none';
        }
    });
}

// ═══════════════════════════════════════════════════════════
//  RENDER RESULTS
// ═══════════════════════════════════════════════════════════
function renderResults(data) {
    // Original vs Corrected
    document.getElementById('result-original').textContent = data.original_text;
    document.getElementById('result-corrected').textContent = data.corrected_text;

    // Sentiment
    const sentCard = document.getElementById('result-sentiment-card');
    const sentEmoji = document.getElementById('sentiment-emoji');
    const sentValue = document.getElementById('sentiment-value');

    sentCard.className = 'result-card result-sentiment';

    if (data.sentiment === 'Positive') {
        sentCard.classList.add('positive');
        sentEmoji.textContent = '🟢';
        sentValue.textContent = 'Highly Positive';
    } else if (data.sentiment === 'Negative') {
        sentCard.classList.add('negative');
        sentEmoji.textContent = '🔴';
        sentValue.textContent = 'Strongly Negative';
    } else {
        sentCard.classList.add('neutral');
        sentEmoji.textContent = '⚪';
        sentValue.textContent = 'Objectively Neutral';
    }

    // Summary
    document.getElementById('result-summary').textContent = data.summary;

    // Predictions
    const [cw1, cw2] = data.context_words;
    document.getElementById('prediction-context').textContent =
        `Context: ("${cw1}", "${cw2}") → what comes next?`;

    const predList = document.getElementById('predictions-list');
    predList.innerHTML = '';

    if (data.predictions && data.predictions.length > 0) {
        const maxProb = data.predictions[0].probability;
        data.predictions.forEach((pred, idx) => {
            const pctWidth = Math.max(8, (pred.probability / maxProb) * 100);
            const item = document.createElement('div');
            item.className = 'prediction-item';
            item.innerHTML = `
                <span class="prediction-rank ${idx === 0 ? 'top' : ''}">${idx === 0 ? '🔥' : idx + 1}</span>
                <span class="prediction-word">${escapeHtml(pred.word)}</span>
                <div class="prediction-bar-wrap">
                    <div class="prediction-bar" style="width: 0%;">${pred.probability.toFixed(4)}</div>
                </div>
            `;
            predList.appendChild(item);

            // Animate bar width
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    item.querySelector('.prediction-bar').style.width = pctWidth + '%';
                });
            });
        });
    }

    // Perplexity
    document.getElementById('perplexity-value').textContent = data.perplexity.toFixed(2);

    // Show results
    resultsArea.style.display = 'block';

    // Scroll to results
    setTimeout(() => {
        resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
}

// ═══════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Smooth scroll for all anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', (e) => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const offset = 80; // navbar height
                const pos = target.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top: pos, behavior: 'smooth' });
            }
        });
    });
}

// ═══════════════════════════════════════════════════════════
//  MOVIE SEARCH LOGIC
// ═══════════════════════════════════════════════════════════
function initMovieSearch() {
    // Load saved TMDB key
    const savedTmdbKey = localStorage.getItem('tmdb_api_key');
    if (savedTmdbKey) tmdbKeyInput.value = savedTmdbKey;

    btnSearchMovie.addEventListener('click', async () => {
        const query = movieQueryInput.value.trim();
        const apiKey = tmdbKeyInput.value.trim();
        
        if (!query) return;
        
        // Save key for next time
        if (apiKey) localStorage.setItem('tmdb_api_key', apiKey);
        
        btnSearchMovie.classList.add('loading');
        searchBtnText.style.display = 'none';
        searchBtnLoader.style.display = 'inline-block';
        
        try {
            const resp = await fetch(`${API_BASE}/api/movie/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, api_key: apiKey })
            });
            const data = await resp.json();
            
            if (data.Error) throw new Error(data.Error);
            
            renderMovieSearchResults(data.Search || []);
        } catch (err) {
            alert(`Search Error: ${err.message}`);
        } finally {
            btnSearchMovie.classList.remove('loading');
            searchBtnText.style.display = 'inline-block';
            searchBtnLoader.style.display = 'none';
        }
    });

    movieQueryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') btnSearchMovie.click();
    });
}

function renderMovieSearchResults(results) {
    movieResultsWrap.innerHTML = '';
    movieDetailWrap.style.display = 'none';
    
    if (results.length === 0) {
        movieResultsWrap.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No movies found.</p>';
        movieResultsWrap.style.display = 'grid';
        return;
    }
    
    results.forEach(movie => {
        const item = document.createElement('div');
        item.className = 'movie-result-item';
        item.innerHTML = `
            <img src="${movie.Poster !== 'N/A' ? movie.Poster : 'https://via.placeholder.com/300x450?text=No+Poster'}" class="movie-result-poster">
            <div class="movie-result-info">
                <div class="movie-result-title">${movie.Title}</div>
                <div class="movie-result-year">${movie.Year}</div>
            </div>
        `;
        item.addEventListener('click', () => fetchMovieDetails(movie.imdbID));
        movieResultsWrap.appendChild(item);
    });
    
    movieResultsWrap.style.display = 'grid';
    movieResultsWrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function fetchMovieDetails(movieId) {
    const apiKey = tmdbKeyInput.value.trim();
    
    try {
        const resp = await fetch(`${API_BASE}/api/movie/details`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ movie_id: movieId, api_key: apiKey })
        });
        const movie = await resp.json();
        
        if (movie.Error) throw new Error(movie.Error);
        
        // Populate detail card
        document.getElementById('movie-detail-title').textContent = movie.Title;
        document.getElementById('movie-detail-year').textContent = movie.Year;
        document.getElementById('movie-detail-rating').textContent = movie.imdbRating || 'N/A';
        document.getElementById('movie-detail-genre').textContent = movie.Genre;
        document.getElementById('movie-detail-plot').textContent = movie.Plot;
        document.getElementById('movie-detail-poster').src = movie.Poster !== 'N/A' ? movie.Poster : 'https://via.placeholder.com/300x450?text=No+Poster';
        
        movieDetailWrap.style.display = 'block';
        movieDetailWrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Setup analyze button
        btnAnalyzePlot.onclick = () => {
            pipelineInput.value = movie.Plot;
            pipelineInput.dispatchEvent(new Event('input'));
            document.getElementById('pipeline').scrollIntoView({ behavior: 'smooth' });
            btnRun.click();
        };
        
    } catch (err) {
        alert(`Error fetching details: ${err.message}`);
    }
}

// ═══════════════════════════════════════════════════════════
//  STANDALONE SUMMARIZER
// ═══════════════════════════════════════════════════════════
const SUMMARIZER_DEMO = `The film "Inception" directed by Christopher Nolan explores the concept of shared dreaming, where a skilled thief named Dom Cobb specializes in extracting secrets from people's subconscious during the dream state. Cobb is offered a chance to have his criminal history erased if he can accomplish the seemingly impossible task of "inception" — planting an idea deep within a target's subconscious. The film takes audiences through multiple layers of dreams, each with its own rules about time dilation and physics. The visual effects are groundbreaking, and the story weaves together themes of grief, memory, and the nature of reality. Hans Zimmer's iconic score adds emotional depth to the already complex narrative. The ensemble cast including Leonardo DiCaprio, Joseph Gordon-Levitt, and Ellen Page deliver powerful performances. The movie's ambiguous ending, with the spinning top, has become one of cinema's most debated conclusions, leaving audiences questioning what is real and what is a dream.`;

function initSummarizer() {
    const summarizerInput = document.getElementById('summarizer-input');
    const btnSummarize = document.getElementById('btn-summarize');
    const btnSummarizerDemo = document.getElementById('btn-summarizer-demo');
    const btnSummarizerClear = document.getElementById('btn-summarizer-clear');
    const summarizerOutput = document.getElementById('summarizer-output');
    const btnSummarizeDefault = document.querySelector('.btn-summarize-default');
    const btnSummarizeLoading = document.querySelector('.btn-summarize-loading');
    const btnCopyStandaloneSummary = document.getElementById('btn-copy-standalone-summary');

    // Demo button
    btnSummarizerDemo.addEventListener('click', () => {
        summarizerInput.value = SUMMARIZER_DEMO;
        btnSummarizerDemo.style.background = 'rgba(90, 228, 167, 0.15)';
        setTimeout(() => { btnSummarizerDemo.style.background = ''; }, 400);
    });

    // Clear button
    btnSummarizerClear.addEventListener('click', () => {
        summarizerInput.value = '';
        summarizerOutput.style.display = 'none';
    });

    // Run summarization
    btnSummarize.addEventListener('click', async () => {
        const text = summarizerInput.value.trim();
        if (!text) {
            summarizerInput.style.outline = '2px solid #e85d75';
            setTimeout(() => { summarizerInput.style.outline = ''; }, 2000);
            return;
        }

        if (text.length < 50) {
            alert('Please provide at least 50 characters for meaningful summarization.');
            return;
        }

        // Lock UI
        btnSummarize.disabled = true;
        btnSummarizeDefault.style.display = 'none';
        btnSummarizeLoading.style.display = 'flex';
        summarizerOutput.style.display = 'none';

        try {
            const resp = await fetch(`${API_BASE}/api/summarize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || 'Summarization failed');
            }

            const data = await resp.json();

            // Populate stats
            document.getElementById('stat-original-words').textContent = data.original_length;
            document.getElementById('stat-summary-words').textContent = data.summary_length;
            document.getElementById('stat-compression').textContent = data.compression_ratio;

            // Populate summary
            document.getElementById('standalone-summary-text').textContent = data.summary;

            // Show output
            summarizerOutput.style.display = 'block';
            summarizerOutput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            alert(`Summarization Error: ${error.message}`);
        } finally {
            btnSummarize.disabled = false;
            btnSummarizeDefault.style.display = 'flex';
            btnSummarizeLoading.style.display = 'none';
        }
    });

    // Copy standalone summary
    btnCopyStandaloneSummary.addEventListener('click', () => {
        const text = document.getElementById('standalone-summary-text').textContent;
        if (text === '—') return;
        navigator.clipboard.writeText(text).then(() => {
            const original = btnCopyStandaloneSummary.textContent;
            btnCopyStandaloneSummary.textContent = '✔️';
            setTimeout(() => { btnCopyStandaloneSummary.textContent = original; }, 1000);
        });
    });
}

function initUtilityActions() {
    btnCopySummary.onclick = () => {
        const summary = document.getElementById('result-summary').textContent;
        if (summary === '—') return;
        
        navigator.clipboard.writeText(summary).then(() => {
            const originalIcon = btnCopySummary.textContent;
            btnCopySummary.textContent = '✔️';
            setTimeout(() => {
                btnCopySummary.textContent = originalIcon;
            }, 1000);
        });
    };

    // Text-to-Speech button
    const btnSpeakSummary = document.getElementById('btn-speak-summary');
    let currentUtterance = null;

    if (btnSpeakSummary) {
        btnSpeakSummary.addEventListener('click', () => {
            const summary = document.getElementById('result-summary').textContent;
            if (summary === '—') return;

            // If already speaking, stop
            if (currentUtterance && window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                btnSpeakSummary.textContent = '🔊';
                return;
            }

            // Speak
            currentUtterance = new SpeechSynthesisUtterance(summary);
            currentUtterance.rate = 1;
            currentUtterance.pitch = 1;
            currentUtterance.volume = 1;

            currentUtterance.onstart = () => {
                btnSpeakSummary.textContent = '⏸️';
            };

            currentUtterance.onend = () => {
                btnSpeakSummary.textContent = '🔊';
            };

            window.speechSynthesis.speak(currentUtterance);
        });
    }
}

// ═══════════════════════════════════════════════════════════
//  VOICE RECORDER
// ═══════════════════════════════════════════════════════════
let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let timerInterval = null;

function initVoiceRecorder() {
    // Load saved Groq key
    const groqKeyInput = document.getElementById('groq-api-key');
    const savedGroqKey = localStorage.getItem('groq_api_key');
    if (savedGroqKey && groqKeyInput) groqKeyInput.value = savedGroqKey;

    // Open recorder modal
    btnMic.addEventListener('click', () => {
        voiceRecorderModal.style.display = 'flex';
        audioChunks = [];
        resetRecorderUI();
    });

    // Close modal
    voiceRecorderClose.addEventListener('click', () => {
        closeRecorderModal();
    });

    voiceRecorderBackdrop.addEventListener('click', () => {
        closeRecorderModal();
    });

    voiceRecorderCancel.addEventListener('click', () => {
        closeRecorderModal();
    });

    // Start recording
    btnStartRecording.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };

            mediaRecorder.onstart = () => {
                recordingStartTime = Date.now();
                btnStartRecording.style.display = 'none';
                btnStopRecording.style.display = 'block';
                voiceStatus.classList.add('recording');
                voiceStatus.querySelector('.status-text').textContent = 'Recording in progress...';
                voiceTimer.style.display = 'block';
                voiceRecorderModal.classList.add('recording');
                startTimer();
            };

            mediaRecorder.start();
        } catch (err) {
            alert(`Microphone Error: ${err.message}\n\nPlease allow microphone access and try again.`);
        }
    });

    // Stop recording
    btnStopRecording.addEventListener('click', () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            mediaRecorder.onstop = () => {
                btnStartRecording.style.display = 'block';
                btnStopRecording.style.display = 'none';
                btnUseRecording.style.display = 'block';
                voiceStatus.classList.remove('recording');
                voiceStatus.querySelector('.status-text').textContent = 'Recording saved ✓';
                voiceTimer.style.display = 'none';
                voiceRecorderModal.classList.remove('recording');
                stopTimer();
                
                // Stop all audio tracks
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            };
        }
    });

    // Use recording
    btnUseRecording.addEventListener('click', async () => {
        if (audioChunks.length === 0) return;

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        
        // Add Groq API Key from frontend
        const groqKeyInput = document.getElementById('groq-api-key');
        const groqKey = groqKeyInput.value.trim();
        if (groqKey) {
            formData.append('groq_api_key', groqKey);
            localStorage.setItem('groq_api_key', groqKey);
        }

        // Show processing state
        btnUseRecording.disabled = true;
        btnUseRecording.textContent = '⏳ Transcribing...';
        voiceStatus.querySelector('.status-text').textContent = 'Transcribing audio...';

        try {
            const resp = await fetch(`${API_BASE}/api/transcribe`, {
                method: 'POST',
                body: formData
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || 'Transcription failed');
            }

            const data = await resp.json();

            if (data.text) {
                // Insert transcribed text into input
                pipelineInput.value = data.text;
                pipelineInput.dispatchEvent(new Event('input'));

                // Close modal
                closeRecorderModal();

                // Scroll to input
                setTimeout(() => {
                    pipelineInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
            } else {
                throw new Error('No text returned from transcription');
            }
        } catch (err) {
            alert(`Transcription Error: ${err.message}`);
        } finally {
            btnUseRecording.disabled = false;
            btnUseRecording.textContent = '✓ Use Recording';
        }
    });
}

function closeRecorderModal() {
    voiceRecorderModal.style.display = 'none';
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    stopTimer();
    audioChunks = [];
}

function resetRecorderUI() {
    btnStartRecording.style.display = 'block';
    btnStopRecording.style.display = 'none';
    btnUseRecording.style.display = 'none';
    voiceStatus.classList.remove('recording');
    voiceStatus.querySelector('.status-text').textContent = 'Ready to record';
    voiceTimer.style.display = 'none';
    voiceTimer.querySelector('.timer-value').textContent = '0:00';
    stopTimer();
}

function startTimer() {
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        voiceTimer.querySelector('.timer-value').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }, 100);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// ═══════════════════════════════════════════════════════════
//  INITIALIZE
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    initNavbar();
    initFAQ();
    initInputActions();
    initLiveSentiment();
    initPipeline();
    initSummarizer();
    initMovieSearch();
    initUtilityActions();
    initVoiceRecorder();
    initSmoothScroll();
});
