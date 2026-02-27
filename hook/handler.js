const axios = require('axios');

const MEMORY_API = 'http://localhost:3000/api';

module.exports = {
  async onMessageReceived(event, context) {
    context.log('[Observational Memory] Message received:', {
      from: event.context?.from,
      channelId: event.context?.channelId,
      contentLength: event.context?.content?.length,
      sessionKey: event.sessionKey
    });
    
    try {
      const content = event.context?.content || event.message || '';
      const conversationId = event.context?.conversationId || event.sessionKey || 'unknown';
      
      if (!content) {
        context.log('[Observational Memory] WARN - No content to record');
        return;
      }
      
      await axios.post(`${MEMORY_API}/sessions`, {
        session_id: conversationId,
        messages: [{
          role: 'user',
          content: content,
          timestamp: new Date(event.context?.timestamp || Date.now()).toISOString()
        }]
      }, { timeout: 5000 });
      
      context.log('[Observational Memory] OK - Recorded user message');
      
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        context.log('[Observational Memory] WARN - Service not running');
      } else {
        context.log('[Observational Memory] ERROR -', error.message);
      }
    }
  },
  
  async onMessageSent(event, context) {
    context.log('[Observational Memory] Message sent:', {
      to: event.context?.to,
      channelId: event.context?.channelId,
      success: event.context?.success,
      sessionKey: event.sessionKey
    });
    
    // 只记录成功发送的消息
    if (event.context?.success === false) {
      context.log('[Observational Memory] SKIP - Message send failed');
      return;
    }
    
    try {
      const content = event.context?.content || event.message || '';
      const conversationId = event.context?.conversationId || event.sessionKey || 'unknown';
      
      if (!content) {
        context.log('[Observational Memory] WARN - No content to record');
        return;
      }
      
      await axios.post(`${MEMORY_API}/sessions`, {
        session_id: conversationId,
        messages: [{
          role: 'assistant',
          content: content,
          timestamp: new Date().toISOString()
        }]
      }, { timeout: 5000 });
      
      context.log('[Observational Memory] OK - Recorded assistant message');
      
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        context.log('[Observational Memory] WARN - Service not running');
      } else {
        context.log('[Observational Memory] ERROR -', error.message);
      }
    }
  }
};
