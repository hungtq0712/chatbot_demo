// API base URL - thay đổi theo URL của bạn
const API_BASE_URL = "http://127.0.0.1:8000"; // hoặc "http://localhost:8000"


// Biến toàn cục
let currentChatId = -1;
let currentMessages = [];

// DOM Elements
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');
const chatStatus = document.getElementById('chat-status');
const messageCount = document.getElementById('message-count');
const newChatBtn = document.getElementById('new-chat-btn');
const historyList = document.getElementById('history-list');

// Khởi tạo
async function init() {
    loadCurrentChat();
    loadChatHistory();

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    newChatBtn.addEventListener('click', createNewChat);

    // Kiểm tra kết nối backend
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            chatStatus.textContent = 'Kết nối OK';
            chatStatus.style.color = '#28a745';
        }
    } catch (error) {
        chatStatus.textContent = 'Mất kết nối backend';
        chatStatus.style.color = '#dc3545';
        console.error('Backend connection error:', error);
    }
}

// Gửi tin nhắn
async function sendMessage() {
    console.log("[sendMessage] currentChatId BEFORE:", currentChatId);
    const text = messageInput.value.trim();
    if (!text) return;

    // Hiển thị tin nhắn người dùng
    addMessage('user', text);
    messageInput.value = '';

    try {
        // Gửi đến backend
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentChatId,
                message: text
            })
        });

        if (!response.ok) {
            throw new Error('Lỗi phản hồi từ server');
        }

        const data = await response.json();

        // Hiển thị phản hồi từ bot
        addMessage('bot', data.reply);

        // Cập nhật currentChatId nếu có
        if (data.session_id) {
            currentChatId = data.session_id;
        }
        console.log("[sendMessage] currentChatId after:", currentChatId);
        updateMessageCount();
        loadChatHistory();

    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('bot', 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.');
    }
}

// Thêm tin nhắn vào giao diện
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Lưu tin nhắn vào mảng hiện tại
    currentMessages.push({ sender, text, timestamp: new Date().toISOString() });
    loadChatHistory();
}

// Tạo chat mới
async function createNewChat() {

    currentChatId = null;
    currentMessages = [];
    chatMessages.innerHTML = '';
    addMessage('bot', '👋 Chào mừng đến với cuộc trò chuyện mới!');
    updateMessageCount();
    chatStatus.textContent = 'Chat mới';
}



// Tải lịch sử chat
async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions`);

        if (!response.ok) {
            throw new Error('Lỗi khi tải lịch sử');
        }

        const history = await response.json();
        if (history.length === 0) {
            historyList.innerHTML = '<div class="no-history">Chưa có lịch sử</div>';
            return;
        }

        let historyHTML = '';
        history.forEach(chat => {
            const date = new Date(chat.created_at).toLocaleDateString('vi-VN');
            const firstMsg = (chat.messages && chat.messages.length > 0) ? chat.messages[0] : null;
            let preview = firstMsg?.content?.trim() || 'Không có preview';

            historyHTML += `
                <div class="history-item" onclick="loadChat('${chat.id}')">
                    <strong>${date}</strong><br>
                    <small>${preview}</small>
                </div>
            `;
        });

        historyList.innerHTML = historyHTML;

    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = '<div class="no-history">Lỗi tải lịch sử</div>';
    }
}

// Tải chat từ lịch sử
async function loadChat(chatId) {
    try {
        const response = await fetch(`${API_BASE_URL}/session/${chatId}`);

        if (!response.ok) {
            throw new Error('Lỗi khi tải chat');
        }

        const chat = await response.json();

        // Xóa chat hiện tại
        chatMessages.innerHTML = '';
        currentMessages = [];
        currentChatId = chat.id;

        // Hiển thị các tin nhắn
        chat.messages.forEach(msg => {
            addMessage(msg.role, msg.content);
        });

        updateMessageCount();
        chatStatus.textContent = 'Đang xem lịch sử';

    } catch (error) {
        console.error('Error loading chat:', error);
        alert('Lỗi khi tải chat!');
    }
}

// Tải chat hiện tại từ localStorage (tạm thời)
function loadCurrentChat() {
    const savedChat = localStorage.getItem('currentChat');
    if (savedChat) {
        const chat = JSON.parse(savedChat);
        currentChatId = chat.id;
        currentMessages = chat.messages;

        // Hiển thị tin nhắn
        chatMessages.innerHTML = '';
        currentMessages.forEach(msg => {
            addMessage(msg.sender, msg.text);
        });

        updateMessageCount();
    } else {
        // Chat mới
       // addMessage('bot', '👋 Xin chào! Hãy bắt đầu trò chuyện');
    }
}

// Cập nhật số tin nhắn
function updateMessageCount() {
    messageCount.textContent = `${currentMessages.length} tin nhắn`;
}

// Chạy khi trang tải xong
document.addEventListener('DOMContentLoaded', init);

// Export các hàm cần thiết cho việc gọi từ HTML
window.loadChat = loadChat;