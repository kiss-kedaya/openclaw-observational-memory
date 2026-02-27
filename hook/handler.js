const axios = require('axios');

const MEMORY_API = 'http://localhost:3000/api';

const handler = async (event) => {
  // 只处理消息事件
  if (event.type !== 'message') {
    return;
  }
  
  const isReceived = event.action === 'received';
  const isSent = event.action === 'sent';
  
  if (!isReceived && !isSent) {
    return;
  }
  
  console.log(`[Observational Memory] ${event.action}:`, {
    from: event.context?.from,
    to: event.context?.to,
    channelId: event.context?.channelId,
    sessionKey: event.sessionKey
  });
  
  try {
    const content = event.context?.content || '';
    const conversationId = event.context?.conversationId || event.sessionKey || 'unknown';
    
    if (!content) {
      console.log('[Observational Memory] WARN - No content');
      return;
    }
    
    // 发送消息失败时跳过
    if (isSent && event.context?.success === false) {
      console.log('[Observational Memory] SKIP - Send failed');
      return;
    }
    
    await axios.post(`${MEMORY_API}/sessions`, {
      session_id: conversationId,
      messages: [{
        role: isReceived ? 'user' : 'assistant',
        content: content,
        timestamp: new Date(event.context?.timestamp || Date.now()).toISOString()
      }]
    }, { timeout: 5000 });
    
    console.log(`[Observational Memory] OK - Recorded ${isReceived ? 'user' : 'assistant'} message`);
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('[Observational Memory] WARN - Service not running');
    } else {
      console.log('[Observational Memory] ERROR -', error.message);
    }
  }
};

module.exports = handler;
