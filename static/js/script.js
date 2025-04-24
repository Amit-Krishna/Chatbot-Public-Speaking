document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('main-sidebar-toggle'); // Target the button in the header

    // --- Sidebar Toggle Logic ---
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed'); // Toggle class directly on sidebar

            // Change icon based on state
            const icon = sidebarToggleBtn.querySelector('i');
            if (icon) {
                // Check if currently collapsed *after* toggle
                if (sidebar.classList.contains('collapsed')) {
                    icon.classList.remove('fa-times'); // Change to open icon
                    icon.classList.add('fa-bars');
                } else {
                    icon.classList.remove('fa-bars'); // Change to close icon
                    icon.classList.add('fa-times');
                }
            }
        });

        // Set initial icon state based on sidebar visibility state
        // Note: Initial *visibility* state is now mainly controlled by CSS media queries
        // But we need the icon to match the initial state.
        const setInitialIcon = () => {
             const icon = sidebarToggleBtn.querySelector('i');
             if (icon) {
                 if (sidebar.classList.contains('collapsed')) {
                      icon.classList.remove('fa-times');
                      icon.classList.add('fa-bars');
                 } else {
                      icon.classList.remove('fa-bars');
                      icon.classList.add('fa-times');
                 }
             }
        }
        // Run on load (after CSS has potentially set initial collapsed state via media query)
         setTimeout(setInitialIcon, 0); // Timeout ensures CSS is applied

    } else {
        console.warn("Sidebar (#sidebar) or Main Sidebar Toggle Button (#main-sidebar-toggle) not found.");
    }


    // --- Function to render Markdown (Keep the robust version) ---
    function renderBasicMarkdown(markdownText) {
        if (typeof markdownText !== 'string') return '';
        let html = markdownText;
        // Code blocks (```lang\n code ```)
        html = html.replace(/```(\w*\n)?([\s\S]*?)```/g, (match, lang, code) => {
            const languageClass = lang ? `language-${lang.trim()}` : '';
            const escapedCode = code.replace(/</g, '<').replace(/>/g, '>');
            return `<pre><code class="${languageClass}">${escapedCode.trim()}</code></pre>`;
        });
        // Bold (**text** or __text__)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');
        // Italic (*text* or _text_)
        html = html.replace(/(?<!\*)\*(?!\*|\s)(.*?)(?<!\s)\*(?!\*)/g, '<em>$1</em>');
        html = html.replace(/_(.*?)_/g, '<em>$1</em>');
        // Inline code (`code`)
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Lists (unordered *, -, +)
        html = html.replace(/^\s*[*+-]\s+(.*)/gm, '<li>$1</li>');
        // Lists (ordered 1., 2.)
        html = html.replace(/^\s*\d+\.\s+(.*)/gm, '<li data-ordered="true">$1</li>'); // Mark ordered items

        // Wrap consecutive list items
        html = html.replace(/^(<(li.*?)>.*?<\/\2>\s*)+/gm, (match) => {
            // Check if the first item was marked as ordered
            if (match.includes('data-ordered="true"')) {
                 // Remove the temporary attribute before wrapping
                 match = match.replace(/ data-ordered="true"/g, '');
                return `<ol>${match.trim()}</ol>`;
            } else {
                return `<ul>${match.trim()}</ul>`;
            }
        });

        // Paragraphs (split by double+ newlines, wrap non-empty lines/blocks)
        html = html.split(/\n\s*\n/).map(part => {
            part = part.trim();
            if (!part) return '';
            if (part.match(/^<(ul|ol|pre|h[1-6]|li)/)) return part; // Avoid wrapping blocks/list items
            return `<p>${part.replace(/\n/g, '<br>')}</p>`; // Add <br> inside <p>
        }).join('');
        // Cleanup potential bad nesting after paragraph split
        html = html.replace(/<\/p>\s*<(ul|ol)>/g, '</p><$1>');
        html = html.replace(/<\/(ul|ol)>\s*<p>/g, '</$1><p>');
        html = html.replace(/<p>\s*<(ul|ol)/g, '<$1'); // Remove P wrapping list start
        html = html.replace(/<\/(ul|ol)>\s*<\/p>/g, '</$1>'); // Remove P wrapping list end
        html = html.replace(/<p><\/p>/g, ''); // Remove empty paragraphs

        return html;
    }


    // Function to add a message to the chat box (Keep the version with avatars)
    function displayMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        const avatar = document.createElement('div');
        avatar.classList.add('avatar', `${sender}-avatar`);
        avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        if (sender === 'bot') {
            contentDiv.innerHTML = renderBasicMarkdown(message);
        } else {
            const paragraph = document.createElement('p');
            paragraph.textContent = message;
            contentDiv.appendChild(paragraph);
        }
        if(sender === 'user') { messageElement.appendChild(contentDiv); messageElement.appendChild(avatar); }
        else { messageElement.appendChild(avatar); messageElement.appendChild(contentDiv); }
        chatBox.appendChild(messageElement);
        setTimeout(() => { chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' }); }, 50);
    }

     // Auto-resize textarea height (Keep as is)
     function autoResizeTextarea() {
         userInput.style.height = 'auto';
        let scrollHeight = userInput.scrollHeight;
        userInput.style.height = `${scrollHeight}px`;
     }
     userInput.addEventListener('input', autoResizeTextarea);
     userInput.addEventListener('input', () => { sendButton.disabled = userInput.value.trim() === ''; });


    // Function to handle sending a message (Keep as is)
    async function sendMessage() {
         const messageText = userInput.value.trim();
        if (messageText === '') return;
        displayMessage(messageText, 'user');
        userInput.value = '';
        autoResizeTextarea();
        sendButton.disabled = true; // Disable on send
        loadingIndicator.style.display = 'flex';
        userInput.disabled = true;
        try {
            const response = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json',}, body: JSON.stringify({ message: messageText }), });
            const data = await response.json();
            if (!response.ok) { console.error(`HTTP Error ${response.status}: ${data.response || 'Unknown server error'}`); displayMessage(`Error: ${data.response || 'Could not reach the server.'}`, 'bot');
            } else { displayMessage(data.response, 'bot'); }
        } catch (error) { console.error('Error sending message:', error); displayMessage('Sorry, I encountered a connection problem. Please try again.', 'bot');
        } finally {
            sendButton.disabled = userInput.value.trim() === '';
            loadingIndicator.style.display = 'none';
            userInput.disabled = false;
            userInput.focus();
        }
    }

    // Event listeners (Keep as is)
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(); } });
    userInput.focus();

    // Initial render for the first bot message (Keep as is)
    const initialBotMessageDiv = chatBox.querySelector('.bot-message .message-content');
    if (initialBotMessageDiv) {
         const initialContent = initialBotMessageDiv.innerHTML;
         initialBotMessageDiv.innerHTML = renderBasicMarkdown(initialContent.replace(/<p>|<\/p>/g, '').trim()); // Trim whitespace too
    }

     autoResizeTextarea(); // Initial check
     sendButton.disabled = userInput.value.trim() === ''; // Initial check

});