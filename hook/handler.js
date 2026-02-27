const axios = require('axios');

const MEMORY_API = 'http://localhost:3000/api';

const handler = async (event) => {
  console.log('[Observational Memory] Event received:', JSON.stringify({
    type: event.type,
    action: event.action,
    sessionKey: event.sessionKey,
    context: event.context
  }, null, 2));
  
  // 只处理消息事件
  if (event.type !== 'message') {
    console.log('[Observational Memory] SKIP - Not a message event');
    return;
  }
  
  const isReceived = event.action === 'received';
  const isSent = event.action === 'sent';
  
  if (!isReceived && !isSent) {
    console.log('[Observational Memory] SKIP - Unknown action:', event.action);
    return;
  }
  
  try {
    // 尝试多种方式获取内容
    const content = event.context?.content || 
                   event.context?.message || 
                   event.context?.text || 
                   event.message || 
                   '';
    
    // 尝试多种方式获取会话 ID
    const conversationId = event.context?.conversationId || 
                          event.context?.sessionKey ||
                          event.sessionKey || 
                          'unknown';
    
    if (!content) {
      console.log('[Observational Memory] WARN - No content found in event');
      return;
    }
    
    // 对于 sent 消息，检查是否成功
    if (isSent && event.context?.success === false) {
      console.log('[Observational Memory] SKIP - Send failed');
      return;
    }
    
    console.log('[Observational Memory] Sending to API:', {
      session_id: conversationId,
      role: isReceived ? 'user' : 'assistant',
      contentLength: content.length
    });
    
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
      console.log('[Observational Memory] ERROR Stack:', error.stack);
    }
  }
};

module.exports = handler;
